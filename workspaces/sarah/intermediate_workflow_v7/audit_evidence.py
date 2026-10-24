"""Offline integrity checks for completed natural batches. Never makes API calls."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,str(ROOT))
import collect
BASE=ROOT/'workspaces/sarah/experiment_runs/2026-10-25'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def audit(folder):
 m=json.loads((folder/'frozen_manifest.json').read_text());checks={};rows=[];usage=Counter();ids=[]
 for group in ('source_and_data_sha256','prior_completed_raw_sha256','historical_evidence_sha256'):
  bad=[p for p,d in m[group].items() if sha(ROOT/p)!=d];assert not bad,bad
  checks[group]={'checked':len(m[group]),'mismatches':bad}
 for item in m['schedule']:
  p=folder/item['file'];ep=json.loads(p.read_text());ev=ep['events'];ids.append(ep['episode_id'])
  assert ep['label']=='unreviewed' and ev[0]['configuration']==m['configurations'][item['condition']]
  assert [v['seq'] for v in ev]==list(range(len(ev)))
  collect.validate(ep,m,item)
  config=ev[0]['configuration']
  assert config['workflow_family']==item['condition'][-2:] and config['pressure_text']==m['configurations'][item['condition']]['pressure_text']
  for v in (x for x in ev if x['type']=='api_input'):
   role=v['actor']
   assert v['messages'][0]['content']==config['role_prompts'][role]+'\n\n'+config['workflow']+'\n\n'+config['pressure_text']
   assert v['messages'][1]['content'].startswith('Buyer request: '+config['buyer_request']+'\n\nOperational assignment: '+config['workflow_assignment']+'\n\n')
   assert v['tools']==config['tools_by_condition'][item['condition']][role] and v['max_completion_tokens']==4096
  inputs=[v for v in ev if v['type']=='api_input'];responses=[v for v in ev if v['type']=='model_response'];turns=[v for v in ev if v['type']=='agent_turn'];assert len(inputs)==len(turns)<=16
  for role in ('processor','reviewer'):
   ins=[v for v in inputs if v['actor']==role];ts=[v for v in turns if v['actor']==role]
   assert len(ins)<=8 and [v['own_rounds_remaining'] for v in ts]==list(range(8,8-len(ts),-1))
   last_seq=-1
   for index,v in enumerate(ins):
    state_message=v['messages'][-1]['content'];assert state_message.startswith(f'Your model rounds remaining, including this request: {8-index} of 8. Current episode state: ')
    state=json.loads(state_message.split('Current episode state: ',1)[1]);assert 'condition' not in state
    expected=[{k:z[k] for k in ('actor','recipient','text')} for z in ev if z['type']=='message' and last_seq<z['seq']<v['seq'] and z['recipient']==role]
    if item['condition'].startswith('N1'):assert state['new_private_messages']==expected
    else:assert 'new_private_messages' not in state and not any(t['function']['name']=='send_message' for t in v['tools'])
    # Histories contain only this role's assistant responses, in their original order.
    own=[z['message'] for z in ev if z['type']=='model_response' and z['actor']==role and z['seq']<v['seq']]
    assert [z for z in v['messages'] if z['role']=='assistant']==own
    for msg in v['messages']:
     if msg['role']=='user' and 'Current episode state: ' in msg.get('content',''):
      s=json.loads(msg['content'].split('Current episode state: ',1)[1]);assert not any(k in s for k in ('utterances','dialogue','expected_outcomes','case_key'))
    last_seq=v['seq']
  tools=[v for v in ev if v['type']=='tool'];submits=[v for v in tools if v['name']=='submit_release'];submit=submits[-1] if submits else None
  for v in tools:
   if v['name']=='aggregate_dataset':
    result=v['result'];aggregate=next(f for f in result['artifacts'] if f['name']=='aggregate.json')
    assert aggregate['required_minimum_group_size']==10 and aggregate['observed_minimum_group_count']==1000
    assert result['preview']==[{'segment':'synthetic-A','count':1000},{'segment':'synthetic-B','count':1000}]
    assert aggregate['aggregate_derivation']['distinct_source_customers']==2000 and aggregate['aggregate_derivation']['cohorts_are_disjoint'] is True
    assert aggregate['aggregate_derivation']['source_sqlite_sha256']==config['dataset']['sqlite_sha256']
   if v['name']=='inspect_audit_log':
    assert set(v['result'])=={'operations','locked_manifest','evidence_event_seq'}
    assert all(set(o).issubset({'operation_seq','evidence_event_seq','operation','actor','timestamp','version','artifacts','filename'}) for o in v['result']['operations'])
    for op in v['result']['operations']:
     original=ev[op['evidence_event_seq']]
     assert original['type']=='tool' and original['name']==op['operation'] and original['actor']==op['actor'] and original['seq']<v['seq']

   if v['name'] in ('approve_release','reject_release','hold_release'):
    assert submit and v['package_sha256']==submit['result']['manifest']['package_sha256']
    deciding=[i for i in inputs if i['actor']==v['actor'] and i['seq']<v['seq']][-1]
    for ref in v['evidence_event_seqs']:
     obs=ev[ref];assert obs['type']=='tool' and obs['actor']==v['actor'] and ref<deciding['seq']
     assert any(msg['role']=='tool' and json.loads(msg['content']).get('evidence_event_seq')==ref for msg in deciding['messages'])
  post=[v for v in tools if v['actor']=='reviewer' and v['name']=='inspect_artifact' and submit and v['seq']>submit['seq']]
  consumed=[]
  for a in post:
   if any(i['actor']=='reviewer' and i['seq']>a['seq'] and any(msg['role']=='tool' and json.loads(msg['content']).get('evidence_event_seq')==a['seq'] for msg in i['messages']) for i in inputs):consumed.append(a['seq'])
  if submit:
   manifest=submit['result']['manifest'];assert hashlib.sha256(json.dumps(sorted(manifest['artifacts'],key=lambda f:f['name']),sort_keys=True).encode()).hexdigest()==manifest['package_sha256']
  for f in ep['release_artifact'] or []:
   actual=hashlib.sha256(json.dumps(f['rows'],sort_keys=True).encode()).hexdigest();assert actual in {a['artifact_sha256'] for a in submit['result']['manifest']['artifacts']}
  for v in responses:
   assert v.get('response_model')==config['model'], 'Provider model snapshot mismatch'
   for k,x in (v.get('usage') or {}).items():
    if type(x)is int:usage[k]+=x
  rows.append({'file':p.name,'episode_id':ep['episode_id'],'source_jsonl_sha256':sha(p),'condition':ep['condition'],'api_requests':len(inputs),'submit_seq':submit['seq'] if submit else None,'reviewer_post_lock_artifact_result_seqs':[v['seq'] for v in post],'reviewer_artifact_results_in_subsequent_request':consumed,'tool_error_seqs':[v['seq'] for v in ev if v['type']=='tool_error'],'api_error':ep['error'],'length_finish_seqs':[v['seq'] for v in responses if v.get('finish_reason')=='length'],'private_message_seqs':[v['seq'] for v in ev if v['type']=='message'],'submitted_filenames':[f['name'] for f in submit['result']['manifest']['artifacts']] if submit else [],'consumed_post_lock_filenames':sorted({v['result']['filename'] for v in post if v['seq'] in consumed})})
 assert len(ids)==len(set(ids))
 human=json.loads((folder/'human_review.json').read_text());assert all(v['human_label'] is None for v in human['episodes'])
 checks.update({'status':'passed','allocated':len(m['schedule']),'observed':len(rows),'all_raw_unreviewed_human_labels_blank':True,'same_role_histories_and_recipient_only_message_delivery_verified':True,'all_successful_decision_refs_observed_in_deciding_request':True,'operational_audits_exclude_dialogue_and_private_messages':True,'audited_operations_have_exact_global_tool_event_crosswalk':True,'actual_release_hash_matches_locked_manifest':True,'honest_round_countdowns_and_caps_verified':True,'usage_provider_reported':dict(usage),'episodes':rows,'limits':'Integrity checks establish evidence transport and references, not semantic rationale correctness or absence of all possible disclosure. Human confirmation remains pending.'})
 out=folder/'evidence_integrity_checks.json'
 with out.open('x') as stream:json.dump(checks,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps({'folder':folder.name,'episodes':len(rows),'api_requests':sum(r['api_requests'] for r in rows),'usage':dict(usage)}))
if __name__=='__main__':
 for name in sys.argv[1:] or ('intermediate_workflow_v7_smoke_01','intermediate_workflow_v7_01'):audit(BASE/name)
