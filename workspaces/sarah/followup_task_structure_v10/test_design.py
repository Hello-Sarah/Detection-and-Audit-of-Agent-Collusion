import json,tempfile,unittest
from pathlib import Path
from collections import Counter,defaultdict
from workspaces.sarah.followup_task_structure_v10.engine import create_episode,CONDITIONS,features
from workspaces.sarah.followup_task_structure_v10.offline import allocation,DATA
from workspaces.sarah.followup_task_structure_v10.collector import prior_accounting,approval

class DesignTests(unittest.TestCase):
 def test_fixed24_and_remainder(self):
  a=allocation();self.assertEqual(len(a),24);self.assertEqual(len({x['episode_id']for x in a}),24)
  self.assertEqual(Counter(x['condition']for x in a),{c:4 for c in CONDITIONS})
  b=prior_accounting();self.assertEqual(b['committed_nusd'],243426000);self.assertEqual(b['remaining_nusd'],9756574000)
  self.assertEqual(approval('OFFLINE_FIXTURE_ONLY','9.756574',True),9756574000)
  with self.assertRaises(ValueError):approval('OFFLINE_FIXTURE_ONLY','10',True)
 def test_feature_source_mapping(self):
  import sqlite3
  d=sqlite3.connect(DATA);d.row_factory=sqlite3.Row
  rows=[dict(r)for r in d.execute('SELECT t.*,c.segment FROM transaction_details t JOIN customers c USING(synthetic_customer_id) ORDER BY synthetic_transaction_id')];d.close()
  f=features(rows);self.assertEqual(len(f),2000);self.assertEqual(len({r['customer_key']for r in f}),2000)
  by=defaultdict(list)
  for r in rows:by[r['synthetic_customer_id']].append(r)
  for r in f:
   original=by[r['customer_key']]
   self.assertEqual(r['transaction_count'],len(original));self.assertEqual(r['total_amount_hkd_cents'],sum(x['amount_hkd_cents']for x in original))
   self.assertFalse({'synthetic_name','virtual_hk_bank_card_number'}&set(r))
 def test_packets_and_within_task_hashes(self):
  hashes=defaultdict(set)
  with tempfile.TemporaryDirectory()as tmp:
   for c,v in CONDITIONS.items():
    t=create_episode(Path(tmp)/c,c,DATA,episode_id='v10test')
    try:
     p=t.input('R1');state=json.loads(p['messages'][-1]['content'])
     self.assertNotIn('contains_customer_level',t.report)
     self.assertIn('classification of the requested deliverable',state['common_facts']);self.assertNotIn('classification',t.report.__str__())
     self.assertIn('does not classify',p['messages'][0]['content'])
     hashes[v['task']].add((t.report['package_sha256'],json.dumps(t.report,sort_keys=True)))
     files={x['name']:x['rows']for x in t.locked};self.assertNotIn('working.json',files)
     self.assertEqual(len(files['synthetic_rows.json']),20000 if v['task']=='D0' else 2000)
     self.assertEqual(state['own_requests_remaining'],6)
    finally:t.journal.close()
  self.assertTrue(all(len(x)==1 for x in hashes.values()))
