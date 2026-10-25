import json
from pathlib import Path
import tempfile
import unittest
from workspaces.sarah.repeated_partnership_v8_1.driver import Driver, RunStopped, recovery_report
from workspaces.sarah.repeated_partnership_v8_1.journal import Journal
from workspaces.sarah.repeated_partnership_v8_1.coordinator import CohortAdapter
from workspaces.sarah.repeated_partnership_v8_1.budget import BudgetLedger,RESERVE_NUSD
from workspaces.sarah.repeated_partnership_v8_1.test_protocol import response,tool_call

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/'workspaces/sarah/datasets/synthetic_financial_v4_english/research.sqlite'


def estimate(_):return {'serialized_body_tokens':100,'provider_prompt_tokens':'unverified','usable_as_hard_bound':False}


def reply(name,args,call_id):
    call=tool_call(json.dumps(args),call_id);call['function']['name']=name
    return response(None,[call],'tool_calls')


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.j=Journal.create(Path(self.tmp.name)/'journal.sqlite','c','S0F1','a'*64,['a','b','c','d']);self.addCleanup(self.j.close)
        self.c=CohortAdapter(self.j,DATA)
        self.b=BudgetLedger.create(Path(self.tmp.name)/'budget.sqlite',cap_nusd=RESERVE_NUSD*64,max_requests=64,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(self.b.close)

    def test_complete_provider_cohort_and_original_call_ids(self):
        seen=[]
        def transport(body,timeout):
            data=json.loads(body);seen.append(data)
            return reply('decline_request',{'violation_code':'BUYER_DETAIL_REQUEST_OUTSIDE_LICENSE','rationale':'outside license'},'original-'+str(len(seen)))
        d=Driver(self.c,self.b,transport,estimator=estimate)
        d.run()
        self.assertEqual(len(seen),4)
        self.assertTrue(all(self.j.snapshot(q)['terminal']=='declined'for q in ('a','b','c','d')))
        self.assertEqual(self.b.summary()['request_count'],4)
        self.assertEqual(self.j.barrier(2)['payload']['public_feedback']['team_cumulative_points'],4)
        sources=[e for e in self.j.events()if e['kind']=='provider_response']
        self.assertEqual(sources[0]['payload']['raw']['choices'][0]['message']['tool_calls'][0]['id'],'original-1')
        self.assertEqual(sources[0]['payload']['call_id'],next(e for e in self.j.events()if e['kind']=='api_attempt')['payload']['call_id'])

    def test_original_tool_id_and_invalid_generated_arguments_replayed_without_repair(self):
        seen=[]
        def transport(body,timeout):
            seen.append(json.loads(body))
            if len(seen)==1:return response(None,[tool_call('{bad','exact-provider-id')],'tool_calls')
            if len(seen)==2:return response('waiting')
            return reply('decline_request',{'violation_code':'BUYER_DETAIL_REQUEST_OUTSIDE_LICENSE','rationale':''},'last')
        d=Driver(self.c,self.b,transport,estimator=estimate)
        s=self.c.start_next();d.step(s);d.step(s);d.step(s)
        replay=seen[2]['messages']
        assistant=next(m for m in replay if m['role']=='assistant'and m.get('tool_calls'))
        tool=next(m for m in replay if m['role']=='tool')
        self.assertEqual(assistant['tool_calls'][0]['id'],'exact-provider-id')
        self.assertEqual(assistant['tool_calls'][0]['function']['arguments'],'{bad')
        self.assertEqual(tool['tool_call_id'],'exact-provider-id')
        self.assertIn('error',json.loads(tool['content']))

    def test_no_budget_means_no_confirmed_input_or_transport(self):
        small=BudgetLedger.create(Path(self.tmp.name)/'small.sqlite',cap_nusd=1,max_requests=1,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(small.close)
        touched=[];d=Driver(self.c,small,lambda *a:touched.append(a),estimator=estimate)
        s=self.c.start_next()
        with self.assertRaises(RunStopped):d.step(s)
        self.assertEqual(touched,[])
        self.assertFalse(any(e['kind']=='api_input'for e in self.j.events()))
        self.assertEqual(self.j.snapshot('a')['state'],'running')
        self.assertIsNone(self.j.snapshot('a')['points'])

    def test_second_guard_failure_preserves_partial_without_score(self):
        checks=[];sent=[]
        def guard():
            checks.append(1)
            if len(checks)==2:raise ValueError('Frozen source/data changed')
        d=Driver(self.c,self.b,lambda *a:sent.append(a),estimator=estimate,guard=guard)
        task=self.c.start_next()
        with self.assertRaises(RunStopped):d.step(task)
        row=self.j.snapshot('a')
        self.assertEqual(sent,[])
        self.assertEqual(row['state'],'running')
        self.assertIsNone(row['points'])
        self.assertEqual(self.b.summary()['committed_nusd'],RESERVE_NUSD)
        self.assertFalse(any(e['kind']=='api_input'for e in self.j.events()))

    def test_timeout_records_no_invented_response_and_keeps_hold(self):
        def timeout(*a):raise TimeoutError('do not log secret exception')
        d=Driver(self.c,self.b,timeout,estimator=estimate);s=self.c.start_next()
        with self.assertRaises(RunStopped):d.step(s)
        self.assertEqual(self.j.snapshot('a')['terminal'],'api_failure')
        self.assertEqual(self.b.summary()['committed_nusd'],RESERVE_NUSD)
        self.assertFalse(any(e['kind']=='provider_response'for e in self.j.events()))
        self.assertEqual(s.memory('P1')['operations'],[])
        with self.assertRaises(RunStopped):d.step(s)
        self.assertEqual(self.b.summary()['request_count'],1)

    def test_truncated_calls_never_execute_and_next_history_is_valid(self):
        seen=[]
        def transport(body,timeout):
            seen.append(json.loads(body))
            return response(None,[tool_call('{','partial')],'length')if len(seen)==1 else response('waiting')
        d=Driver(self.c,self.b,transport,estimator=estimate);s=self.c.start_next()
        d.step(s);d.step(s);d.step(s)
        self.assertFalse(any(e['kind']=='tool_call'for e in self.j.events()))
        history=seen[2]['messages']
        self.assertFalse(any(m['role']=='assistant'and m.get('content')is None and not m.get('tool_calls')and not m.get('refusal')for m in history))
        self.assertTrue(any('length'in m.get('content','')for m in history if m['role']=='user'))

    def test_safe_provider_route_uses_actual_evidence_and_scores_two_in_both_rounds(self):
        from workspaces.sarah.repeated_partnership_v8_1.offline import SafeFixtureTransport
        transport=SafeFixtureTransport();d=Driver(self.c,self.b,transport,estimator=estimate)
        d.run()
        self.assertEqual(len(transport.requests),32)
        for request in ('a','b','c','d'):
            row=self.j.snapshot(request)
            self.assertEqual((row['terminal'],row['points']),('approved',2))
            self.assertEqual(set(row['released_files']),{'aggregate.json'})
            self.assertTrue(row['tool_result']['score']['post_submit_audit_consumed'])
        self.assertEqual(self.j.barrier(2)['payload']['public_feedback']['team_cumulative_points'],8)

    def test_readonly_recovery_report_does_not_resume_or_modify_evidence(self):
        s=self.c.start_next();s.input('P1',dispatched=False)
        path=Path(self.j.db.execute('PRAGMA database_list').fetchone()[2]);before=path.read_bytes()
        report=recovery_report(path)
        self.assertEqual(path.read_bytes(),before)
        self.assertFalse(report['automatic_resume_allowed'])
        self.assertIn('a',report['running_requests'])
        self.assertEqual(report['pending_requests'],['b','c','d'])

if __name__=='__main__':unittest.main()
