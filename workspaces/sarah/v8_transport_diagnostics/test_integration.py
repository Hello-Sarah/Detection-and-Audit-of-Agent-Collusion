import hashlib,json,tempfile,unittest
from pathlib import Path
from workspaces.sarah.v8_transport_diagnostics import candidate
from workspaces.sarah.repeated_partnership_v8_1.budget import BudgetLedger,BoundedDispatcher,BudgetStop
from workspaces.sarah.repeated_partnership_v8_1.test_protocol import actor_input,response

class IntegrationTests(unittest.TestCase):
 def make(self,budget,path,transport):
  cls=getattr(candidate,'PersistentTransport',None)
  self.assertTrue(callable(cls),'durable integration missing')
  t=cls(budget,path,transport);self.addCleanup(t.close);return t
 def test_fault_persists_call_id_and_retains_unknown_hold_without_retry(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);b=BudgetLedger.create(p/'budget.sqlite',cap_nusd=15*10**9,max_requests=128,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(b.close)
   calls=[]
   def fault(body,timeout):calls.append(body);raise ConnectionResetError('SECRET')
   t=self.make(b,p/'transport.jsonl',fault)
   with self.assertRaises(BudgetStop):BoundedDispatcher(b,t).dispatch('fault',actor_input())
   es=[json.loads(l)for l in (p/'transport.jsonl').read_text().splitlines()]
   self.assertEqual([e['status']for e in es],['dispatch_start','failed'])
   self.assertTrue(all(e['call_id']=='fault'for e in es))
   self.assertEqual(es[-1]['failure'],'CONNECTION_RESET')
   self.assertNotIn('SECRET',json.dumps(es));self.assertEqual(len(calls),1)
   self.assertEqual(b.summary()['committed_nusd'],108192000);self.assertTrue(b.summary()['stopped'])
 def test_response_received_is_not_misreported_as_successful_validation(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);b=BudgetLedger.create(p/'b.sqlite',cap_nusd=15*10**9,max_requests=128,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(b.close)
   t=self.make(b,p/'t.jsonl',lambda *a:{'invalid':'SECRET'})
   with self.assertRaises(BudgetStop):BoundedDispatcher(b,t).dispatch('bad',actor_input())
   es=[json.loads(l)for l in (p/'t.jsonl').read_text().splitlines()]
   self.assertEqual(es[-1]['status'],'response_received');self.assertNotIn('SECRET',json.dumps(es))
   self.assertTrue(b.summary()['stopped'])
 def test_fsync_failure_prevents_network_and_conservatively_stops_budget(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);b=BudgetLedger.create(p/'b.sqlite',cap_nusd=15*10**9,max_requests=128,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(b.close)
   touched=[];t=self.make(b,p/'t.jsonl',lambda *a:touched.append(1))
   with patch('os.fsync',side_effect=OSError('SECRET')):
    with self.assertRaises(BudgetStop):BoundedDispatcher(b,t).dispatch('fault',actor_input())
   self.assertEqual(touched,[]);self.assertTrue(b.summary()['stopped'])
   self.assertEqual(b.summary()['committed_nusd'],108192000)
 def test_result_log_failure_preserves_hold_after_one_network_call(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);b=BudgetLedger.create(p/'b.sqlite',cap_nusd=15*10**9,max_requests=128,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(b.close)
   touched=[]
   def network(*a):touched.append(1);return response()
   t=self.make(b,p/'t.jsonl',network)
   original=t._record;count=[]
   def record(event):
    count.append(event)
    if len(count)>1:raise OSError('SECRET')
    original(event)
   with patch.object(t,'_record',side_effect=record):
    with self.assertRaises(BudgetStop):BoundedDispatcher(b,t).dispatch('fault',actor_input())
   self.assertEqual(len(touched),1);self.assertTrue(b.summary()['stopped'])
   self.assertEqual(b.summary()['committed_nusd'],108192000)
   self.assertNotIn('SECRET',(p/'t.jsonl').read_text())
 def test_unreserved_request_and_existing_log_cannot_dispatch(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);b=BudgetLedger.create(p/'b.sqlite',cap_nusd=15*10**9,max_requests=128,approval_ref='OFFLINE_FIXTURE_ONLY');self.addCleanup(b.close)
   touched=[];t=self.make(b,p/'t.jsonl',lambda *a:touched.append(1))
   with self.assertRaises(ValueError):t(b'{}',90)
   self.assertEqual(touched,[])
   with self.assertRaises(FileExistsError):type(t)(b,p/'t.jsonl',lambda *a:None)

if __name__=='__main__':unittest.main()
