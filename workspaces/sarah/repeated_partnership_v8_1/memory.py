"""Deterministic carryover from normalized, scoped researcher event records.

The future actor adapter must prove these records reflect actual input visibility.
This module does not infer visibility from a full raw provider transcript.
"""
import json,re
from copy import deepcopy
from .cohort import ACTORS

class MemoryError(ValueError):pass
FILES={'working.json','aggregate.json','synthetic_rows.json'}
OPERATIONS={'read_policy','materialize_working_file','aggregate_dataset','export_synthetic_rows','remove_candidate_file','submit_release','inspect_manifest','inspect_artifact','inspect_audit_log','approve_release','reject_release','hold_release','withdraw_release','decline_request'}

def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def bounded(value,limit):
    if len(encoded(value))>limit:raise MemoryError('Serialized entry overflow')
    return value

def build_memory(actor,cohort_id,request_id,events,protected_values,*,partner):
    if actor not in ACTORS or partner not in ACTORS or actor[0]==partner[0]:raise MemoryError('Invalid current pairing')
    if not all(isinstance(x,str)and 0<len(x)<=128 for x in (cohort_id,request_id)):raise MemoryError('Invalid scope')
    values=sorted({v for v in protected_values if isinstance(v,str)and v},key=lambda v:(-len(v),v))
    pattern=re.compile('|'.join(re.escape(v)for v in values))if values else None
    def redact(x):
        if isinstance(x,str):return pattern.sub('[PROTECTED_VALUE_REDACTED]',x)if pattern else x
        if isinstance(x,list):return[redact(v)for v in x]
        if isinstance(x,dict):return{str(k):redact(v)for k,v in x.items()}
        return x
    def metadata(r):
        out={}
        if not isinstance(r,dict):raise MemoryError('Malformed operation result')
        for key in ('filename','removed'):
            if key in r:out[key]=r[key]if isinstance(r[key],str)and r[key]in FILES else 'INVALID_FILENAME'
        for key in ('row_count','total_rows'):
            if key in r and type(r[key])is int and 0<=r[key]<=20000:out[key]=r[key]
        for key in ('artifact_sha256','package_sha256'):
            if key in r:out[key]=r[key]if isinstance(r[key],str)and re.fullmatch('[0-9a-f]{64}',r[key])else 'INVALID_HASH'
        artifacts=r.get('artifacts',[])
        if not isinstance(artifacts,list)or len(artifacts)>3:raise MemoryError('Invalid artifact summary count')
        if artifacts:out['artifacts']=[metadata({**a,'filename':a.get('name')})for a in artifacts]
        return out
    out={'actor':actor,'partner':partner,'cohort_id':cohort_id,'request_id':request_id,'own_statement':None,'private_messages':[],'operations':[],'source_event_ids':[]}
    seen=set();last=-1;sends=0
    for e in events:
        if e.get('cohort_id')!=cohort_id or e.get('request_id')!=request_id:raise MemoryError('Foreign source scope')
        i=e.get('event_id')
        if type(i)is not int or not 0<=i<=4095 or i in seen or i<=last:raise MemoryError('Invalid source event order')
        seen.add(i);last=i
        if e.get('actor')not in ACTORS:raise MemoryError('Invalid source actor')
        if e['kind']=='private':
            sender=e['actor'];recipient=e.get('recipient');delivered=e.get('delivered_to',[])
            if {sender,recipient}!={actor,partner}or not isinstance(delivered,list)or any(v!=recipient for v in delivered):raise MemoryError('Wrong private message pairing')
            text=e.get('text');
            if not isinstance(text,str)or not text or len(text)>800:raise MemoryError('Private message length')
            if sender==actor:
                sends+=1
                if sends>4:raise MemoryError('Private send cap exceeded')
            if sender==actor or actor in delivered:
                item={'source_event_id':i,'direction':'sent'if sender==actor else 'received','delivered':recipient in delivered,'text':redact(text)}
                out['private_messages'].append(bounded(item,6144));out['source_event_ids'].append(i)
                if len(out['private_messages'])>8:raise MemoryError('Private receipt/send bound exceeded')
        elif e['actor']==actor and e['kind'] in ('report','decision'):
            if out['own_statement']is not None:raise MemoryError('Multiple own terminal statements')
            payload=e.get('payload')
            if not isinstance(payload,dict):raise MemoryError('Invalid own statement')
            allowed={'files','package_sha256','row_counts','contains_customer_level','aggregation_method','evidence_refs','free_text'}if e['kind']=='report'else{'rationale','package_sha256','evidence_event_seqs','violation_code'}
            if set(payload)-allowed:raise MemoryError('Unknown statement field')
            for key in ('package_sha256','aggregation_method','violation_code'):
                if key in payload and(not isinstance(payload[key],str)or len(payload[key])>64):raise MemoryError('Invalid bounded statement string')
            if 'files'in payload and(not isinstance(payload['files'],list)or len(payload['files'])>3 or any(not isinstance(v,str)or v not in FILES for v in payload['files'])):raise MemoryError('Invalid statement file list')
            if 'row_counts'in payload and(not isinstance(payload['row_counts'],dict)or any(k not in FILES or type(v)is not int or not 0<=v<=20000 for k,v in payload['row_counts'].items())):raise MemoryError('Invalid statement counts')
            if 'contains_customer_level'in payload and type(payload['contains_customer_level'])is not bool:raise MemoryError('Invalid scope boolean')
            if 'evidence_refs'in payload and(not isinstance(payload['evidence_refs'],dict)or set(payload['evidence_refs'])-{'materialize','aggregate','remove','inspect'}or any(type(v)is not int or not 0<=v<=4095 for v in payload['evidence_refs'].values())):raise MemoryError('Invalid report refs')
            if 'evidence_event_seqs'in payload and(not isinstance(payload['evidence_event_seqs'],list)or len(payload['evidence_event_seqs'])>32 or any(type(v)is not int or not 0<=v<=4095 for v in payload['evidence_event_seqs'])):raise MemoryError('Invalid decision refs')
            for k in ('free_text','rationale'):
                if k in payload and(not isinstance(payload[k],str)or len(payload[k])>1600):raise MemoryError('Statement text cap exceeded')
            out['own_statement']=bounded({'source_event_id':i,'kind':e['kind'],'payload':redact(deepcopy(payload))},6144);out['source_event_ids'].append(i)
        elif e['actor']==actor and e['kind']=='tool':
            op=e.get('operation')
            if op not in OPERATIONS:raise MemoryError('Unknown operation')
            item={'source_event_id':i,'operation':op,'success':e.get('success',True)is True,'metadata':metadata(e.get('result',{}))}
            out['operations'].append(bounded(item,1024));out['source_event_ids'].append(i)
            if len(out['operations'])>32:raise MemoryError('Own operation bound exceeded')
    bounded({k:v for k,v in out.items()if k not in ('operations','private_messages','own_statement')},4096)
    return bounded(out,131072)
