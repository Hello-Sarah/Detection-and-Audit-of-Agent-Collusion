"""Actual CLI-completion provenance and bounded JSON mediated actions."""
import hashlib
import json

class BridgeError(ValueError):pass

def packet_digest(packet):
    return hashlib.sha256(json.dumps(packet,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def _object(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise BridgeError('DUPLICATE_JSON_KEY')
        out[key]=value
    return out

def _constant(value):raise BridgeError('NONFINITE_JSON')

def parse_completion(events):
    if not isinstance(events,list)or not events:raise BridgeError('NO_CLI_EVENTS')
    threads=[];started=0;completed=[];messages=[]
    for event in events:
        if not isinstance(event,dict):raise BridgeError('INVALID_CLI_EVENT')
        kind=event.get('type')
        if kind=='thread.started':threads.append(event.get('thread_id'))
        elif kind=='turn.started':started+=1
        elif kind=='turn.completed':completed.append(event)
        elif kind in ('item.started','item.updated','item.completed'):
            item=event.get('item',{})
            if item.get('type')not in ('agent_message','reasoning'):raise BridgeError('NATIVE_TOOL_OR_UNKNOWN_ITEM')
            if kind=='item.completed'and item.get('type')=='agent_message':messages.append(item.get('text'))
        else:raise BridgeError('FAILED_OR_UNKNOWN_CLI_EVENT')
    if len(threads)!=1 or not isinstance(threads[0],str)or not threads[0]or started!=1 or len(completed)!=1 or events[-1].get('type')!='turn.completed' or len(messages)!=1:
        raise BridgeError('INCOMPLETE_OR_DUPLICATE_COMPLETION')
    usage=completed[0].get('usage')
    if not isinstance(usage,dict)or any(type(usage.get(k))is not int or usage[k]<0 for k in ('input_tokens','output_tokens')):
        raise BridgeError('INVALID_USAGE')
    text=messages[0]
    if not isinstance(text,str)or len(text)>32000:raise BridgeError('INVALID_FINAL_TEXT')
    try:out=json.loads(text,object_pairs_hook=_object,parse_constant=_constant)
    except (ValueError,TypeError):raise BridgeError('INVALID_FINAL_JSON')from None
    if not isinstance(out,dict)or set(out)!={'content','calls'} or not isinstance(out['content'],str)or len(out['content'])>1600 or not isinstance(out['calls'],list)or len(out['calls'])>4:
        raise BridgeError('INVALID_ACTION_ENVELOPE')
    for call in out['calls']:
        if not isinstance(call,dict)or set(call)!={'name','arguments'}or not isinstance(call['name'],str)or not isinstance(call['arguments'],dict):raise BridgeError('INVALID_MEDIATED_CALL')
    return out['content'],out['calls'],dict(usage)

def confirm_and_apply(task,actor,payload_hash,call_id,events):
    if task.poisoned or task.terminal or actor!=task.awaiting or task._provider_call!=call_id or task._pending_input is None:
        raise BridgeError('WRONG_OR_TERMINAL_ACTOR_INPUT')
    candidates=[e for e in task.journal.events()if e['kind']=='api_input'and e['request_id']==task.request_id and e['payload'].get('call_id')==call_id]
    if len(candidates)!=1 or candidates[0]['payload'].get('actor')!=actor or candidates[0]['payload'].get('payload_sha256')!=payload_hash:
        raise BridgeError('PACKET_IDENTITY_MISMATCH')
    content,calls,usage=parse_completion(events)
    task._log('provider_response',actor=actor,call_id=call_id,confirmed=True,
              transport='codex_subscription_cli',raw={'cli_events':events},usage=usage)
    received=set(task._pending_input['payload']['delivered_private_event_ids'])
    for message in task.private:
        if message['event_id']in received:message['delivered']=True
    return task.respond(actor,content,calls)
