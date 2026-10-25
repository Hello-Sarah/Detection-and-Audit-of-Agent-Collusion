import json,tempfile,unittest
from pathlib import Path
from workspaces.sarah.v8_transport_diagnostics.launch import freeze,run_technical

class LaunchTests(unittest.TestCase):
 def setup_run(self,tmp):
  p=Path(tmp);r=p/'readiness.json';r.write_text(json.dumps({'status':'offline_pass','model':'gpt-5-mini-2025-08-07','tokenizer_version':'0.12.0','encoding':'o200k_base'}))
  m=p/'manifest.json';freeze(m,r);return p,m
 def test_full_runner_persists_failure_and_all_pending_slots(self):
  with tempfile.TemporaryDirectory()as tmp:
   p,m=self.setup_run(tmp)
   def disconnected(*a):raise ConnectionResetError('SECRET')
   s=run_technical(m,p/'run',approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='15',_transport_fixture=disconnected,_estimator_fixture=lambda p:{'serialized_body_tokens':100})
   self.assertEqual(s['status'],'stopped');self.assertTrue(s['budget']['stopped'])
   self.assertEqual(s['budget']['committed_nusd'],108192000)
   self.assertEqual(sum(e['state']=='unrun'or e['state']=='pending'for e in s['episodes']),7)
   log=p/'run/transport.jsonl';self.assertTrue(log.exists(),'runner lacks persisted diagnostics')
   events=[json.loads(l)for l in log.read_text().splitlines()]
   self.assertEqual(events[-1]['failure'],'CONNECTION_RESET')
   self.assertEqual(s['transport_diagnostics']['events'],2)
   self.assertNotIn('SECRET',log.read_text())
 def test_complete_eight_deliveries_with_persisted_fixture_transport(self):
  from workspaces.sarah.repeated_partnership_v8_1.offline import SafeFixtureTransport
  with tempfile.TemporaryDirectory()as tmp:
   p,m=self.setup_run(tmp);fixture=SafeFixtureTransport()
   s=run_technical(m,p/'run',approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='15',_transport_fixture=fixture,_estimator_fixture=lambda p:{'serialized_body_tokens':100})
   self.assertEqual(s['status'],'completed')
   self.assertEqual(len(s['episodes']),8)
   self.assertTrue(all(e['terminal']=='approved'and e['mechanical_points']==2 for e in s['episodes']))
   self.assertEqual(s['transport_diagnostics']['events'],2*len(fixture.requests))
   self.assertEqual(s['run_type'],'scripted_offline_fixture')
 def test_missing_approval_creates_no_live_directory(self):
  with tempfile.TemporaryDirectory()as tmp:
   p,m=self.setup_run(tmp)
   with self.assertRaises(ValueError):run_technical(m,p/'run',approval_ref='',cap_usd='15')
   self.assertFalse((p/'run').exists())

if __name__=='__main__':unittest.main()
