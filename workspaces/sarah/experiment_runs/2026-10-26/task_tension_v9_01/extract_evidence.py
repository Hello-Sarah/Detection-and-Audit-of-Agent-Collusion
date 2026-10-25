"""Posthoc mechanical extract, not semantic adjudication; no network."""
import json,re,hashlib,sys
from pathlib import Path
p=Path(sys.argv[1]);s=json.loads((p/'summary.json').read_text());items=[]
for row in s['episodes']:
 root=p/row['episode_id']
 if not (root/'trajectory.jsonl').exists():
  items.append({'episode_id':row['episode_id'],'condition':row['condition'],'state':row['state'],'semantic_review_status':'unreviewed'});continue
 events=[json.loads(l)for l in(root/'trajectory.jsonl').read_text().splitlines()]
 inputs=[e for e in events if e['kind']=='api_input']
 decisions=[{'event_id':e['event_id'],**e['payload']}for e in events if e['kind']=='tool_call' and e['payload'].get('actor')=='R1' and e['payload']['operation']in('approve_release','reject_release','hold_release')]
 replies=[{'event_id':e['event_id'],**e['payload']}for e in events if e['kind']=='private' and e['payload']['actor']=='R1']
 script=[{'event_id':e['event_id'],**e['payload']}for e in events if e['kind']=='private' and e['payload']['actor']=='P1']
 candidates=[]
 for e in events:
  if e['kind']!='model_response':continue
  texts=[e['payload'].get('content','')]+[x['arguments'].get('rationale','')for x in e['payload']['calls']if isinstance(x.get('arguments'),dict)]
  for text in texts:
   for kind,pattern in [('first_person_materialization',r'\bI\b[^.!?]{0,100}\b(?:materialized|created)\b'),('first_person_computation',r'\bI\b[^.!?]{0,100}\b(?:computed|calculated|counted|validated|verified)\b')]:
    for m in re.finditer(pattern,text):candidates.append({'model_response_event_id':e['event_id'],'pattern':kind,'verbatim_excerpt':text[max(0,m.start()-20):min(len(text),m.end()+180)],'status':'regex candidate only; context and provenance require review'})
 released=json.loads((root/'released_files.json').read_text());terminal=json.loads((root/'terminal_record.json').read_text())
 items.append({'episode_id':row['episode_id'],'condition':row['condition'],'factors':row.get('condition_factors'),
  'source_jsonl_sha256':hashlib.sha256((root/'trajectory.jsonl').read_bytes()).hexdigest(),
  'initial_input_confirmed':row['initial_input_confirmed'],'initial_script_messages':script,
  'script_message_delivery_inputs':[{'api_input_event_id':e['event_id'],'delivered_private_event_ids':e['payload']['delivered_private_event_ids']}for e in inputs if e['payload']['delivered_private_event_ids']],
  'reviewer_private_messages':replies,'decision_attempts':decisions,
  'terminal':row['terminal'],'released_file_rows':{k:len(v)for k,v in released.items()},
  'actual_protected_rows_released':row.get('protected_rows_released',0),
  'tool_errors':[{'event_id':e['event_id'],**e['payload']}for e in events if e['kind']=='tool_result'and e['payload'].get('actor')=='R1'and not e['payload']['success']],
  'process_statement_candidates':candidates,'verbal_acceptance_annotation':None,'false_scope_annotation':None,
  'coordination_interpretation':None,'annotator_disagreement':None,'human_label':None,'semantic_review_status':'unreviewed',
  'v9_mechanical_business_record':row.get('v9_business_record'),'legacy_points_not_v9_score':terminal.get('points')})
(p/'EVIDENCE_TABLE_DRAFT.json').write_text(json.dumps({'status':'mechanical extraction with unreviewed text candidates, not reference labels','axes_spec':'workspaces/sarah/task_tension_v9/EVIDENCE_RULES.md','episodes':items},ensure_ascii=False,indent=2)+'\n')
print('Extracted',len(items),'episodes; semantic/human annotations remain null.')
