"""Pure Chat Completions protocol. No client, credentials or network calls."""
from dataclasses import dataclass
import hashlib
import json

MODEL='gpt-5-mini-2025-08-07'
INPUT_RESERVE_TOKENS=400000
OUTPUT_CAP=4096


class ProtocolError(ValueError):pass


def canonical(value):
    try:return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode('utf-8')
    except (TypeError,ValueError,UnicodeError)as exc:raise ProtocolError('INVALID_FINITE_JSON')from None


@dataclass(frozen=True)
class PreparedRequest:
    body:bytes
    sha256:str


@dataclass(frozen=True)
class ParsedResponse:
    content:str
    calls:list
    call_ids:list
    status:str
    refusal:str|None
    prompt_tokens:int
    completion_tokens:int
    raw:dict


def build_request(actor_input):
    # The immutable byte buffer, not the original mutable histories, is what a
    # future transport must send and what reservation provenance hashes.
    source=json.loads(canonical(actor_input))
    messages=source.get('messages');tools=source.get('tools')
    if not isinstance(messages,list)or not messages or not isinstance(tools,list):raise ProtocolError('INVALID_REQUEST_INPUT')
    for message in messages:
        if not isinstance(message,dict)or message.get('role')not in ('system','user','assistant','tool'):
            raise ProtocolError('INVALID_REQUEST_MESSAGE')
        if message.get('content')is not None and not isinstance(message['content'],str):raise ProtocolError('TEXT_ONLY_REQUEST')
        if message['role']=='tool'and(not isinstance(message.get('content'),str)or not isinstance(message.get('tool_call_id'),str)):
            raise ProtocolError('INVALID_TOOL_MESSAGE')
    for tool in tools:
        if not isinstance(tool,dict)or tool.get('type')!='function'or not isinstance(tool.get('function'),dict):
            raise ProtocolError('FUNCTION_TOOLS_ONLY')
    body=canonical({'model':MODEL,'messages':messages,'tools':tools,'tool_choice':'auto',
                    'n':1,'max_completion_tokens':OUTPUT_CAP,'stream':False,'store':False,'service_tier':'default'})
    return PreparedRequest(body,hashlib.sha256(body).hexdigest())


def _int(value,maximum):return type(value)is int and 0<=value<=maximum


def _unique_object(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise ValueError('Duplicate JSON key')
        out[key]=value
    return out


def _arguments(raw):
    try:
        value=json.loads(raw,object_pairs_hook=_unique_object,
                         parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Non-finite JSON')))
        if not isinstance(value,dict):raise ValueError('Object required')
        canonical(value)
        return value
    except (ValueError,TypeError,UnicodeError):return 'INVALID_JSON_OBJECT'


def parse_response(response):
    raw=json.loads(canonical(response))
    if not isinstance(raw,dict)or raw.get('model')!=MODEL:raise ProtocolError('RESPONSE_MODEL_MISMATCH')
    if raw.get('service_tier')not in (None,'default'):raise ProtocolError('RESPONSE_TIER_MISMATCH')
    choices=raw.get('choices')
    if not isinstance(choices,list)or len(choices)!=1 or not isinstance(choices[0],dict):raise ProtocolError('INVALID_CHOICES')
    choice=choices[0]
    if type(choice.get('index'))is not int or choice['index']!=0:raise ProtocolError('INVALID_CHOICE_INDEX')
    finish=choice.get('finish_reason')
    if finish not in ('stop','tool_calls','length','content_filter'):raise ProtocolError('INVALID_FINISH_REASON')
    message=choice.get('message')
    if not isinstance(message,dict)or message.get('role')!='assistant':raise ProtocolError('INVALID_ASSISTANT_MESSAGE')
    content=message.get('content');refusal=message.get('refusal')
    if content is not None and not isinstance(content,str)or refusal is not None and not isinstance(refusal,str):
        raise ProtocolError('INVALID_ASSISTANT_TEXT')
    tool_calls=message.get('tool_calls')
    if tool_calls is not None and not isinstance(tool_calls,list):raise ProtocolError('INVALID_TOOL_CALL_LIST')
    usage=raw.get('usage')
    if not isinstance(usage,dict):raise ProtocolError('MISSING_USAGE')
    prompt=usage.get('prompt_tokens');completion=usage.get('completion_tokens');total=usage.get('total_tokens')
    if not _int(prompt,INPUT_RESERVE_TOKENS)or not _int(completion,OUTPUT_CAP)or type(total)is not int or total!=prompt+completion:
        raise ProtocolError('INVALID_USAGE')
    for key,field,limit in [('prompt_tokens_details','cached_tokens',prompt),('completion_tokens_details','reasoning_tokens',completion)]:
        details=usage.get(key)
        if details is not None and(not isinstance(details,dict)or field in details and not _int(details[field],limit)):
            raise ProtocolError('INVALID_USAGE_DETAILS')
    status='refusal'if refusal else finish
    calls=[];ids=[]
    if status not in ('length','refusal','content_filter'):
        if bool(tool_calls)!=(finish=='tool_calls'):raise ProtocolError('TOOL_FINISH_MISMATCH')
        if not content and not tool_calls:raise ProtocolError('EMPTY_RESPONSE')
        for call in tool_calls or []:
            if not isinstance(call,dict)or call.get('type')!='function'or not isinstance(call.get('function'),dict):
                raise ProtocolError('INVALID_TOOL_CALL')
            call_id=call.get('id');function=call['function']
            if not isinstance(call_id,str)or not 0<len(call_id)<=256 or call_id in ids:
                raise ProtocolError('INVALID_TOOL_CALL_ID')
            if not isinstance(function.get('name'),str)or not function['name']or not isinstance(function.get('arguments'),str):
                raise ProtocolError('INVALID_TOOL_FUNCTION')
            ids.append(call_id);calls.append({'name':function['name'],'arguments':_arguments(function['arguments'])})
    return ParsedResponse(content or '',calls,ids,status,refusal,prompt,completion,raw)


def serialized_token_estimate(prepared):
    """Local JSON-token measurement only, never an invoice or hard prompt bound."""
    try:
        import tiktoken
        encoding=tiktoken.encoding_for_model(MODEL)
    except (ImportError,KeyError):raise RuntimeError('TOKENIZER_UNAVAILABLE: exact model encoding required')from None
    return {'serialized_body_tokens':len(encoding.encode(prepared.body.decode('utf-8'))),
            'encoding':encoding.name,'provider_prompt_tokens':'unverified','usable_as_hard_bound':False}
