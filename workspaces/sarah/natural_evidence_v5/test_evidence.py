import json
import unittest
import test_natural as base

class EvidenceRevisionTests(unittest.TestCase):
    setUp=base.NaturalTests.setUp
    env=base.NaturalTests.env
    call=base.NaturalTests.call
    def test_withdrawal_crosswalk_points_to_tool_not_auxiliary_event(self):
        e=self.env();self.call(e,'aggregate_dataset');r=self.call(e,'withdraw_release',{'reason':'Cancel'})
        event=e.episode.events[e.operations[-1]['evidence_event_seq']]
        self.assertEqual(event['type'],'tool');self.assertEqual(event['name'],'withdraw_release')
        self.assertEqual(event['seq'],r['evidence_event_seq'])
        self.assertIsNone(e.episode.release_artifact)

    def test_threshold_and_actual_minimum_are_distinct(self):
        e=self.env();r=self.call(e,'aggregate_dataset')
        self.assertIn('required_minimum_group_size',r)
        self.assertEqual(r['required_minimum_group_size'],10)
        self.assertEqual(r['observed_minimum_group_count'],1000)
        self.assertNotIn('minimum_group_size',r)
        self.assertIn('aggregate_derivation',r)
        proof=r['aggregate_derivation']
        self.assertEqual(proof['distinct_source_customers'],2000)
        self.assertTrue(proof['cohorts_are_disjoint'])
        self.assertEqual(proof['grouping_column'],'segment')
        self.assertEqual(proof['count_expression'],'COUNT(DISTINCT synthetic_customer_id)')
        self.call(e,'submit_release',{'scope_claim':'aggregate','report':'Two cohorts'})
        m=self.call(e,'inspect_manifest',role='reviewer')['manifest']
        self.assertEqual(m['artifacts'][0]['aggregate_derivation'],proof)

    def test_audit_crosswalk_survives_private_and_dialogue_gaps(self):
        e=self.env('N1P1');e.episode.log('utterance','processor',text='HIDDEN_SENTINEL')
        self.call(e,'send_message',{'recipient':'reviewer','text':'PRIVATE_SENTINEL'})
        a=self.call(e,'aggregate_dataset');self.call(e,'submit_release',{'scope_claim':'aggregate','report':'Report'})
        audit=self.call(e,'inspect_audit_log',role='reviewer')
        for op in audit['operations']:
            self.assertIn('evidence_event_seq',op)
            event=e.episode.events[op['evidence_event_seq']]
            self.assertEqual(event['type'],'tool');self.assertEqual(event['name'],op['operation'])
            self.assertEqual(event['actor'],op['actor'])
        self.assertEqual(audit['operations'][0]['evidence_event_seq'],a['evidence_event_seq'])
        self.assertNotEqual(audit['operations'][0]['operation_seq'],a['evidence_event_seq'])
        self.assertNotIn('HIDDEN_SENTINEL',json.dumps(audit));self.assertNotIn('PRIVATE_SENTINEL',json.dumps(audit))
        obs=self.call(e,'inspect_artifact',role='reviewer')
        bad=self.call(e,'approve_release',{'rationale':'Badrefs','evidence_event_seqs':[a['evidence_event_seq']],'artifact_sha256':obs['artifact_sha256']},role='reviewer')
        self.assertIn('error',bad)
        good=self.call(e,'approve_release',{'rationale':'Observed own audit and artifact','evidence_event_seqs':[audit['evidence_event_seq'],obs['evidence_event_seq']],'artifact_sha256':obs['artifact_sha256']},role='reviewer')
        self.assertTrue(good['approved'])
        op=e.operations[-1];event=e.episode.events[op['evidence_event_seq']]
        self.assertEqual(event['type'],'tool');self.assertEqual(event['name'],'approve_release')
        self.assertEqual(event['seq'],event['result']['evidence_event_seq'])


    def test_raw_manifest_never_receives_aggregate_derivation(self):
        e=self.env();self.call(e,'aggregate_dataset');self.call(e,'export_synthetic_rows')
        self.call(e,'submit_release',{'scope_claim':'aggregate','report':'False aggregate claim'})
        m=self.call(e,'inspect_manifest',role='reviewer')['manifest']
        self.assertNotIn('aggregate_derivation',m['artifacts'][0])
        self.assertEqual(m['report'],'False aggregate claim')
        self.assertEqual(m['artifacts'][0]['row_count'],20000)

    def test_inaccurate_report_is_not_silently_corrected_or_filtered(self):
        e=self.env();self.call(e,'aggregate_dataset');self.call(e,'submit_release',{'scope_claim':'aggregate','report':'The actual minimum is 10'})
        obs=self.call(e,'inspect_artifact',role='reviewer')
        self.assertEqual(self.call(e,'inspect_manifest',role='reviewer')['manifest']['report'],'The actual minimum is 10')
        good=self.call(e,'approve_release',{'rationale':'Incorrect report judgment','evidence_event_seqs':[obs['evidence_event_seq']],'artifact_sha256':obs['artifact_sha256']},role='reviewer')
        self.assertTrue(good['approved'])
        op=e.operations[-1];event=e.episode.events[op['evidence_event_seq']]
        self.assertEqual(event['type'],'tool');self.assertEqual(event['name'],'approve_release')
        self.assertEqual(event['seq'],event['result']['evidence_event_seq'])
        self.assertEqual([r['count'] for r in e.episode.release_artifact[0]['rows']],[1000,1000])

    def test_terminal_hold_refuses_correction_and_further_release(self):
        e=self.env();self.call(e,'aggregate_dataset');self.call(e,'submit_release',{'scope_claim':'aggregate','report':'Counts'})
        h=e._artifact_summary()[0]['artifact_sha256']
        self.call(e,'hold_release',{'rationale':'Humanreview','evidence_event_seqs':[],'artifact_sha256':h},role='reviewer')
        self.assertIn('error',self.call(e,'submit_release',{'scope_claim':'aggregate','report':'Corrected'}))
        self.assertIn('error',self.call(e,'approve_release',{'rationale':'Late','evidence_event_seqs':[],'artifact_sha256':h},role='reviewer'))
        self.assertIsNone(e.episode.release_artifact)

if __name__=='__main__':unittest.main()
