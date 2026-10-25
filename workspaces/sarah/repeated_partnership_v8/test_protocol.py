from copy import deepcopy
import json
import unittest
from workspaces.sarah.repeated_partnership_v8.protocol import (MODEL, ProtocolError, build_request, parse_response, serialized_token_estimate)


def response(content='hello',calls=None,finish='stop',prompt=10,completion=2):
    return {'model':'gpt-5-mini-2025-08-07','choices':[{'index':0,'finish_reason':finish,
            'message':{'role':'assistant','content':content,'tool_calls':calls,'refusal':None}}],
            'usage':{'prompt_tokens':prompt,'completion_tokens':completion,'total_tokens':prompt+completion}}


def tool_call(arguments='{}',call_id='original-call'):
    return {'id':call_id,'type':'function','function':{'name':'read_policy','arguments':arguments}}


def actor_input():
    return {'actor':'P1','request_id':'q','messages':[{'role':'system','content':'policy'},{'role':'user','content':'buyer'}],
            'tools':[{'type':'function','function':{'name':'read_policy','parameters':{'type':'object','properties':{}}}}]}


class ProtocolTests(unittest.TestCase):
    def test_request_bytes_detached_and_all_budget_fields_pinned(self):
        source=actor_input();prepared=build_request(source)
        source['messages'][1]['content']='mutated';source['tools'].clear()
        body=json.loads(prepared.body)
        self.assertEqual(body['messages'][1]['content'],'buyer')
        self.assertEqual(body['tools'][0]['function']['name'],'read_policy')
        self.assertEqual((body['model'],body['max_completion_tokens'],body['n'],body['service_tier']),(MODEL,4096,1,'default'))
        self.assertFalse(body['stream']);self.assertFalse(body['store'])
        self.assertNotIn('actor',body)

    def test_original_call_ids_and_tool_arguments_preserved(self):
        raw=response(None,[tool_call('{"filename":"aggregate.json"}')],'tool_calls')
        before=deepcopy(raw);parsed=parse_response(raw)
        self.assertEqual(parsed.calls,[{'name':'read_policy','arguments':{'filename':'aggregate.json'}}])
        self.assertEqual(parsed.call_ids,['original-call'])
        self.assertEqual(parsed.raw,before)
        self.assertEqual(raw,before)
        raw['choices'][0]['message']['tool_calls'].clear()
        self.assertEqual(len(parsed.calls),1)

    def test_invalid_generated_json_is_not_repaired_into_tool_action(self):
        for args in ('{bad','[]','{"x":1,"x":2}','{"x":NaN}'):
            parsed=parse_response(response(None,[tool_call(args)],'tool_calls'))
            self.assertEqual(parsed.calls[0]['arguments'],'INVALID_JSON_OBJECT')
            self.assertEqual(parsed.raw['choices'][0]['message']['tool_calls'][0]['function']['arguments'],args)

    def test_truncated_and_refusal_return_no_calls_or_invented_text(self):
        raw=response(None,[tool_call('{')],'length')
        parsed=parse_response(raw)
        self.assertEqual(parsed.status,'length');self.assertEqual(parsed.calls,[]);self.assertEqual(parsed.content,'')
        raw=response(None);raw['choices'][0]['message']['refusal']='Cannot comply'
        parsed=parse_response(raw)
        self.assertEqual(parsed.status,'refusal');self.assertEqual(parsed.refusal,'Cannot comply');self.assertEqual(parsed.calls,[])

    def test_envelope_validation_stops_instead_of_guessing(self):
        invalid=[]
        r=response();r['model']='different-model';invalid.append(r)
        r=response();r['choices'].append(deepcopy(r['choices'][0]));invalid.append(r)
        r=response();r['choices'][0]['message']['role']='user';invalid.append(r)
        r=response();r['choices'][0]['finish_reason']='unknown';invalid.append(r)
        r=response(None,[tool_call(),tool_call()],'tool_calls');invalid.append(r)
        r=response(None,[{'id':'a','type':'function','function':{}}],'tool_calls');invalid.append(r)
        r=response(None,None,'tool_calls');invalid.append(r)
        for r in invalid:
            with self.assertRaises(ProtocolError):parse_response(r)

    def test_usage_exact_types_bounds_and_reasoning(self):
        changes=[('prompt_tokens',True),('prompt_tokens',-1),('completion_tokens',4097),('total_tokens',999)]
        for key,value in changes:
            r=response();r['usage'][key]=value
            with self.assertRaises(ProtocolError):parse_response(r)
        r=response();del r['usage']
        with self.assertRaises(ProtocolError):parse_response(r)
        r=response(completion=4096);r['usage']['completion_tokens_details']={'reasoning_tokens':4090}
        self.assertEqual(parse_response(r).completion_tokens,4096)

    def test_estimator_never_claims_provider_billing_count(self):
        prepared=build_request(actor_input())
        try:estimate=serialized_token_estimate(prepared)
        except RuntimeError as exc:self.assertIn('TOKENIZER_UNAVAILABLE',str(exc))
        else:
            self.assertFalse(estimate['usable_as_hard_bound'])
            self.assertEqual(estimate['provider_prompt_tokens'],'unverified')

if __name__=='__main__':unittest.main()
