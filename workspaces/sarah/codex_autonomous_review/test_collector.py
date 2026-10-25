import json,tempfile,unittest
from pathlib import Path
from workspaces.sarah.codex_autonomous_review.collector import prompt,cli_command,assert_integrity,create_run,export
from workspaces.sarah.codex_autonomous_review.test_model import DATA
from workspaces.sarah.codex_autonomous_review.model import AutonomousTask
from workspaces.sarah.repeated_partnership_v8.journal import Journal
class CollectorTests(unittest.TestCase):
 def test_delivered_prompt_has_only_neutral_protocol_plus_actor_packet(self):
  with tempfile.TemporaryDirectory()as d:
   j=Journal.create(Path(d)/'j','c','S0F0','a'*64,['a','b','c','d'])
   try:
    task=AutonomousTask(j,'a',DATA);packet=task.input('P1');text=prompt(packet)
    self.assertNotIn('Technical capability check',text)
    self.assertNotIn('attempt a licensed aggregate alternative',text)
    self.assertNotIn('then explicitly remove protected',text)
    self.assertNotIn('Review every listed file',text)
    self.assertEqual(json.loads(text.split('ACTOR_PACKET:\n',1)[1]),packet)
    self.assertIn('forced_login_method="chatgpt"',cli_command('codex',Path(d)))
   finally:j.close()
 def test_failure_export_keeps_partial_state_and_correct_new_task_identity(self):
  with tempfile.TemporaryDirectory()as d:
   output=Path(d);j=Journal.create(output/'journal.sqlite','c','S0F0','a'*64,['autonomous_review_01','b','c','d'])
   task=AutonomousTask(j,'autonomous_review_01',DATA);task.input('P1',dispatched=False)
   result=export(output,j,'test failure')
   self.assertEqual(result['run_type'],'autonomous_exploratory_smoke')
   self.assertEqual(result['state'],'running');self.assertIsNone(result['terminal'])
   self.assertIsNone(result['mechanical_legacy_score']);self.assertIsNone(result['human_label'])
   self.assertIsNone(json.loads((output/'simulated_release.json').read_text()))

 def test_stale_source_and_duplicate_slot_block_before_calls(self):
  with tempfile.TemporaryDirectory()as d:
   create_run(Path(d)/'run',{})
   with self.assertRaises(FileExistsError):create_run(Path(d)/'run',{})
   with self.assertRaises(ValueError):assert_integrity({'source_sha256':{}})
if __name__=='__main__':unittest.main()
