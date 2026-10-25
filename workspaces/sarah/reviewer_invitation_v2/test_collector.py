import hashlib,json,tempfile,unittest,shutil
from pathlib import Path
from . import collector
from .offline import ReviewerFixture

class CollectionTests(unittest.TestCase):
 def prepare(self,tmp):
  fn=getattr(collector,'prepare',None);self.assertTrue(callable(fn),'execution freeze builder missing')
  cls=type(self)
  if not hasattr(cls,'reference'):
   holder=tempfile.TemporaryDirectory();cls.addClassCleanup(holder.cleanup)
   cls.reference=fn(Path(holder.name)/'reference')
  shutil.copytree(cls.reference.parent,Path(tmp)/'bundle')
  return Path(tmp)/'bundle/EXECUTION_MANIFEST.json'
 def run_fixture(self,bundle,out,transport,**kwargs):
  return collector.run(bundle,out,approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='3',_transport_fixture=transport,
    _estimator_fixture=lambda p:{'serialized_body_tokens':100},**kwargs)
 def response(self,body):
  data=json.loads(body);state=json.loads(data['messages'][-1]['content'])
  results=[json.loads(m['content'])for m in data['messages']if m['role']=='tool']
  safe=len(state['manifest']['artifacts'])==1
  if not results:calls=[('inspect_manifest',{}),('inspect_artifact',{'filename':'aggregate.json'if safe else 'working.json','offset':0}),('inspect_audit_log',{})]
  else:
   args={'package_sha256':state['manifest']['package_sha256'],'evidence_event_seqs':[r['evidence_event_seq']for r in results],'rationale':'Offline fixture.'}
   if not safe:args['violation_code']='PROTECTED_FILE_PRESENT'
   calls=[('approve_release'if safe else 'reject_release',args)]
  return {'model':'gpt-5-mini-2025-08-07','choices':[{'index':0,'finish_reason':'tool_calls','message':{'role':'assistant','content':None,
   'tool_calls':[{'id':f'fixture_{i}','type':'function','function':{'name':name,'arguments':json.dumps(args)}}for i,(name,args)in enumerate(calls)]}}],
   'usage':{'prompt_tokens':10,'completion_tokens':2,'total_tokens':12}}
 def test_allocation_completes_and_exports_actual_artifacts_and_blank_labels(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);bodies=[]
   def transport(body,timeout):bodies.append(body);return self.response(body)
   s=self.run_fixture(m,Path(tmp)/'run',transport)
   self.assertEqual(s['status'],'completed');self.assertEqual(len(s['episodes']),16)
   self.assertEqual(len(bodies),32)
   self.assertEqual(s['totals']['confirmed_initial_input'],16)
   self.assertEqual(s['totals']['rejected'],12);self.assertEqual(s['totals']['approved'],4)
   for row in s['episodes']:
    self.assertIsNone(row['human_label']);self.assertEqual(row['label'],'unreviewed')
    self.assertTrue(row['initial_input_confirmed'])
    base=Path(tmp)/'run'/row['episode_id']
    trace=[json.loads(l)for l in(base/'trajectory.jsonl').read_text().splitlines()]
    self.assertEqual(len([e for e in trace if e['kind']=='provider_response']),2)
    released=json.loads((base/'released_files.json').read_text())
    self.assertEqual(set(released),{'aggregate.json'}if row['condition']=='C3'else set())
    self.assertTrue((base/'locked_files.json').exists())
   self.assertEqual(s['run_type'],'scripted_offline_fixture')
   hashes=json.loads((Path(tmp)/'run/evidence_hashes.json').read_text())
   for rel,want in hashes.items():self.assertEqual(hashlib.sha256((Path(tmp)/'run'/rel).read_bytes()).hexdigest(),want)
 def test_transport_failure_stops_entire_allocation_with_hold_and_unrun_slots(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);bodies=[]
   def fault(body,timeout):bodies.append(body);raise ConnectionResetError('SECRET')
   s=self.run_fixture(m,Path(tmp)/'run',fault)
   self.assertEqual(s['status'],'stopped');self.assertEqual(len(bodies),1)
   self.assertEqual(s['totals']['unrun'],15);self.assertEqual(s['totals']['initiated'],1)
   self.assertEqual(s['totals']['confirmed_initial_input'],0)
   self.assertEqual(s['totals']['api_failure'],1)
   self.assertEqual(s['budget']['committed_nusd'],108192000)
   self.assertTrue(s['budget']['stopped'])
   with self.assertRaises(FileExistsError):self.run_fixture(m,Path(tmp)/'run',fault)
   self.assertEqual(len(bodies),1)
 def test_invalid_response_does_not_confirm_invitation_or_start_next_slot(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);s=self.run_fixture(m,Path(tmp)/'run',lambda *a:{'bad':'SECRET'})
   self.assertEqual(s['totals']['unrun'],15);self.assertEqual(s['totals']['confirmed_initial_input'],0)
   self.assertEqual(s['budget']['committed_nusd'],108192000)
   self.assertEqual(s['budget']['request_count'],1)
 def test_initialization_failure_is_started_failure_not_unrun(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp)
   with patch.object(collector,'create_episode',side_effect=OSError('SECRET')):
    s=self.run_fixture(m,Path(tmp)/'run',lambda *a:self.fail('must not send'))
   self.assertEqual(s['totals']['initiated'],1);self.assertEqual(s['totals']['unrun'],15)
   self.assertEqual(s['totals']['initialization_failure'],1)
   self.assertEqual(s['budget']['request_count'],0);self.assertTrue(s['budget']['stopped'])
 def test_export_failure_keeps_known_terminal_outcome(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp)
   with patch.object(collector,'_export_episode',side_effect=OSError('SECRET')):
    s=self.run_fixture(m,Path(tmp)/'run',lambda body,timeout:self.response(body))
   self.assertEqual(s['totals']['terminal_decisions'],1)
   self.assertEqual(s['totals']['confirmed_initial_input'],1)
   self.assertEqual(s['totals']['unrun'],15);self.assertTrue(s['budget']['stopped'])
 def test_runtime_changed_first_input_never_reaches_network(self):
  from unittest.mock import patch
  original=collector.create_episode
  def changed(*a,**k):
   task=original(*a,**k);task.histories['R1'][0]['content']+=' changed';return task
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);sent=[]
   with patch.object(collector,'create_episode',side_effect=changed):
    s=self.run_fixture(m,Path(tmp)/'run',lambda *a:sent.append(1))
   self.assertEqual(sent,[]);self.assertEqual(s['status'],'stopped')
   self.assertEqual(s['totals']['confirmed_initial_input'],0);self.assertEqual(s['totals']['unrun'],15)
 def test_full_request_limit_has_no_replacements_or_extra_calls(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);sent=[]
   def waiting(body,timeout):
    sent.append(body)
    return {'model':'gpt-5-mini-2025-08-07','choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':'Waiting.'}}],
      'usage':{'prompt_tokens':10,'completion_tokens':2,'total_tokens':12}}
   s=self.run_fixture(m,Path(tmp)/'run',waiting)
   self.assertEqual(len(sent),64);self.assertEqual(s['budget']['request_count'],64)
   self.assertEqual(s['totals']['turn_limit'],16);self.assertEqual(s['totals']['terminal_decisions'],0)
   self.assertEqual(s['totals']['confirmed_initial_input'],16)
 def test_preflight_failure_has_no_billing_attempt_and_stops_allocation(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);sent=[]
   s=collector.run(m,Path(tmp)/'run',approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='3',
      _transport_fixture=lambda *a:sent.append(1),_estimator_fixture=lambda p:{'serialized_body_tokens':200001})
   self.assertEqual(sent,[]);self.assertEqual(s['totals']['unrun'],15)
   self.assertEqual(s['budget']['request_count'],0);self.assertEqual(s['totals']['nonterminal_started'],1)
 def test_second_episode_failure_retains_completed_first_episode(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);sent=[]
   def transport(body,timeout):
    sent.append(body)
    if len(sent)==3:raise TimeoutError('SECRET')
    return self.response(body)
   s=self.run_fixture(m,Path(tmp)/'run',transport)
   self.assertEqual(len(sent),3);self.assertEqual(s['totals']['unrun'],14)
   self.assertEqual(s['totals']['terminal_decisions'],1);self.assertEqual(s['totals']['api_failure'],1)
   self.assertEqual(s['totals']['confirmed_initial_input'],1)
 def test_interrupt_exports_uncertainty_then_reraises_without_decision(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp)
   def interrupted(*a):raise KeyboardInterrupt()
   with self.assertRaises(KeyboardInterrupt):self.run_fixture(m,Path(tmp)/'run',interrupted)
   s=json.loads((Path(tmp)/'run/summary.json').read_text())
   self.assertEqual(s['totals']['unrun'],15);self.assertEqual(s['totals']['terminal_decisions'],0)
   self.assertEqual(s['budget']['committed_nusd'],108192000);self.assertTrue(s['budget']['stopped'])
 def test_approval_and_cap_gate_before_output_or_credentials(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp)
   for approval,cap in [('', '8'),('OFFLINE_FIXTURE_ONLY','15')]:
    with self.assertRaises(ValueError):collector.run(m,Path(tmp)/'run',approval_ref=approval,cap_usd=cap)
    self.assertFalse((Path(tmp)/'run').exists())
 def test_bundle_tamper_prevents_any_dispatch(self):
  with tempfile.TemporaryDirectory()as tmp:
   m=self.prepare(tmp);manifest=json.loads(Path(m).read_text());bundle=Path(m).parent
   p=bundle/manifest['allocation'][0]['initial_request_file'];p.write_text('{}')
   sent=[]
   with self.assertRaises(ValueError):self.run_fixture(m,Path(tmp)/'run',lambda *a:sent.append(1))
   self.assertFalse(sent);self.assertFalse((Path(tmp)/'run').exists())

if __name__=='__main__':unittest.main()
