import json
from pathlib import Path
import tempfile
import unittest
from workspaces.sarah.repeated_partnership_v8_1.budget import BudgetLedger, BudgetStop, BoundedDispatcher
from workspaces.sarah.repeated_partnership_v8_1.protocol import build_request
from workspaces.sarah.repeated_partnership_v8_1.test_protocol import actor_input,response

RESERVE=108192000


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'budget.sqlite'
        self.b=BudgetLedger.create(self.path,cap_nusd=RESERVE*2,max_requests=2,approval_ref='OFFLINE_FIXTURE_ONLY')
        self.addCleanup(self.b.close)

    def test_reservation_exists_before_transport_and_known_usage_settles(self):
        def transport(body,timeout):
            self.assertEqual(self.b.summary()['committed_nusd'],RESERVE)
            self.assertEqual(timeout,90)
            self.assertEqual(json.loads(body)['model'],'gpt-5-mini-2025-08-07')
            return response(prompt=100,completion=20)
        parsed=BoundedDispatcher(self.b,transport).dispatch('call1',actor_input())
        self.assertEqual(parsed.content,'hello')
        self.assertEqual(self.b.summary()['committed_nusd'],100*250+20*2000)
        self.assertEqual(self.b.summary()['request_count'],1)

    def test_insufficient_cap_never_invokes_transport(self):
        small=BudgetLedger.create(Path(self.tmp.name)/'small.sqlite',cap_nusd=RESERVE-1,max_requests=1,approval_ref='OFFLINE_FIXTURE_ONLY')
        self.addCleanup(small.close)
        touched=[]
        with self.assertRaises(BudgetStop):BoundedDispatcher(small,lambda *a:touched.append(a)).dispatch('call',actor_input())
        self.assertEqual(touched,[]);self.assertEqual(small.summary()['request_count'],0)

    def test_pending_reopen_duplicate_and_request_cap_block_redispatch(self):
        prepared=build_request(actor_input())
        self.b.reserve('call1',prepared.sha256)
        other=BudgetLedger.open(self.path);self.addCleanup(other.close)
        with self.assertRaises(BudgetStop):other.reserve('call2',prepared.sha256)
        self.b.settle('call1',response(),10,2)
        with self.assertRaises(BudgetStop):other.reserve('call1',prepared.sha256)
        other.reserve('call2',prepared.sha256);other.settle('call2',response(),10,2)
        with self.assertRaises(BudgetStop):self.b.reserve('call3',prepared.sha256)
        self.assertEqual(self.b.summary()['request_count'],2)

    def test_timeout_or_malformed_response_keeps_full_reservation_and_stops(self):
        def timeout(*args):raise TimeoutError('secret-error-string')
        for name,transport in [('timeout',timeout),('malformed',lambda *a:{'invalid':True})]:
            b=BudgetLedger.create(Path(self.tmp.name)/(name+'.sqlite'),cap_nusd=RESERVE*3,max_requests=3,approval_ref='OFFLINE_FIXTURE_ONLY')
            self.addCleanup(b.close)
            with self.assertRaises(BudgetStop)as caught:BoundedDispatcher(b,transport).dispatch('call1',actor_input())
            self.assertNotIn('secret-error-string',str(caught.exception))
            self.assertEqual(b.summary()['committed_nusd'],RESERVE)
            self.assertTrue(b.summary()['stopped'])
            with self.assertRaises(BudgetStop):b.reserve('call2',build_request(actor_input()).sha256)

    def test_settlement_cannot_guess_missing_or_oversized_usage(self):
        self.b.reserve('call1',build_request(actor_input()).sha256)
        for prompt,completion in ((True,1),(1,4097),(-1,0),(400001,0)):
            with self.assertRaises(ValueError):self.b.settle('call1',response(),prompt,completion)
        self.assertEqual(self.b.summary()['committed_nusd'],RESERVE)

    def test_exclusive_creation_and_reopened_rates_are_pinned(self):
        with self.assertRaises(FileExistsError):BudgetLedger.create(self.path,cap_nusd=1,max_requests=1,approval_ref='OFFLINE_FIXTURE_ONLY')
        self.assertEqual(self.path.stat().st_mode &0o777,0o600)
        other=BudgetLedger.open(self.path);self.addCleanup(other.close)
        self.assertEqual(other.summary()['cap_nusd'],RESERVE*2)

    def test_malformed_response_is_durable_even_when_parser_rejects_it(self):
        raw={'model':'unexpected','choices':[],'extra':'original-evidence'}
        with self.assertRaises(BudgetStop):BoundedDispatcher(self.b,lambda *a:raw).dispatch('call1',actor_input())
        row=self.b.db.execute('SELECT raw_response FROM reservations WHERE call_id=?',('call1',)).fetchone()
        self.assertEqual(json.loads(row[0]),raw)
        self.assertEqual(self.b.summary()['committed_nusd'],RESERVE)

    def test_two_simultaneous_reservations_cannot_bypass_outstanding_hold(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier=Barrier(2)
        digest=build_request(actor_input()).sha256
        def reserve(call):
            ledger=BudgetLedger.open(self.path)
            try:
                barrier.wait(timeout=5)
                try:ledger.reserve(call,digest);return 'reserved'
                except BudgetStop:return 'blocked'
            finally:ledger.close()
        with ThreadPoolExecutor(max_workers=2)as pool:
            outcomes=list(pool.map(reserve,['left','right']))
        self.assertEqual(sorted(outcomes),['blocked','reserved'])
        self.assertEqual(self.b.summary()['request_count'],1)
        self.assertEqual(self.b.summary()['committed_nusd'],RESERVE)

    def test_accounting_failure_retains_pending_hold(self):
        import sqlite3
        self.b.reserve('call1',build_request(actor_input()).sha256)
        db=sqlite3.connect(self.path)
        db.execute("CREATE TRIGGER fail_settle BEFORE UPDATE ON reservations WHEN NEW.state='settled' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        db.commit();db.close()
        with self.assertRaises(sqlite3.IntegrityError):self.b.settle('call1',response(),10,2)
        self.assertEqual(self.b.summary()['committed_nusd'],RESERVE)
        with self.assertRaises(BudgetStop):self.b.reserve('call2',build_request(actor_input()).sha256)

if __name__=='__main__':unittest.main()
