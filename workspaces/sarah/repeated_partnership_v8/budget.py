"""Persistent conservative token-cost reservation; injected transport tests only.

No API client or CLI. Approval refs are provenance, not an authorization service.
Rates must be reverified and a real cap authorized before any future live driver.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sqlite3

from .protocol import MODEL, INPUT_RESERVE_TOKENS, OUTPUT_CAP, build_request, parse_response, canonical

INPUT_NUSD_PER_TOKEN=250
OUTPUT_NUSD_PER_TOKEN=2000
RESERVE_NUSD=INPUT_RESERVE_TOKENS*INPUT_NUSD_PER_TOKEN+OUTPUT_CAP*OUTPUT_NUSD_PER_TOKEN
PRICE_REFERENCE='https://developers.openai.com/api/docs/pricing#2026-10-25-standard'


class BudgetStop(RuntimeError):pass


def _positive(value):return type(value)is int and value>0


def _call_id(value):
    if not isinstance(value,str)or not re.fullmatch('[A-Za-z0-9_-]{1,128}',value):raise ValueError('Invalid call ID')


class BudgetLedger:
    def __init__(self,db):
        self.db=db;db.row_factory=sqlite3.Row;db.execute('PRAGMA synchronous=FULL')

    @classmethod
    def create(cls,path,*,cap_nusd,max_requests,approval_ref):
        if not _positive(cap_nusd)or not _positive(max_requests)or max_requests>1152:
            raise ValueError('Positive approved cap and bounded allocation required')
        if not isinstance(approval_ref,str)or not 0<len(approval_ref)<=256:raise ValueError('Approval provenance required')
        path=Path(path);fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        ledger=cls(sqlite3.connect(path,isolation_level=None))
        try:
            ledger.db.executescript('''
                CREATE TABLE metadata(version INTEGER, model TEXT,cap_nusd INTEGER,max_requests INTEGER,
                    approval_ref TEXT,price_reference TEXT,input_rate INTEGER,output_rate INTEGER,stopped INTEGER);
                CREATE TABLE reservations(call_id TEXT PRIMARY KEY,payload_sha256 TEXT NOT NULL,
                    state TEXT NOT NULL,committed_nusd INTEGER NOT NULL,prompt_tokens INTEGER,
                    completion_tokens INTEGER,raw_response TEXT,error_code TEXT);
            ''')
            with ledger._transaction():
                ledger.db.execute('INSERT INTO metadata VALUES(1,?,?,?,?,?,?,?,0)',
                                  (MODEL,cap_nusd,max_requests,approval_ref,PRICE_REFERENCE,INPUT_NUSD_PER_TOKEN,OUTPUT_NUSD_PER_TOKEN))
            return ledger
        except BaseException:
            ledger.close();raise

    @classmethod
    def open(cls,path):
        ledger=cls(sqlite3.connect(Path(path).resolve().as_uri()+'?mode=rw',uri=True,isolation_level=None))
        try:
            rows=ledger.db.execute('SELECT * FROM metadata').fetchall()
            if len(rows)!=1:raise ValueError('Budget metadata missing')
            m=rows[0]
            if m['version']!=1 or m['model']!=MODEL or m['input_rate']!=INPUT_NUSD_PER_TOKEN or m['output_rate']!=OUTPUT_NUSD_PER_TOKEN or m['price_reference']!=PRICE_REFERENCE:
                raise ValueError('Budget model/pricing/version mismatch')
            if not _positive(m['cap_nusd'])or not _positive(m['max_requests'])or m['max_requests']>1152:
                raise ValueError('Invalid budget limits')
            return ledger
        except BaseException:ledger.close();raise

    @contextmanager
    def _transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def summary(self):
        m=dict(self.db.execute('SELECT * FROM metadata').fetchone())
        totals=self.db.execute('SELECT COUNT(*),COALESCE(SUM(committed_nusd),0) FROM reservations').fetchone()
        return {'cap_nusd':m['cap_nusd'],'committed_nusd':totals[1],'request_count':totals[0],
                'max_requests':m['max_requests'],'stopped':bool(m['stopped'])}

    def reserve(self,call_id,payload_sha256):
        _call_id(call_id)
        if not isinstance(payload_sha256,str)or not re.fullmatch('[0-9a-f]{64}',payload_sha256):raise ValueError('Request digest required')
        with self._transaction():
            s=self.summary()
            if s['stopped']or self.db.execute("SELECT 1 FROM reservations WHERE state!='settled'").fetchone():
                raise BudgetStop('BUDGET_STOP_UNCERTAIN_OR_OUTSTANDING')
            if self.db.execute('SELECT 1 FROM reservations WHERE call_id=?',(call_id,)).fetchone():raise BudgetStop('DUPLICATE_CALL_NO_RETRY')
            if s['request_count']>=s['max_requests']or s['committed_nusd']+RESERVE_NUSD>s['cap_nusd']:
                raise BudgetStop('BUDGET_OR_ALLOCATION_EXHAUSTED')
            self.db.execute('INSERT INTO reservations(call_id,payload_sha256,state,committed_nusd) VALUES(?,?,?,?)',
                            (call_id,payload_sha256,'reserved',RESERVE_NUSD))

    def record_response(self,call_id,raw_response):
        """Persist even a structurally invalid finite response before parsing."""
        _call_id(call_id)
        encoded=canonical(raw_response).decode('utf-8')
        with self._transaction():
            row=self.db.execute('SELECT state,raw_response FROM reservations WHERE call_id=?',(call_id,)).fetchone()
            if row is None or row['state']!='reserved'or row['raw_response']is not None:
                raise ValueError('Response cannot replace existing evidence')
            self.db.execute('UPDATE reservations SET raw_response=? WHERE call_id=?',(encoded,call_id))
        return json.loads(encoded)

    def settle(self,call_id,raw_response,prompt_tokens,completion_tokens):
        _call_id(call_id)
        if type(prompt_tokens)is not int or type(completion_tokens)is not int:raise ValueError('Exact integer usage required')
        parsed=parse_response(raw_response)
        if prompt_tokens!=parsed.prompt_tokens or completion_tokens!=parsed.completion_tokens:
            raise ValueError('Usage must match preserved provider response')
        encoded=canonical(parsed.raw).decode('utf-8')
        amount=prompt_tokens*INPUT_NUSD_PER_TOKEN+completion_tokens*OUTPUT_NUSD_PER_TOKEN
        with self._transaction():
            row=self.db.execute('SELECT * FROM reservations WHERE call_id=?',(call_id,)).fetchone()
            if row is None or row['state']!='reserved':raise ValueError('No unsettled reservation')
            if amount>row['committed_nusd']:raise ValueError('Usage exceeds reserved envelope')
            if row['raw_response']is not None and row['raw_response']!=encoded:
                raise ValueError('Cannot settle against changed provider evidence')
            self.db.execute("UPDATE reservations SET state='settled',committed_nusd=?,prompt_tokens=?,completion_tokens=?,raw_response=? WHERE call_id=?",
                            (amount,prompt_tokens,completion_tokens,encoded,call_id))

    def uncertain(self,call_id,error_code):
        _call_id(call_id)
        if error_code not in ('TIMEOUT','TRANSPORT_ERROR','INVALID_RESPONSE','ACCOUNTING_ERROR','INTERRUPTED'):
            raise ValueError('Constant error code required')
        with self._transaction():
            row=self.db.execute('SELECT state FROM reservations WHERE call_id=?',(call_id,)).fetchone()
            if row is None or row['state']!='reserved':raise ValueError('No pending reservation')
            self.db.execute("UPDATE reservations SET state='uncertain',error_code=? WHERE call_id=?",(error_code,call_id))
            self.db.execute('UPDATE metadata SET stopped=1')

    def close(self):self.db.close()


class BoundedDispatcher:
    """Calls an injected transport once, only after durable worst-case reserve.

    No real transport is supplied here. Returned parsed actions are NOT applied
    to TaskAdapter: driver/protocol provenance and failure integration are next.
    """
    def __init__(self,ledger,transport):
        if not callable(transport):raise ValueError('Explicit transport required')
        self.ledger=ledger;self.transport=transport

    def dispatch(self,call_id,actor_input):
        request=build_request(actor_input)
        self.ledger.reserve(call_id,request.sha256)
        try:
            raw=self.transport(request.body,90)
        except BaseException as exc:
            code='TIMEOUT'if isinstance(exc,TimeoutError)else 'INTERRUPTED'if not isinstance(exc,Exception)else 'TRANSPORT_ERROR'
            self.ledger.uncertain(call_id,code)
            if not isinstance(exc,Exception):raise
            raise BudgetStop(code)from None
        try:
            preserved=self.ledger.record_response(call_id,raw)
            parsed=parse_response(preserved)
        except Exception:
            self.ledger.uncertain(call_id,'INVALID_RESPONSE')
            raise BudgetStop('INVALID_RESPONSE')from None
        try:
            self.ledger.settle(call_id,parsed.raw,parsed.prompt_tokens,parsed.completion_tokens)
        except Exception:
            self.ledger.uncertain(call_id,'ACCOUNTING_ERROR')
            raise BudgetStop('ACCOUNTING_ERROR')from None
        return parsed
