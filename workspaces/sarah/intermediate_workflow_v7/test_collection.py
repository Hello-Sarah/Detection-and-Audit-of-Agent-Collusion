import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).parent))
import collect

class CollectionStopTests(unittest.TestCase):
    def test_malformed_protocol_stops_after_preserving_first_slot(self):
        for kind in ('invalid_json','missing_message'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                folder=Path(temp)
                config=collect.config('gpt-5-mini-2025-08-07','N0P1W0')
                m={'source_and_data_sha256':{},'prior_completed_raw_sha256':{},'configurations':{'N0P1W0':config},'base_url':'https://api.openai.com/v1','schedule':[{'file':f'{i:02d}.jsonl','condition':'N0P1W0'} for i in (1,2)]}
                (folder/'frozen_manifest.json').write_text(json.dumps(m))
                class Client:
                    api_key='DUMMY_TEST_ONLY';base_url='https://api.openai.com/v1';calls=0
                    def complete(self,*args):
                        self.calls+=1
                        if kind=='invalid_json':raise RuntimeError('Model API returned invalid JSON.')
                        return {'choices':[{}]}
                c=Client()
                with patch.object(collect,'prior_gate',lambda:None),patch.object(collect.runner,'client_from_environment',lambda:(c,'gpt-5-mini-2025-08-07')),patch.object(collect.runner,'BoundedClient',lambda client:client):
                    with self.assertRaisesRegex(RuntimeError,'Systemic failure'):
                        collect.collect(folder)
                self.assertEqual(c.calls,1)
                ep=json.loads((folder/'01.jsonl').read_text());self.assertIsNotNone(ep['error']);self.assertEqual(ep['label'],'unreviewed')
                self.assertFalse((folder/'02.jsonl').exists());self.assertFalse((folder/'01.in_progress.json').exists())

    def test_fixed_complete_blocks_and_repetitions(self):
        for smoke,count in ((True,6),(False,24)):
            rows=collect.schedule(smoke);self.assertEqual(len(rows),count)
            self.assertEqual(rows,collect.schedule(smoke))
            from collections import Counter
            self.assertEqual(set(Counter(r['condition'] for r in rows).values()),{1 if smoke else 4})
            for start in range(0,count,6):self.assertEqual({r['condition'] for r in rows[start:start+6]},set(collect.runner.CONDITIONS))

    def test_interrupted_slot_is_not_rerun(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);(folder/'01.in_progress.json').write_text('{}')
            c=type('Client',(),{'api_key':'DUMMY_TEST_ONLY','base_url':'https://api.openai.com/v1'})()
            m={'base_url':c.base_url,'configurations':{'N0P1W0':{'model':'gpt-5-mini-2025-08-07'}},'schedule':[{'condition':'N0P1W0','file':'01.jsonl'}]}
            with patch.object(collect,'prior_gate',lambda:None),patch.object(collect,'check',lambda folder:m),patch.object(collect.runner,'client_from_environment',lambda:(c,'gpt-5-mini-2025-08-07')),patch.object(collect.runner,'BoundedClient',lambda client:client):
                with self.assertRaisesRegex(RuntimeError,'Interrupted slot'):collect.collect(folder)
            self.assertFalse((folder/'01.jsonl').exists())

    def test_multi_file_release_validation_uses_exact_named_source(self):
        from dataclasses import asdict
        condition='N0P1W1';config=collect.config('gpt-5-mini-2025-08-07',condition)
        ep=collect.runner.Episode('validation',condition,'live',label='unreviewed');ep.log('task','harness',configuration=config)
        env=collect.runner._Environment(ep,condition)
        for name,args in [('materialize_working_file',{}),('aggregate_dataset',{}),('submit_release',{'scope_claim':'aggregate','report':'Counts'})]:env.run_tool('processor',condition,name,args)
        obs=env.run_tool('reviewer',condition,'inspect_artifact',{'filename':'working.json'})
        env.run_tool('reviewer',condition,'approve_release',{'rationale':'Bad test approval','evidence_event_seqs':[obs['evidence_event_seq']],'package_sha256':obs['package_sha256']})
        value=asdict(ep);m={'configurations':{condition:config}};item={'condition':condition}
        collect.validate(value,m,item)
        value['release_artifact'][0]['rows'][0]['synthetic_name']='MUTATED'
        with self.assertRaises(AssertionError):collect.validate(value,m,item)

if __name__=='__main__':unittest.main()
