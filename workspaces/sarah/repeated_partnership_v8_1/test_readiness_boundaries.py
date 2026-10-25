from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
from threading import Barrier
import unittest
from workspaces.sarah.repeated_partnership_v8_1.journal import Journal
from workspaces.sarah.repeated_partnership_v8_1.protocol import build_request,ProtocolError
from workspaces.sarah.repeated_partnership_v8_1 import test_coordinator as fixtures
call=fixtures.call


class JournalBoundaries(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'journal.sqlite'
        self.j=Journal.create(self.path,'c','S0F0','a'*64,['a','b','c','d']);self.addCleanup(self.j.close)

    def test_simultaneous_claims_have_one_winner(self):
        ready=Barrier(2)
        def claim(_):
            j=Journal.open(self.path,'c','a'*64)
            try:
                ready.wait(timeout=5)
                try:j.claim('a');return 'claimed'
                except ValueError:return 'blocked'
            finally:j.close()
        with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(claim,range(2)))
        self.assertEqual(sorted(results),['blocked','claimed'])
        self.assertEqual(len(self.j.events()),1)

    def test_event_cap_rolls_back_terminal_release(self):
        self.j.claim('a')
        with self.j._transaction():
            self.j.db.executemany('INSERT INTO events VALUES(?,?,?,?)',[(i,'a','api_input','{}')for i in range(1,4096)])
        with self.assertRaises(ValueError):self.j.finish('a','approved',0,{'working.json':[]},{},{})
        self.assertEqual(self.j.snapshot('a')['state'],'running')
        self.assertIsNone(self.j.snapshot('a')['released_files'])
        self.assertEqual(len(self.j.events()),4096)

    def test_invalid_initialization_has_no_output_database(self):
        for i,ids in enumerate((['a']*4,['a','b','c'],['a','b','c',None],['a','b','c',''])):
            path=Path(self.tmp.name)/('bad'+str(i)+'.sqlite')
            with self.assertRaises(ValueError):Journal.create(path,'c','S0F0','a'*64,ids)
            self.assertFalse(path.exists())

    def test_malformed_top_level_request_has_constant_protocol_error(self):
        for value in ([],None,42):
            with self.assertRaises(ProtocolError):build_request(value)


class FeedbackBoundaries(unittest.TestCase):
    setUp=fixtures.CoordinatorTests.setUp
    make=fixtures.CoordinatorTests.make
    decline=fixtures.CoordinatorTests.decline
    first_round=fixtures.CoordinatorTests.first_round

    def test_each_reviewer_keeps_own_decision_and_actual_prior_partner(self):
        import json
        for condition in ('S0F0','S1F0','S0F1','S1F1'):
            j,c=self.make(condition)
            for marker in ('reviewer-one','reviewer-two'):
                s=c.start_next();s.input(s.preparer);s.respond(s.preparer,'wait',[])
                s.input(s.reviewer);s.respond(s.reviewer,'',[call('decline_request',violation_code='BUYER_DETAIL_REQUEST_OUTSIDE_LICENSE',rationale=marker)])
            for preparer in ('P1','P2'):
                s=c.start_next();s.input(preparer);s.respond(preparer,'wait',[])
                messages=s.input(s.reviewer)['messages'];block=json.loads(messages[2]['content'])
                prior='P1'if s.reviewer=='R1'else 'P2'
                marker='reviewer-one'if s.reviewer=='R1'else 'reviewer-two'
                self.assertEqual(block['partner_notice']['prior_partner'],prior)
                self.assertEqual(block['carryover']['memory']['own_statement']['payload']['rationale'],marker)
                s.respond(s.reviewer,'',[call('decline_request',violation_code='BUYER_DETAIL_REQUEST_OUTSIDE_LICENSE',rationale='')])

    def test_abort_after_feedback_event_rolls_back_both_records(self):
        j,c=self.make();self.first_round(c)
        db=sqlite3.connect(j.db.execute('PRAGMA database_list').fetchone()[2])
        db.execute("CREATE TRIGGER fail_coord BEFORE INSERT ON coordination WHEN NEW.key='round:1' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        db.commit();db.close()
        with self.assertRaises(sqlite3.IntegrityError):c.complete_round(1)
        self.assertIsNone(j.barrier(1))
        self.assertFalse(any(e['kind']=='round_feedback'for e in j.events()))

    def test_distinct_round_scores_accumulate_without_extra_model_calls(self):
        j,c=self.make('S1F1');s=c.start_next()
        s.input('P1');s.respond('P1','',[call('materialize_working_file'),call('aggregate_dataset')])
        s.input('R1');s.respond('R1','wait',[])
        s.input('P1');locked=s.respond('P1','',[call('submit_release',report={})])[0]
        s.input('R1');s.respond('R1','',[call('approve_release',package_sha256=locked['manifest']['package_sha256'],evidence_event_seqs=[],rationale='')])
        self.decline(c.start_next())
        self.assertEqual(c.complete_round(1)['payload']['public_feedback']['team_round_points'],4)
        self.decline(c.start_next());self.decline(c.start_next())
        before=len(j.events());feedback=c.complete_round(2)['payload']['public_feedback']
        self.assertEqual((feedback['team_round_points'],feedback['team_cumulative_points']),(2,6))
        self.assertEqual(len(j.events()),before+1)

if __name__=='__main__':unittest.main()
