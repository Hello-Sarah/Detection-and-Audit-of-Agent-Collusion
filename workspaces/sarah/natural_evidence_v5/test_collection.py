import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import collect

class CollectionStopTests(unittest.TestCase):
    def test_malformed_protocol_stops_after_preserving_first_slot(self):
        for kind in ('invalid_json','missing_message'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                folder=Path(temp)
                config=collect.config('gpt-5-mini-2025-08-07','N0P0')
                m={'source_and_data_sha256':{},'prior_completed_raw_sha256':{},'configurations':{'N0P0':config},'base_url':'https://api.openai.com/v1','schedule':[{'file':f'{i:02d}.jsonl','condition':'N0P0'} for i in (1,2)]}
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

if __name__=='__main__':unittest.main()
