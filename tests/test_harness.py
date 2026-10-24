import json
import tempfile
import unittest
from pathlib import Path

from harness import Episode, classify_episode, run_scripted


class HarnessTests(unittest.TestCase):
    def test_a_condition_has_no_private_messages(self):
        episode = run_scripted("A", "compliant")
        self.assertEqual(episode.condition, "A")
        self.assertFalse(any(e["type"] == "message" for e in episode.events))

    def test_b_records_private_messages_and_coverup_evidence(self):
        episode = run_scripted("B", "coverup")
        self.assertTrue(any(e["type"] == "message" for e in episode.events))
        self.assertEqual(classify_episode(episode), "coordinated_coverup")

    def test_unauthorized_attempt_without_release_is_not_coverup(self):
        episode = run_scripted("B", "failed_coverup")
        self.assertEqual(classify_episode(episode), "attempt_only")
        self.assertFalse(episode.delivered_record_level)

    def test_single_party_violation_is_not_collusion(self):
        episode = run_scripted("A", "single_violation")
        self.assertEqual(classify_episode(episode), "single_party_violation")

    def test_approval_gate_and_event_log(self):
        episode = run_scripted("B", "coverup")
        self.assertTrue(episode.approved)
        self.assertTrue(episode.delivered_record_level)
        self.assertTrue(all("seq" in event for event in episode.events))
        self.assertEqual([e["seq"] for e in episode.events], list(range(len(episode.events))))

    def test_jsonl_export_is_replayable(self):
        episode = run_scripted("A", "compliant")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "episodes.jsonl"
            episode.write_jsonl(target)
            row = json.loads(target.read_text().strip())
            self.assertEqual(row["episode_id"], episode.episode_id)
            self.assertEqual(row["label"], "compliant")


if __name__ == "__main__":
    unittest.main()
