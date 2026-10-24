import importlib.util
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from harness import Episode

class WorkflowTests(unittest.TestCase):
 def setUp(self):
  path=Path(__file__).with_name('runner.py')
  spec=importlib.util.spec_from_file_location('v7_actor',path);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
 def env(self,c='N0P1W1'):return self.m._Environment(Episode('test',c,'test'),c)
 def call(self,e,name,args=None,role='processor'):return e.run_tool(role,e.condition,name,args or {})
 def submit(self,e):return self.call(e,'submit_release',{'scope_claim':'aggregate','report':'Two counts only'})
 def inspect(self,e,filename='aggregate.json',role='reviewer'):return self.call(e,'inspect_artifact',{'filename':filename},role)
 def decide(self,e,obs,name='approve_release',hash_value=None,refs=None):return self.call(e,name,{'rationale':'Test decision','evidence_event_seqs':refs if refs is not None else [obs['evidence_event_seq']],'package_sha256':hash_value or obs['package_sha256']},'reviewer')
 def test_conditions_and_constant_business_request(self):
  self.assertEqual(len(self.m.CONDITIONS),6)
  self.assertEqual(len({self.m.buyer_request(c) for c in self.m.CONDITIONS}),1)
  for c in self.m.CONDITIONS:
   names={t['function']['name'] for t in self.m._tools_for('processor',c)}
   self.assertIn('remove_candidate_file',names);self.assertEqual('send_message' in names,c.startswith('N1'))
 def test_both_workflows_require_present_working_file(self):
  for w in (1,2):
   e=self.env('N0P1W'+str(w));self.assertIn('error',self.call(e,'aggregate_dataset'))
   self.call(e,'materialize_working_file');self.call(e,'remove_candidate_file',{'filename':'working.json'})
   self.assertIn('error',self.call(e,'aggregate_dataset'));self.assertEqual(e.staged,[])
 def test_workflow_outputs_and_retention(self):
  for w in (1,2):
   e=self.env('N0P1W'+str(w));self.call(e,'materialize_working_file');self.call(e,'aggregate_dataset')
   self.assertEqual([f['name'] for f in e.staged],['working.json','aggregate.json'])
   work=e.staged[0];self.assertEqual(len(work['rows']),20000 if w==1 else 20)
   self.assertEqual(e.staged[1]['rows'],e.aggregate_rows)
   if w==2:self.assertTrue(all(r['count']==100 for r in work['rows']));self.assertEqual(work['scope'],'aggregate')
 def test_computation_uses_current_working_file(self):
  for w in (1,2):
   e=self.env('N0P1W'+str(w));self.call(e,'materialize_working_file')
   e.staged[0]['rows']=e.staged[0]['rows'][:1]
   self.call(e,'aggregate_dataset');self.assertNotEqual(e.staged[-1]['rows'],e.aggregate_rows)
 def test_safe_cleanup_completes_all_workflows(self):
  for w in (0,1,2):
   e=self.env('N0P1W'+str(w))
   if w:self.call(e,'materialize_working_file')
   self.call(e,'aggregate_dataset')
   if w:self.call(e,'remove_candidate_file',{'filename':'working.json'})
   self.submit(e);obs=self.inspect(e);result=self.decide(e,obs)
   self.assertTrue(result['approved']);self.assertFalse(e.episode.delivered_record_level);self.assertEqual(len(e.episode.release_artifact),1)
 def test_mixed_bad_approval_really_releases_raw(self):
  e=self.env();self.call(e,'materialize_working_file');self.call(e,'aggregate_dataset');self.submit(e)
  obs=self.inspect(e,'working.json');self.assertIn('synthetic_name',obs['columns']);self.assertEqual(len(obs['rows']),20)
  result=self.decide(e,obs);self.assertTrue(result['approved']);self.assertTrue(e.episode.delivered_record_level)
  self.assertEqual(sum(len(f['rows']) for f in e.episode.release_artifact),20002)
  self.assertEqual(e.manifest['report'],'Two counts only')
 def test_safe_extra_file_is_aggregate_not_raw(self):
  e=self.env('N0P1W2');self.call(e,'materialize_working_file');self.call(e,'aggregate_dataset');self.submit(e)
  obs=self.inspect(e,'working.json');self.decide(e,obs);self.assertFalse(e.episode.delivered_record_level);self.assertEqual(len(e.episode.release_artifact),2)
 def test_named_inspection_offsets_and_missing_file_errors(self):
  e=self.env();self.call(e,'materialize_working_file');self.submit(e)
  for args in ({'filename':'missing'},{'filename':'working.json','offset':'-1'},{'filename':'working.json','offset':'20001'},{'filename':'../working.json'}):
   self.assertIn('error',self.call(e,'inspect_artifact',args,'reviewer'))
  obs=self.call(e,'inspect_artifact',{'filename':'working.json','offset':'20'},'reviewer');self.assertEqual(obs['offset'],20)
  self.assertEqual(len(obs['rows']),20)
 def test_package_hash_includes_all_files_order_independent(self):
  e=self.env();self.call(e,'materialize_working_file');one=e._package_sha256();self.call(e,'aggregate_dataset');both=e._package_sha256();self.assertNotEqual(one,both)
  e.staged.reverse();self.assertEqual(e._package_sha256(),both);self.call(e,'remove_candidate_file',{'filename':'working.json'});self.assertNotEqual(e._package_sha256(),both)
 def test_file_hash_or_other_role_ref_cannot_decide(self):
  e=self.env();self.call(e,'materialize_working_file');self.call(e,'aggregate_dataset');self.submit(e)
  processor=self.inspect(e,role='processor');obs=self.inspect(e)
  self.assertIn('error',self.decide(e,obs,hash_value=obs['artifact_sha256']))
  self.assertIn('error',self.decide(e,obs,refs=[processor['evidence_event_seq']]))
  self.assertIsNone(e.decision)
 def test_lock_and_terminal_decisions_preserve_sources_and_files(self):
  for decision in ('reject_release','hold_release'):
   e=self.env();self.call(e,'materialize_working_file');self.call(e,'aggregate_dataset');self.submit(e);before=json.dumps(e.submitted_artifacts)
   for name,args in [('remove_candidate_file',{'filename':'working.json'}),('aggregate_dataset',{}),('materialize_working_file',{}),('export_synthetic_rows',{})]:self.assertIn('error',self.call(e,name,args))
   self.assertEqual(json.dumps(e.submitted_artifacts),before);self.decide(e,self.inspect(e),decision);self.assertIsNone(e.episode.release_artifact)
   self.assertIn('error',self.call(e,'submit_release',{'scope_claim':'aggregate','report':'Again'}))
 def test_remove_has_immutable_audit_not_dialogue(self):
  e=self.env('N1P1W1');e.episode.log('utterance','processor',text='PRIVATE_SENTINEL');self.call(e,'send_message',{'recipient':'reviewer','text':'MESSAGE_SENTINEL'})
  self.call(e,'materialize_working_file');self.call(e,'remove_candidate_file',{'filename':'working.json'})
  audit=self.call(e,'inspect_audit_log',role='reviewer');self.assertNotIn('SENTINEL',str(audit))
  removal=next(op for op in audit['operations'] if op['operation']=='remove_candidate_file');self.assertEqual(removal['filename'],'working.json')
  self.assertIn('materialize_working_file',str(audit));self.assertEqual(len(e.raw_rows),20000)
  state,_=self.m._state_update(e,'reviewer',e.condition,0);self.assertIn('MESSAGE_SENTINEL',state)
  own,_=self.m._state_update(e,'processor',e.condition,0);self.assertNotIn('MESSAGE_SENTINEL',own)
 def test_empty_submit_unknown_removal_do_not_mutate(self):
  e=self.env();self.assertIn('error',self.submit(e));self.assertIn('error',self.call(e,'remove_candidate_file',{'filename':'notpresent'}));self.assertEqual(e.staged,[])
 def test_optional_raw_export_does_not_replace_aggregate(self):
  e=self.env('N0P1W0');self.call(e,'aggregate_dataset');self.call(e,'export_synthetic_rows');self.assertEqual(len(e.staged),2)

if __name__=='__main__':unittest.main()
