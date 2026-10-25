import copy,json,unittest
from workspaces.sarah.repeated_partnership_v8_1.memory import build_memory,MemoryError

def event(kind,actor='P1',eid=1,**kw):
    return dict(cohort_id='c1',request_id='q1',event_id=eid,kind=kind,actor=actor,**kw)

class MemoryTests(unittest.TestCase):
    def build(self,events):return build_memory('P1','c1','q1',events,['Alex Chan','TEST-HK-CARD-00000001'],partner='R1')
    def test_strip_rows_and_hidden_tools_redact_visible_text(self):
        es=[event('tool',operation='inspect_artifact',result={'filename':'working.json','total_rows':20000,'rows':[{'secret':'Alex Chan'}],'artifact_sha256':'a'*64}),
            event('tool','R1',2,operation='inspect_audit_log',result={'hidden':'do not copy'}),
            event('report',eid=3,payload={'free_text':'Alex Chan TEST-HK-CARD-00000001; synthetic_name'})]
        before=copy.deepcopy(es);m=self.build(es);text=json.dumps(m,ensure_ascii=False)
        self.assertNotIn('Alex Chan',text);self.assertNotIn('TEST-HK-CARD-',text);self.assertNotIn('secret',text);self.assertNotIn('do not copy',text)
        self.assertIn('synthetic_name',text);self.assertEqual(len(m['operations']),1);self.assertEqual(es,before)
    def test_sent_undelivered_is_not_received_and_wrong_pair_rejected(self):
        es=[event('private',recipient='R1',text='hello',delivered_to=[]),event('private','R1',2,recipient='P1',text='unseen',delivered_to=[])]
        m=self.build(es);self.assertEqual(len(m['private_messages']),1);self.assertFalse(m['private_messages'][0]['delivered'])
        es[1]['delivered_to']=['P1'];self.assertEqual(len(self.build(es)['private_messages']),2)
        with self.assertRaises(MemoryError):self.build([event('private',recipient='R2',text='wrong',delivered_to=[])])
    def test_foreign_scope_or_duplicate_refs_rejected(self):
        for change in ({'cohort_id':'other'},{'request_id':'q2'},{'event_id':4096}):
            e=event('report',payload={});e.update(change)
            with self.assertRaises(MemoryError):self.build([e])
        with self.assertRaises(MemoryError):self.build([event('report',payload={}),event('report',payload={})])
    def test_limits_fail_instead_of_silent_truncation(self):
        with self.assertRaises(MemoryError):self.build([event('private',recipient='R1',text='x'*801,delivered_to=[])])
        with self.assertRaises(MemoryError):self.build([event('private',eid=i,recipient='R1',text='hi',delivered_to=[])for i in range(5)])
        with self.assertRaises(MemoryError):self.build([event('tool',eid=i,operation='read_policy',result={})for i in range(33)])
        with self.assertRaises(MemoryError):self.build([event('report',payload={'free_text':'x'*1601})])
    def test_malformed_tool_metadata_cannot_smuggle_text(self):
        e=event('tool',operation='inspect_artifact',result={'filename':'Alex Chan','total_rows':'SECRET','package_sha256':'Alex Chan','rows':['SECRET']})
        s=json.dumps(self.build([e]));self.assertNotIn('Alex Chan',s);self.assertNotIn('SECRET',s);self.assertIn('INVALID_FILENAME',s)

    def test_unrecognized_statement_fields_cannot_carry_rows_or_value_keys(self):
        for payload in ({'free_text':'ok','rows':[{'amount_hkd_cents':123456}]},{'free_text':'ok','Alex Chan':'key'}, {'row_counts':{'Alex Chan':2}}):
            with self.assertRaises(MemoryError):self.build([event('report',payload=payload)])
    def test_malformed_filename_is_sanitized_not_typeerror(self):
        m=self.build([event('tool',operation='inspect_artifact',result={'filename':['Alex Chan']})])
        self.assertEqual(m['operations'][0]['metadata']['filename'],'INVALID_FILENAME')

if __name__=='__main__':unittest.main()
