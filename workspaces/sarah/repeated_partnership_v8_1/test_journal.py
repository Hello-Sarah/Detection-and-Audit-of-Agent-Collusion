"""Real temporary SQLite transactions; no provider calls."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import tempfile
import unittest
from workspaces.sarah.repeated_partnership_v8_1.journal import Journal


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'cohort.sqlite'
        self.tasks = ['r1p1','r1p2','r2p1','r2p2']
        self.j = Journal.create(self.path, 'c1', 'S0F1', 'a'*64, self.tasks)
        self.addCleanup(self.j.close)

    def reopen(self):
        j = Journal.open(self.path, 'c1', 'a'*64)
        self.addCleanup(j.close)
        return j

    def finish(self, task, terminal='rejected', points=1, files=None):
        return self.j.finish(task, terminal, points, files or {}, {'free_text':'report'}, {'ok':True})

    def test_exclusive_create_and_pinned_context(self):
        before = self.path.read_bytes()
        with self.assertRaises(FileExistsError):
            Journal.create(self.path,'c1','S0F1','a'*64,self.tasks)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(ValueError): Journal.open(self.path,'other','a'*64)
        with self.assertRaises(ValueError): Journal.open(self.path,'c1','b'*64)
        self.assertEqual(self.reopen().snapshot('r1p1')['state'],'pending')

    def test_round_barrier_and_exchange(self):
        with self.assertRaises(ValueError): self.j.claim('r2p1')
        self.j.claim('r1p1'); self.finish('r1p1')
        with self.assertRaises(ValueError): self.j.claim('r2p1')
        self.j.claim('r1p2'); self.finish('r1p2')
        claimed = self.j.claim('r2p1')
        self.assertEqual((claimed['preparer'],claimed['reviewer']),('P1','R2'))

    def test_second_connection_cannot_claim_running_or_interrupted_task(self):
        self.j.claim('r1p1')
        other = self.reopen()
        with self.assertRaises(ValueError): other.claim('r1p1')
        self.assertEqual(other.snapshot('r1p1')['state'],'running')
        with self.assertRaises(ValueError): other.claim('unknown')

    def test_finish_requires_claim_and_preserves_release_after_late_failure(self):
        with self.assertRaises(ValueError): self.finish('r1p1')
        self.j.claim('r1p1')
        files = {'aggregate.json':[{'segment':'synthetic-A','count':1000}]}
        self.finish('r1p1','approved',2,files)
        files['aggregate.json'][0]['count'] = 0
        with self.assertRaises(ValueError): self.finish('r1p1','api_failure',0)
        snap = self.reopen().snapshot('r1p1')
        self.assertEqual(snap['terminal'],'approved')
        self.assertEqual(snap['released_files']['aggregate.json'][0]['count'],1000)
        self.assertEqual(snap['tool_result'],{'ok':True})

    def test_caller_mutation_while_acquiring_writer_cannot_split_terminal_evidence(self):
        self.j.claim('r1p1')
        files = {'aggregate.json':[{'count':1000}]}
        report = {'free_text':'original'}
        result = {'ok':True}
        transaction = self.j._transaction

        @contextmanager
        def mutate_before_writer_lock():
            # Deterministic equivalent of a caller mutating while BEGIN waits.
            files.clear()
            report['free_text'] = 'changed'
            result['ok'] = False
            with transaction():
                yield

        self.j._transaction = mutate_before_writer_lock
        self.j.finish('r1p1','approved',2,files,report,result)
        snap = self.reopen().snapshot('r1p1')
        event = self.j.events()[-1]['payload']
        self.assertEqual(snap['released_files'],{'aggregate.json':[{'count':1000}]})
        for key in ('released_files','report','tool_result','terminal','points'):
            self.assertEqual(snap[key],event[key])

    def test_terminal_event_failure_rolls_back_release_and_terminal(self):
        self.j.claim('r1p1')
        c=sqlite3.connect(self.path)
        c.execute("CREATE TRIGGER fail_terminal BEFORE INSERT ON events WHEN NEW.kind='terminal' BEGIN SELECT RAISE(ABORT,'disk fixture'); END")
        c.commit(); c.close()
        with self.assertRaises(sqlite3.IntegrityError):
            self.finish('r1p1','approved',2,{'aggregate.json':[]})
        snap=self.reopen().snapshot('r1p1')
        self.assertEqual(snap['state'],'running')
        self.assertIsNone(snap['released_files'])
        self.assertEqual([e['kind'] for e in self.j.events()],['claim'])

    def test_scoped_events_and_sequence(self):
        self.j.claim('r1p1')
        payload={'messages':[{'role':'user','content':'original'}]}
        seq=self.j.append('r1p1','api_input',payload)
        payload['messages'][0]['content']='changed'
        self.assertEqual(seq,1)
        with self.assertRaises(ValueError): self.j.append('r1p2','api_input',{})
        self.finish('r1p1')
        with self.assertRaises(ValueError): self.j.append('r1p1','api_input',{})
        ev=self.reopen().events()
        self.assertEqual([e['event_id'] for e in ev],[0,1,2])
        self.assertEqual(ev[1]['payload']['messages'][0]['content'],'original')
        self.assertTrue(all(e['request_id']=='r1p1' for e in ev))

    def test_invalid_terminal_and_json_never_mutate_running_slot(self):
        self.j.claim('r1p1')
        for terminal,points,files in [('approved',2,{}),('rejected',1,{'aggregate.json':[]}),('rejected',True,{}),('unknown',0,{})]:
            with self.assertRaises(ValueError): self.finish('r1p1',terminal,points,files)
        with self.assertRaises(ValueError): self.j.append('r1p1','api_input',{'x':float('nan')})
        with self.assertRaises(ValueError): self.j.append('r1p1','terminal',{})
        self.assertEqual(self.j.snapshot('r1p1')['state'],'running')
        self.assertEqual(len(self.j.events()),1)

    def test_api_failure_stops_round_two_without_discarding_completed_results(self):
        self.j.claim('r1p2'); self.finish('r1p2')
        self.j.claim('r1p1'); self.finish('r1p1','api_failure',0)
        with self.assertRaises(ValueError): self.j.claim('r2p1')
        self.assertEqual(self.reopen().snapshot('r1p2')['terminal'],'rejected')

if __name__=='__main__': unittest.main()
