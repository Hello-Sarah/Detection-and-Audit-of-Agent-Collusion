"""Bounded technical-only launch. No calls without explicit approval and frozen inputs."""
import argparse
from decimal import Decimal,InvalidOperation
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import shlex
import sqlite3
import subprocess

from .budget import BudgetLedger,RESERVE_NUSD
from .coordinator import CohortAdapter
from .driver import Driver
from .journal import Journal
from .protocol import MODEL,canonical,serialized_token_estimate
from .transport import HTTPTransport

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
DATA=ROOT/'workspaces/sarah/datasets/synthetic_financial_v4_english/research.sqlite'
MANIFEST=BASE/'TECHNICAL_MANIFEST.json'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    files=sorted(BASE.glob('*.py'))+sorted(BASE.glob('requirements*.txt'))+[BASE/'DESIGN_DRAFT.md',BASE/'DESIGN_ZH.md',DATA]
    return {str(p.relative_to(ROOT)):sha(p)for p in files}


def validate_runtime():
    os.environ.setdefault('TIKTOKEN_CACHE_DIR',str(ROOT.parent/'v8-runtime/token-cache'))
    import tiktoken
    if version('tiktoken')!='0.12.0'or tiktoken.encoding_for_model(MODEL).name!='o200k_base':
        raise ValueError('Frozen tokenizer unavailable/mismatched')


def technical_cohorts():
    cohorts=[]
    for index,condition in enumerate(('S1F1','S0F0'),1):
        ids=[f'v8tech{index}_{x}'for x in ('a','b','c','d')]
        order=[ids[i]for i in ((1,0,2,3)if index==1 else(0,1,3,2))]
        cohorts.append({'cohort_id':f'v8tech{index}','condition':condition,'request_ids':ids,'execution_order':order})
    return cohorts


def freeze(path,readiness_path):
    readiness_path=Path(readiness_path).resolve()
    record=json.loads(readiness_path.read_text())
    if record.get('status')!='offline_pass'or record.get('model')!=MODEL or record.get('tokenizer_version')!='0.12.0'or record.get('encoding')!='o200k_base':
        raise ValueError('Passing offline readiness record required')
    cohorts=technical_cohorts()
    try:source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    except subprocess.CalledProcessError:raise ValueError('Git source identity required')from None
    manifest={'version':1,'run_type':'technical_only','model':MODEL,'max_deliveries':8,'max_requests':128,
              'max_completion_tokens':4096,'timeout_seconds':90,'serialized_input_token_guard':200000,
              'proposed_cap_usd':'15','conservative_token_ceiling_usd':str(Decimal(RESERVE_NUSD*128)/Decimal(10**9)),
              'require_explicit_approval':True,'formal_auto_start':False,'source_commit':source_commit,
              'source_and_data_sha256':source_hashes(),'readiness_file':str(readiness_path.relative_to(ROOT))if readiness_path.is_relative_to(ROOT)else str(readiness_path),
              'readiness_sha256':sha(readiness_path),'tokenizer_version':'0.12.0','encoding':'o200k_base','cohorts':cohorts}
    with Path(path).open('x',encoding='utf-8')as f:json.dump(manifest,f,ensure_ascii=False,indent=2);f.write('\n')
    return manifest


def verify_manifest(path=MANIFEST,*,check_runtime=True):
    manifest=json.loads(Path(path).read_text())
    if manifest.get('version')!=1 or manifest.get('run_type')!='technical_only'or manifest.get('model')!=MODEL:
        raise ValueError('Technical manifest model/version mismatch')
    expected={'max_deliveries':8,'max_requests':128,'max_completion_tokens':4096,'timeout_seconds':90,
              'serialized_input_token_guard':200000,'proposed_cap_usd':'15','require_explicit_approval':True,
              'formal_auto_start':False,'tokenizer_version':'0.12.0','encoding':'o200k_base','cohorts':technical_cohorts()}
    if any(canonical(manifest.get(k))!=canonical(v)for k,v in expected.items()):raise ValueError('Technical allocation/config changed')
    if manifest.get('source_and_data_sha256')!=source_hashes():raise ValueError('Frozen source/data changed')
    readiness=Path(manifest['readiness_file'])
    if not readiness.is_absolute():readiness=ROOT/readiness
    if sha(readiness)!=manifest.get('readiness_sha256'):raise ValueError('Readiness record changed')
    if check_runtime:validate_runtime()
    return manifest


def validate_approval(approval_ref,cap_usd):
    if not isinstance(approval_ref,str)or not approval_ref.strip()or len(approval_ref)>256:
        raise ValueError('Explicit human approval reference required')
    try:cap=Decimal(cap_usd)
    except (InvalidOperation,TypeError,ValueError):raise ValueError('Technical cap must be USD15')from None
    if not cap.is_finite()or cap!=15:raise ValueError('Technical cap must be USD15; revise plan before another amount')
    return int(cap*10**9)


def _settings():
    settings={}
    for line in (ROOT/'.env').read_text().splitlines():
        key,sep,value=line.strip().partition('=')
        if sep and key in ('OPENAI_API_KEY','OPENAI_MODEL','OPENAI_BASE_URL'):
            parts=shlex.split(value,comments=False,posix=True);settings[key]=parts[0]if parts else ''
    for key in ('OPENAI_API_KEY','OPENAI_MODEL','OPENAI_BASE_URL'):
        if key in os.environ:settings[key]=os.environ[key]
    if not settings.get('OPENAI_API_KEY')or settings.get('OPENAI_MODEL')!=MODEL or settings.get('OPENAI_BASE_URL','https://api.openai.com/v1').rstrip('/')!='https://api.openai.com/v1':
        raise ValueError('Exact model/official endpoint/key configuration required')
    return settings


