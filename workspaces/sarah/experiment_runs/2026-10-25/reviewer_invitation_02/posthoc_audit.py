"""Posthoc read-only integrity checks, not an agent prompt or semantic labeler."""
from pathlib import Path
from collections import Counter
import hashlib,json,sqlite3,sys
from workspaces.sarah.repeated_partnership_v8_1.protocol import canonical,parse_response
from workspaces.sarah.repeated_partnership_v8_1.adapter import confirmed_inputs
from workspaces.sarah.repeated_partnership_v8_1.scoring import load_source,package_hash
from workspaces.sarah.reviewer_invitation_v2.offline import digest
p=Path(sys.argv[1]);out=Path(sys.argv[2])
m=json.loads((p/'frozen_manifest.json').read_text());s=json.loads((p/'summary.json').read_text());hashes=json.loads((p/'evidence_hashes.json').read_text())
for rel,want in hashes.items():assert hashlib.sha256((p/rel).read_bytes()).hexdigest()==want,rel
source=load_source('workspaces/sarah/datasets/synthetic_financial_v4_english/research.sqlite')
db=sqlite3.connect((p/'budget.sqlite').resolve().as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
reservations={r['call_id']:dict(r)for r in db.execute('SELECT * FROM reservations')};db.close()
assert len(reservations)==s['budget']['request_count'] and all(r['state']=='settled'for r in reservations.values())
models=Counter();finishes=Counter();errors=Counter();operations=Counter();cached=0;reasoning=0;prompt=0;completion=0;items=[]
for row in s['episodes']:
 root=p/row['episode_id'];events=[json.loads(l)for l in(root/'trajectory.jsonl').read_text().splitlines()]
 assert len({e['event_id']for e in events})==len(events)
 inputs=[e for e in events if e['kind']=='api_input'];responses=[e for e in events if e['kind']=='provider_response'];outputs=[e for e in events if e['kind']=='model_response']
 assert len(inputs)==len(responses)==len(outputs)==len(list((root/'requests').glob('*.json')))
 assert len(inputs)<=4 and all(e['payload']['actor']=='R1'for e in inputs+responses+outputs)
 assert source.pattern.search(json.dumps(inputs[0]['payload']['messages']))is None
 assert len(confirmed_inputs(events))==len(inputs)
 assert inputs[0]['payload']['delivered_private_event_ids']
 assert hashlib.sha256((root/'requests/01.json').read_bytes()).hexdigest()==row['initial_request_sha256']
 private=[e for e in events if e['kind']=='private'and e['payload']['actor']=='P1'];assert len(private)==1 and private[0]['payload']['actor_kind']=='script'
 for index,(i,r,o)in enumerate(zip(inputs,responses,outputs),1):
  body=(root/f'requests/{index:02d}.json').read_bytes();payload=json.loads(body);assert payload['messages']==i['payload']['messages'];assert payload['tools']==i['payload']['tools']
  assert hashlib.sha256(body).hexdigest()==i['payload']['payload_sha256']==reservations[i['payload']['call_id']]['payload_sha256']
  assert canonical(r['payload']['raw'])==canonical(json.loads(reservations[i['payload']['call_id']]['raw_response']))
  parsed=parse_response(r['payload']['raw']);assert parsed.content==o['payload']['content']and parsed.calls==o['payload']['calls']
  raw=r['payload']['raw'];u=raw['usage'];prompt+=u['prompt_tokens'];completion+=u['completion_tokens'];cached+=u.get('prompt_tokens_details',{}).get('cached_tokens',0);reasoning+=u.get('completion_tokens_details',{}).get('reasoning_tokens',0);models[raw['model']]+=1;finishes[raw['choices'][0]['finish_reason']]+=1
 for e in events:
  v=e['payload']
  if e['kind']=='tool_call'and v.get('actor')=='R1':operations[v['operation']]+=1
  if e['kind']=='tool_result'and v.get('actor')=='R1'and not v['success']:errors[(v['operation'],v['result']['error'],v['result'].get('validation',{}).get('field'))]+=1
 locked=json.loads((root/'locked_files.json').read_text());released=json.loads((root/'released_files.json').read_text());report=json.loads((root/'locked_report.json').read_text())
 assert set(locked)==({'aggregate.json'}if row['condition']=='C3'else{'working.json','aggregate.json'})
 assert digest(report)==m['stimulus_hashes'][row['condition']]['report_sha256']
 assert package_hash([{'name':name,'rows':rows}for name,rows in locked.items()])==report['package_sha256']
 assert locked['aggregate.json']==list(source.aggregate_rows)
 if 'working.json'in locked:assert len(locked['working.json'])==20000
 assert released==locked if row['terminal']=='approved' else released=={}
 terminal=[e for e in events if e['kind']=='terminal'][-1];assert terminal['payload']['terminal']==row['terminal']
 decisions=[{'event_id':e['event_id'],'tool':e['payload']['operation'],'arguments':e['payload']['arguments']}for e in events if e['kind']=='tool_call'and e['payload'].get('actor')=='R1'and e['payload']['operation']in('approve_release','reject_release','hold_release')]
 assert row['approval_attempts']==sum(x['tool']=='approve_release' for x in decisions)
 if row['terminal']=='approved':
  own=set(inputs[-1]['payload']['consumed_event_ids'])
  ops=[e['payload'] for e in events if e['kind']=='tool_result' and e['payload'].get('actor')=='R1' and e['payload'].get('success') and e['event_id'] in own]
  assert any(x['operation']=='inspect_manifest' for x in ops)
  assert any(x['operation']=='inspect_audit_log' for x in ops)
  for name in locked: assert any(x['operation']=='inspect_artifact' and x.get('filename')==name and x.get('offset',0)==0 for x in ops)
 for i in inputs:
  state=json.loads(i['payload']['messages'][-1]['content'])
  assert state['eligible_decision_evidence_event_ids']==i['payload']['consumed_event_ids']
 items.append({'episode_id':row['episode_id'],'condition':row['condition'],'terminal':row['terminal'],'requests':len(inputs),'terminal_event_id':terminal['event_id'],'decision_attempts':decisions,'last_consumed_event_ids':inputs[-1]['payload']['consumed_event_ids']})
assert prompt*250+completion*2000==s['budget']['committed_nusd']
assert all(x['human_label']is None for x in json.loads((p/'human_review.json').read_text())['episodes'])
facts={'evidence_hashes_verified':len(hashes),'requests':len(reservations),'prompt_tokens':prompt,'completion_tokens':completion,'cached_prompt_tokens':cached,'reasoning_tokens_included_in_completion':reasoning,'models':dict(models),'finish_reasons':dict(finishes),'reviewer_tool_calls':dict(operations),'tool_errors':[{'operation':k[0],'error':k[1],'field':k[2],'count':v}for k,v in errors.items()],'conservative_uncached_token_cost_usd':s['budget']['committed_nusd']/1e9,'unknown_holds':0,'episodes':items,'raw_human_fields_unchanged':True,'annotation_status':'mechanical facts plus AI-assisted review; semantic human labels pending'}
out.write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in facts.items()if k!='episodes'},ensure_ascii=False,indent=2))
