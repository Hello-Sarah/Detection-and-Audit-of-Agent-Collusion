import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
from . import collector

class ClaimTests(unittest.TestCase):
 def test_same_manifest_cannot_start_in_another_output_directory(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp);manifest=p/'EXECUTION_MANIFEST.json';manifest.write_text('{}')
   fn=getattr(collector,'claim_live_run',None);self.assertTrue(callable(fn),'one-time execution claim missing')
   fn(manifest,p/'first','human-approval-reference')
   with self.assertRaises(FileExistsError):fn(manifest,p/'second','human-approval-reference')
   data=json.loads((p/'LIVE_CLAIM.json').read_text())
   self.assertEqual(data['output'],str((p/'first').resolve()))
   self.assertEqual(data['status'],'claimed_no_automatic_retry')
 def test_stale_or_wrong_pricing_blocks_live_gate(self):
  for age,rate in [(25,250),(0,251)]:
   pricing={'checked_utc':(datetime.now(timezone.utc)-timedelta(hours=age)).isoformat(),'input_nusd_per_token':rate,'output_nusd_per_token':2000}
   with self.assertRaises(ValueError):collector._pricing_live({'pricing':pricing})

if __name__=='__main__':unittest.main()