def export_run(output,manifest,budget,*,run_type,failure,http_failure):
    episodes=[]
    for item in manifest['cohorts']:
        path=output/(item['cohort_id']+'.sqlite')
        snapshots={};journal_hash=None
        if path.exists():
            journal_hash=sha(path)
            db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
            try:
                snapshots={r['request_id']:dict(r)for r in db.execute('SELECT * FROM tasks')}
                trace=output/(item['cohort_id']+'.jsonl')
                with trace.open('x',encoding='utf-8')as stream:
                    for row in db.execute('SELECT * FROM events ORDER BY event_id'):
                        e=dict(row);e['payload']=json.loads(e['payload']);stream.write(json.dumps(e,ensure_ascii=False)+'\n')
            finally:db.close()
        for request in item['request_ids']:
            row=snapshots.get(request,{})
            episodes.append({'episode_id':request,'cohort_id':item['cohort_id'],'condition':item['condition'],
                             'state':row.get('state','unrun'),'terminal':row.get('terminal'),'mechanical_points':row.get('points'),
                             'label':'unreviewed','human_label':None,'source_journal_sha256':journal_hash})
    summary={'run_type':run_type,'status':'stopped'if failure else 'completed','failure':failure,'http_failure':http_failure,
             'episodes':episodes,'budget':budget.summary(),'formal_auto_start':False,
             'note':'Technical mechanical outcomes only, not semantic collusion labels. Pending/unrun slots retained; no replacements.'}
    with(output/'summary.json').open('x')as f:json.dump(summary,f,indent=2);f.write('\n')
    with(output/'human_review.json').open('x')as f:json.dump({'status':'unreviewed','episodes':episodes},f,indent=2);f.write('\n')
    return summary


def run_technical(manifest_path,output,*,approval_ref,cap_usd,_transport_fixture=None,_estimator_fixture=None):
    cap=validate_approval(approval_ref,cap_usd)
    fixture=_transport_fixture is not None
    if fixture and not approval_ref.startswith('OFFLINE_FIXTURE'):raise ValueError('Fixture mode must be labeled explicitly')
    if not fixture and approval_ref.startswith('OFFLINE'):raise ValueError('Fixture approval cannot launch live calls')
    manifest=verify_manifest(manifest_path,check_runtime=not fixture)
    output=Path(output).resolve()
    if not fixture:
        if not output.is_relative_to(ROOT/'workspaces/sarah/experiment_runs'):raise ValueError('Live evidence must stay in Sarah workspace')
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
        if not branch.startswith('sarah/'):raise ValueError('Sarah branch required')
        settings=_settings()
        transport=HTTPTransport(settings['OPENAI_API_KEY'])
        estimator=serialized_token_estimate
    else:transport=_transport_fixture;estimator=_estimator_fixture or serialized_token_estimate
    # Exclusive run directory prevents overwriting/resuming/replacing any slot.
    output.mkdir(parents=True,exist_ok=False)
    (output/'frozen_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    budget=BudgetLedger.create(output/'budget.sqlite',cap_nusd=cap,max_requests=manifest['max_requests'],approval_ref=approval_ref)
    failure=None;interrupted=None
    try:
        for item in manifest['cohorts']:
            verify_manifest(manifest_path,check_runtime=not fixture)
            journal=Journal.create(output/(item['cohort_id']+'.sqlite'),item['cohort_id'],item['condition'],
                                   hashlib.sha256(canonical(manifest)).hexdigest(),item['request_ids'])
            try:
                coordinator=CohortAdapter(journal,DATA,execution_order=item['execution_order'])
                driver=Driver(coordinator,budget,transport,estimator=estimator,
                              guard=lambda:verify_manifest(manifest_path,check_runtime=not fixture))
                driver.run()
            finally:journal.close()
    except BaseException as exc:
        failure=type(exc).__name__
        if not isinstance(exc,Exception):interrupted=exc
    finally:
        summary=export_run(output,manifest,budget,run_type='scripted_offline_fixture'if fixture else 'model_generated_technical',
                           failure=failure,http_failure=getattr(transport,'last_failure',None))
        budget.close()
    if interrupted is not None:raise interrupted
    return summary


def main():
    parser=argparse.ArgumentParser(description='V8 technical-only gate; no formal auto-start')
    sub=parser.add_subparsers(dest='command',required=True)
    f=sub.add_parser('freeze');f.add_argument('--readiness',required=True);f.add_argument('--manifest',default=str(MANIFEST))
    c=sub.add_parser('check');c.add_argument('--manifest',default=str(MANIFEST))
    r=sub.add_parser('run');r.add_argument('--manifest',default=str(MANIFEST));r.add_argument('--output',required=True)
    r.add_argument('--approval-ref',required=True);r.add_argument('--cap-usd',required=True)
    args=parser.parse_args()
    if args.command=='freeze':freeze(args.manifest,args.readiness);print('Technical manifest frozen; no API calls.')
    elif args.command=='check':verify_manifest(args.manifest);print('Source/data/tokenizer gate passed; approval still required.')
    else:
        summary=run_technical(args.manifest,args.output,approval_ref=args.approval_ref,cap_usd=args.cap_usd)
        print(json.dumps({'status':summary['status'],'episodes':len(summary['episodes']),'budget':summary['budget'],'http_failure':summary['http_failure']}))
        if summary['status']!='completed':raise SystemExit(1)

if __name__=='__main__':main()
