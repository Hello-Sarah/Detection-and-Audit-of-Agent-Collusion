import unittest
from workspaces.sarah.repeated_partnership_v8_1 import allocation

class AllocationTests(unittest.TestCase):
    def test_four_balanced_blocks_have_unique_ids_and_balanced_round_order(self):
        a=allocation.formal_allocation();self.assertEqual(a,allocation.formal_allocation())
        self.assertEqual(len(a),16)
        self.assertEqual(len({q for c in a for q in c['request_ids']}),64)
        conditions={'S0F0','S1F0','S0F1','S1F1'}
        for block in range(1,5):self.assertEqual({c['condition']for c in a if c['block']==block},conditions)
        for condition in conditions:
            cells=[c for c in a if c['condition']==condition];self.assertEqual(len(cells),4)
            for offset in (0,2):
                self.assertEqual(sum(c['execution_order'][offset]==c['request_ids'][offset]for c in cells),2)
        self.assertTrue(all(set(c['execution_order'][:2])==set(c['request_ids'][:2])for c in a))
    def test_cost_ceiling_includes_all_formal_calls_and_separate_technical_gate(self):
        x=allocation.cost_proposal()
        self.assertEqual(x['formal_requests_max'],1024)
        self.assertEqual(x['formal_uncached_ceiling_usd'],'110.788608')
        self.assertEqual(x['technical_uncached_ceiling_usd'],'13.848576')
        self.assertEqual(x['combined_uncached_ceiling_usd'],'124.637184')
        self.assertFalse(x['spending_authorized'])

if __name__=='__main__':unittest.main()
