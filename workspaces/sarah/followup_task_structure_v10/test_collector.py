import hashlib,json,tempfile,unittest
from pathlib import Path
from workspaces.sarah.followup_task_structure_v10 import collector
from workspaces.sarah.repeated_partnership_v8_1.protocol import MODEL

class CollectionChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.reference_dir=tempfile.TemporaryDirectory();base=Path(cls.reference_dir.name)/'freeze';base.mkdir()
  cls.reference=collector.prepare(base/'bundle')
 @classmethod
 def tearDownClass(cls):cls.reference_dir.cleanup()
 def fixture_bundle(self,tmp):
  return self.reference
 def response(self,body):
  data=json.loads(body);state=json.loads(data['messages'][-1]['content'])
  results=[json.loads(m['content'])for m in data['messages']if m['role']=='tool']
  if not results:
   calls=[('inspect_manifest',{}),('inspect_artifact',{'filename':'aggregate.json','offset':0}),
          ('inspect_artifact',{'filename':'synthetic_rows.json','offset':0}),('inspect_audit_log',{})]
  else:
   call={'package_sha256':state['manifest']['package_sha256'],
         'evidence_event_seqs':[r['evidence_event_seq']for r in results],
         'rationale':'Offline deterministic rejection route.','violation_code':'PROTECTED_FILE_PRESENT'}
   calls=[('reject_release',call)]
  return {'model':MODEL,'choices':[{'index':0,'finish_reason':'tool_calls','message':{'role':'assistant','content':None,
   'tool_calls':[{'id':f'fixture_{i}','type':'function','function':{'name':n,'arguments':json.dumps(a)}}for i,(n,a)in enumerate(calls)]}}],
   'usage':{'prompt_tokens':10,'completion_tokens':2,'total_tokens':12}}
 def run_fixture(self,m,out,transport):
  return collector.run(m,out,approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='9.756574',_transport_fixture=transport,
   _estimator_fixture=lambda p:{'serialized_body_tokens':100})
 def test_fixed_allocation_raw_exports_and_labels_stay_unreviewed(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.fixture_bundle(tmp);sent=[]
   s=self.run_fixture(m,Path(tmp)/'run',lambda b,t:(sent.append(b),self.response(b))[1])
   self.assertEqual(s['status'],'completed');self.assertEqual(len(s['episodes']),24);self.assertEqual(len(sent),48)
   self.assertEqual(s['totals']['confirmed_initial_input'],24);self.assertEqual(s['totals']['rejected'],24)
   for row in s['episodes']:
    self.assertEqual(row['label'],'unreviewed');self.assertIsNone(row['human_label'])
    root=Path(tmp)/'run'/row['episode_id'];trace=[json.loads(x)for x in(root/'trajectory.jsonl').read_text().splitlines()]
    self.assertEqual(len([e for e in trace if e['kind']=='provider_response']),2)
    self.assertEqual(set(json.loads((root/'released_files.json').read_text())),set())
    digests=json.loads((Path(tmp)/'run/evidence_hashes.json').read_text())
   for rel,want in digests.items():self.assertEqual(hashlib.sha256((Path(tmp)/'run'/rel).read_bytes()).hexdigest(),want)
 def test_postcheck_approval_can_release_and_no_budget_substitution(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.fixture_bundle(tmp);manifest=json.loads(Path(m).read_text())
   self.assertEqual(manifest['cap_usd'],'9.756574');self.assertEqual(manifest['max_episodes'],24)
   self.assertEqual(manifest['prior_budget_check']['committed_nusd'],243426000)
   from workspaces.sarah.followup_task_structure_v10.engine import create_episode
   from workspaces.sarah.followup_task_structure_v10.offline import DATA
   t=create_episode(Path(tmp)/'direct','D1M2',DATA,episode_id='direct_release_test')
   try:
    t.input('R1');t._respond('R1','',[{'name':'inspect_manifest','arguments':{}},{'name':'inspect_artifact','arguments':{'filename':'aggregate.json','offset':0}},
     {'name':'inspect_artifact','arguments':{'filename':'synthetic_rows.json','offset':0}},{'name':'inspect_audit_log','arguments':{}}])
    p=t.input('R1');state=json.loads(p['messages'][-1]['content'])
    t._respond('R1','',[{'name':'approve_release','arguments':{'package_sha256':t.report['package_sha256'],'evidence_event_seqs':t._deciding_consumed('R1'),'rationale':'Offline mechanism check.'}}])
    released=t.journal.snapshot(t.request_id)['released_files'];self.assertEqual(len(released['synthetic_rows.json']),2000)
   finally:t.journal.close()
 def test_transport_uncertainty_preserves_slot_and_stops_before_next(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.fixture_bundle(tmp);calls=[]
   def fault(body,timeout):calls.append(body);raise TimeoutError('private')
   s=self.run_fixture(m,Path(tmp)/'run',fault)
   self.assertEqual(len(calls),1);self.assertEqual(s['totals']['unrun'],23)
   self.assertEqual(s['totals']['api_failure'],1);self.assertTrue(s['budget']['stopped'])
 def test_wrong_remainder_or_prior_ledger_mismatch_blocks_run(self):
  for cap in ('10','9.75'):
   with tempfile.TemporaryDirectory()as tmp:
    m=self.fixture_bundle(tmp);called=[]
    with self.assertRaises(ValueError):collector.run(m,Path(tmp)/'run',approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd=cap,_transport_fixture=lambda *a:called.append(1))
    self.assertEqual(called,[]);self.assertFalse((Path(tmp)/'run').exists())
if __name__=='__main__':unittest.main()
