"""Posthoc partial evidence snapshot; never calls API or changes raw/human files."""
from pathlib import Path
import hashlib,json,shutil,sys,tempfile
import audit_evidence
BASE=Path(__file__).resolve().parents[3]/'workspaces/sarah/experiment_runs/2026-10-25'
def checkpoint(name,notes_path):
 folder=BASE/name;manifest=json.loads((folder/'frozen_manifest.json').read_text());notes=json.loads(Path(notes_path).read_text())
 done=[item for item in manifest['schedule'] if (folder/item['file']).exists()]
 assert done and set(notes)=={item['file'] for item in done},'Read and note every completed raw episode, including explicit empty notes, before snapshot.'
 rows=[]
 for item in done:
  p=folder/item['file'];ep=json.loads(p.read_text());rows.append({'file':p.name,'episode_id':ep['episode_id'],'condition':ep['condition'],'source_jsonl_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'human_label':None,'qualifications':notes[p.name]})
 # Audit an exclusive temporary prefix copy; never alter the prospectively frozen allocation.
 with tempfile.TemporaryDirectory() as temp:
  out=Path(temp);prefix={**manifest,'schedule':done};(out/'frozen_manifest.json').write_text(json.dumps(prefix))
  (out/'human_review.json').write_text(json.dumps({'episodes':[{'human_label':None} for _ in done]}))
  for item in done:shutil.copyfile(folder/item['file'],out/item['file'])
  audit_evidence.audit(out);checks=json.loads((out/'evidence_integrity_checks.json').read_text())
 checks['status']='Partial completed prefix only; full allocation not yet checked';checks['original_allocated']=len(manifest['schedule']);checks['actual_human_worksheet']='Not created or changed by this helper; final full worksheet checked after collector completes.'
 (folder/'integrity_progress.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
 (folder/'ai_review_progress.json').write_text(json.dumps({'status':'Partial raw-first AI notes; not ground truth; independent crosscheck separately recorded in ledger; final review pending','episodes':rows},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'observed':len(rows),'allocated':len(manifest['schedule']),'api_requests':sum(r['api_requests'] for r in checks['episodes'])}))
if __name__=='__main__':checkpoint(sys.argv[1],sys.argv[2])
