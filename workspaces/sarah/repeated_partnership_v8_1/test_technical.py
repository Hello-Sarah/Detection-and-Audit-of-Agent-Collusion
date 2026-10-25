import json
from pathlib import Path
import tempfile
import unittest
from workspaces.sarah.repeated_partnership_v8_1.technical import freeze,verify_manifest,validate_approval,run_technical
from workspaces.sarah.repeated_partnership_v8_1.offline import SafeFixtureTransport


class TechnicalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.record=self.base/'readiness.json'
        self.record.write_text(json.dumps({'status':'offline_pass','model':'gpt-5-mini-2025-08-07','tokenizer_version':'0.12.0','encoding':'o200k_base'}))
        self.manifest=self.base/'manifest.json'

    def test_freeze_pins_eight_technical_deliveries_and_source(self):
        freeze(self.manifest,self.record)
        m=verify_manifest(self.manifest,check_runtime=False)
        self.assertEqual((m['max_deliveries'],m['max_requests'],m['proposed_cap_usd']),(8,128,'15'))
        self.assertFalse(m['formal_auto_start'])
        self.assertEqual([c['condition']for c in m['cohorts']],['S1F1','S0F0'])
        self.record.write_text('{}')
        with self.assertRaises(ValueError):verify_manifest(self.manifest,check_runtime=False)

    def test_manifest_allocation_cannot_be_silently_expanded(self):
        freeze(self.manifest,self.record)
        m=json.loads(self.manifest.read_text());m['cohorts'].append(m['cohorts'][0]);m['max_requests']=256
        self.manifest.write_text(json.dumps(m))
        with self.assertRaises(ValueError):verify_manifest(self.manifest,check_runtime=False)

    def test_approval_required_before_any_run_directory_is_created(self):
        freeze(self.manifest,self.record)
        for ref,cap in (('', '15'),('approval','0'),('approval','16')):
            with self.assertRaises(ValueError):validate_approval(ref,cap)
        output=self.base/'not-created'
        with self.assertRaises(ValueError):run_technical(self.manifest,output,approval_ref='',cap_usd='15')
        self.assertFalse(output.exists())

    def test_scripted_full_technical_run_exports_all_eight_unreviewed(self):
        freeze(self.manifest,self.record)
        output=self.base/'run'
        summary=run_technical(self.manifest,output,approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='15',
                    _transport_fixture=SafeFixtureTransport(),_estimator_fixture=lambda p:{'serialized_body_tokens':100,'usable_as_hard_bound':False})
        self.assertEqual(len(summary['episodes']),8)
        self.assertTrue(all(e['terminal']=='approved'and e['label']=='unreviewed'and e['human_label']is None for e in summary['episodes']))
        self.assertEqual(summary['run_type'],'scripted_offline_fixture')
        self.assertEqual(summary['budget']['request_count'],64)
        with self.assertRaises(FileExistsError):run_technical(self.manifest,output,approval_ref='OFFLINE_FIXTURE_ONLY',cap_usd='15',_transport_fixture=SafeFixtureTransport(),_estimator_fixture=lambda p:{'serialized_body_tokens':100})

if __name__=='__main__':unittest.main()
