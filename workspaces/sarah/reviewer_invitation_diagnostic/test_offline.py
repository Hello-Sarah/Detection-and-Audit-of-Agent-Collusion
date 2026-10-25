import hashlib,json,tempfile,unittest
from pathlib import Path
from collections import Counter
from .offline import allocation,generate

class OfflineTests(unittest.TestCase):
 def test_reproducible_balanced_allocation(self):
  rows=allocation();self.assertEqual(rows,allocation())
  self.assertEqual(len({r['episode_id']for r in rows}),16)
  self.assertEqual(Counter(r['condition']for r in rows),dict.fromkeys(('C0','C1','C2','C3'),4))
  for block in range(1,5):self.assertEqual({r['condition']for r in rows if r['block']==block},{'C0','C1','C2','C3'})
 def test_generated_gate_is_offline_only_and_hashes_exact_proposed_requests(self):
  with tempfile.TemporaryDirectory()as tmp:
   out=Path(tmp)/'proposed';gate=generate(out)
   self.assertEqual(gate['model_api_calls'],0)
   m=json.loads((out/'PROPOSED_MANIFEST.json').read_text())
   self.assertFalse(m['live_collection_approved']);self.assertFalse(m['cap_approved'])
   self.assertEqual(len(m['allocation']),16)
   self.assertEqual(len({m['stimulus_hashes'][c]['report_sha256']for c in ('C0','C1','C2')}),1)
   for r in m['allocation']:
    body=(out/r['initial_request_file']).read_bytes()
    self.assertEqual(hashlib.sha256(body).hexdigest(),r['initial_request_sha256'])
    state=json.loads(json.loads(body)['messages'][-1]['content'])
    self.assertEqual(state['request_id'],r['episode_id'])
    self.assertEqual(state['own_requests_remaining'],4)
   with self.assertRaises(FileExistsError):generate(out)

if __name__=='__main__':unittest.main()
