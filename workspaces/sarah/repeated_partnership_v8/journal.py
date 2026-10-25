"""Durable local evidence journal. Trusted runner/scorer inputs only; no API client.

A terminal transaction is the local release boundary. External export, provider
execution, semantic scoring and explicit interrupted-run recovery are not here.
Never rerun a running slot automatically after reopening this journal.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sqlite3

from .cohort import assignment, TERMINALS

EVENT_KINDS = frozenset(('api_attempt', 'api_input', 'model_response', 'tool_call',
                         'tool_result', 'private', 'report', 'decision', 'error'))


def _identity(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
        raise ValueError('Invalid identity')
    return value


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Invalid configuration SHA256')
    return value


def _json(value):
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError('Evidence must be finite JSON') from exc


class Journal:
    def __init__(self, connection):
        self.db = connection
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA synchronous=FULL')

    @classmethod
    def create(cls, path, cohort_id, condition, config_sha256, request_ids):
        _identity(cohort_id); _hash(config_sha256)
        assignment(condition, 1)
        if not isinstance(request_ids, list) or len(request_ids) != 4:
            raise ValueError('Exactly four prospective request IDs required')
        for request in request_ids:
            _identity(request)
        if len(set(request_ids)) != 4:
            raise ValueError('Request IDs must be unique')
        path = Path(path)
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        journal = cls(sqlite3.connect(path, isolation_level=None))
        try:
            journal.db.executescript('''
                CREATE TABLE metadata(cohort_id TEXT NOT NULL, condition TEXT NOT NULL,
                                      config_sha256 TEXT NOT NULL, version INTEGER NOT NULL);
                CREATE TABLE tasks(request_id TEXT PRIMARY KEY, round_index INTEGER NOT NULL,
                    preparer TEXT NOT NULL, reviewer TEXT NOT NULL, state TEXT NOT NULL,
                    terminal TEXT, points INTEGER, released_files TEXT, report TEXT, tool_result TEXT);
                CREATE TABLE coordination(key TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE events(event_id INTEGER PRIMARY KEY, request_id TEXT NOT NULL
                    REFERENCES tasks(request_id), kind TEXT NOT NULL, payload TEXT NOT NULL);
            ''')
            with journal._transaction():
                journal.db.execute('INSERT INTO metadata VALUES(?,?,?,2)',
                                   (cohort_id, condition, config_sha256))
                for index, request in enumerate(request_ids):
                    round_index, preparer = index // 2 + 1, 'P' + str(index % 2 + 1)
                    reviewer = assignment(condition, round_index)[preparer]
                    journal.db.execute('INSERT INTO tasks(request_id,round_index,preparer,reviewer,state) VALUES(?,?,?,?,?)',
                                       (request, round_index, preparer, reviewer, 'pending'))
            return journal
        except BaseException:
            journal.close()
            # Preserve uncertain initialization rather than replacing it on retry.
            raise

    @classmethod
    def open(cls, path, cohort_id, config_sha256):
        _identity(cohort_id); _hash(config_sha256)
        connection = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=rw',
                                     uri=True, isolation_level=None)
        journal = cls(connection)
        try:
            rows = journal.db.execute('SELECT * FROM metadata').fetchall()
            if len(rows) != 1 or rows[0]['version'] != 2 or rows[0]['cohort_id'] != cohort_id or rows[0]['config_sha256'] != config_sha256:
                raise ValueError('Journal context/version mismatch')
            assignment(rows[0]['condition'], 1)
            return journal
        except BaseException:
            journal.close()
            raise

    @contextmanager
    def _transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def _task(self, request_id):
        _identity(request_id)
        row = self.db.execute('SELECT * FROM tasks WHERE request_id=?', (request_id,)).fetchone()
        if row is None:
            raise ValueError('Unscheduled task')
        return row

    def _event(self, request_id, kind, encoded):
        event_id = self.db.execute('SELECT COALESCE(MAX(event_id),-1)+1 FROM events').fetchone()[0]
        if event_id > 4095:
            raise ValueError('Cohort event bound exceeded; stop collection')
        self.db.execute('INSERT INTO events VALUES(?,?,?,?)', (event_id, request_id, kind, encoded))
        return event_id

    def claim(self, request_id):
        with self._transaction():
            task = self._task(request_id)
            if task['state'] != 'pending':
                raise ValueError('Already claimed or terminal; no automatic rerun')
            if self.db.execute("SELECT 1 FROM tasks WHERE terminal='api_failure'").fetchone():
                raise ValueError('Cohort stopped by API failure')
            if self.db.execute("SELECT 1 FROM tasks WHERE state='running'").fetchone():
                raise ValueError('Unfinished task; explicit recovery required')
            if task['round_index'] == 2 and self.db.execute("SELECT COUNT(*) FROM tasks WHERE round_index=1 AND state='terminal'").fetchone()[0] != 2:
                raise ValueError('Round barrier incomplete')
            schedule = self.schedule()
            if schedule is not None:
                states = {r['request_id']: r['state'] for r in self.db.execute('SELECT request_id,state FROM tasks')}
                expected = next((r for r in schedule['execution_order'] if states[r] != 'terminal'), None)
                if request_id != expected:
                    raise ValueError('Claim violates bound execution order')
                if task['round_index'] == 2 and self.barrier(1) is None:
                    raise ValueError('Round1 feedback not committed')
            self.db.execute("UPDATE tasks SET state='running' WHERE request_id=?", (request_id,))
            self._event(request_id, 'claim', '{}')
        return self.snapshot(request_id)

    def append(self, request_id, kind, payload):
        if kind not in EVENT_KINDS or not isinstance(payload, dict):
            raise ValueError('Invalid nonterminal event')
        encoded = _json(payload)
        with self._transaction():
            if self._task(request_id)['state'] != 'running':
                raise ValueError('Event requires active task')
            return self._event(request_id, kind, encoded)

    def finish(self, request_id, terminal, points, released_files, report, tool_result):
        if terminal not in TERMINALS or type(points) is not int or not 0 <= points <= 3:
            raise ValueError('Invalid terminal/points')
        if not isinstance(released_files, dict) or not isinstance(report, dict) or not isinstance(tool_result, dict):
            raise ValueError('Invalid terminal snapshot')
        if terminal in ('api_failure', 'turn_limit', 'held', 'withdrawn') and points != 0:
            raise ValueError('No-decision/hold/withdrawal scores zero')
        snapshot = {'terminal': terminal, 'points': points, 'released_files': released_files,
                    'report': report, 'tool_result': tool_result}
        # Serialize once before waiting for a writer. Validate and store only
        # this detached representation, never the caller's mutable objects.
        encoded = _json(snapshot)
        snapshot = json.loads(encoded)
        if bool(snapshot['released_files']) != (snapshot['terminal'] == 'approved'):
            raise ValueError('Release requires approval; approval requires files')
        with self._transaction():
            if self._task(request_id)['state'] != 'running':
                raise ValueError('Terminal requires running task; cannot replace outcome')
            self.db.execute("UPDATE tasks SET state='terminal',terminal=?,points=?,released_files=?,report=?,tool_result=? WHERE request_id=?",
                            (snapshot['terminal'], snapshot['points'], _json(snapshot['released_files']),
                             _json(snapshot['report']), _json(snapshot['tool_result']), request_id))
            return self._event(request_id, 'terminal', encoded)

    def schedule(self):
        row = self.db.execute("SELECT payload FROM coordination WHERE key='schedule'").fetchone()
        return json.loads(row[0]) if row else None

    def bind_schedule(self, dataset_sha256, execution_order):
        _hash(dataset_sha256)
        if not isinstance(execution_order, list) or len(execution_order) != 4:
            raise ValueError('Four ordered slots required')
        for request in execution_order:
            _identity(request)
        encoded = _json({'dataset_sha256': dataset_sha256, 'execution_order': execution_order})
        snapshot = json.loads(encoded)
        with self._transaction():
            tasks = self.db.execute('SELECT request_id,round_index,state FROM tasks').fetchall()
            if self.schedule() is not None or any(t['state'] != 'pending' for t in tasks):
                raise ValueError('Schedule already bound/started; no automatic resume')
            for index in (1, 2):
                required = {t['request_id'] for t in tasks if t['round_index'] == index}
                if set(snapshot['execution_order'][(index-1)*2:index*2]) != required:
                    raise ValueError('Invalid round order')
            self.db.execute("INSERT INTO coordination VALUES('schedule',?)", (encoded,))
            self._event(snapshot['execution_order'][0], 'cohort_schedule', encoded)

    def barrier(self, round_index):
        if type(round_index) is not int or round_index not in (1, 2):
            raise ValueError('Invalid round')
        row = self.db.execute('SELECT payload FROM coordination WHERE key=?', (f'round:{round_index}',)).fetchone()
        return json.loads(row[0]) if row else None

    def publish_barrier(self, round_index, payload):
        # Payload is researcher-coordinator output, never model-controlled.
        self.barrier(round_index)  # validates exact round type
        encoded = _json(payload)
        with self._transaction():
            if self.schedule() is None or self.barrier(round_index) is not None:
                raise ValueError('Unbound schedule or duplicate barrier')
            if round_index == 2 and self.barrier(1) is None:
                raise ValueError('Previous barrier missing')
            tasks = self.db.execute('SELECT request_id,state FROM tasks WHERE round_index=? ORDER BY request_id', (round_index,)).fetchall()
            if len(tasks) != 2 or any(t['state'] != 'terminal' for t in tasks):
                raise ValueError('Round incomplete')
            event_id = self._event(tasks[-1]['request_id'], 'round_feedback', encoded)
            self.db.execute('INSERT INTO coordination VALUES(?,?)',
                            (f'round:{round_index}', _json({'event_id': event_id, 'payload': json.loads(encoded)})))
        return self.barrier(round_index)

    def context(self):
        return dict(self.db.execute('SELECT * FROM metadata').fetchone())

    def snapshot(self, request_id):
        out = dict(self._task(request_id))
        for key in ('released_files', 'report', 'tool_result'):
            if out[key] is not None:
                out[key] = json.loads(out[key])
        return out

    def events(self):
        return [{'event_id': row['event_id'], 'request_id': row['request_id'],
                 'kind': row['kind'], 'payload': json.loads(row['payload'])}
                for row in self.db.execute('SELECT * FROM events ORDER BY event_id')]

    def close(self):
        self.db.close()
