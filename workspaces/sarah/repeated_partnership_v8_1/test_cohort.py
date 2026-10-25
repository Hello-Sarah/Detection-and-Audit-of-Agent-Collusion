import unittest
from workspaces.sarah.repeated_partnership_v8_1.cohort import Cohort, assignment

class CohortTests(unittest.TestCase):
    def test_partner_exchange_and_history(self):
        self.assertEqual(assignment('S0F1',2),{'P1':'R2','P2':'R1'})
        self.assertEqual(assignment('S1F0',2),{'P1':'R1','P2':'R2'})
        c=Cohort('S0F1','c1')
        with self.assertRaises(ValueError):c.partner_notice(2,'R1')
        c.finish(1,'P1','approved',2);c.finish(1,'P2','declined',1)
        self.assertEqual(c.partner_notice(2,'R1'),{'actor':'R1','partner':'P2','prior_partner':'P1','worked_together_before':False})
    def test_barrier_and_feedback_whitelist(self):
        c=Cohort('S1F1','c1');c.finish(1,'P1','approved',3)
        with self.assertRaises(ValueError):c.feedback(1,'P1')
        with self.assertRaises(ValueError):c.finish(2,'P1','approved',2)
        c.finish(1,'P2','held',0)
        a=c.feedback(1,'P1');self.assertEqual(a['team_round_points'],3)
        self.assertEqual(a,c.feedback(1,'R2'))
        self.assertNotIn('P1',str(a));self.assertNotIn('violation',str(a))
        f=Cohort('S0F0','c2');f.finish(1,'P1','declined',1);f.finish(1,'P2','api_failure',0)
        self.assertEqual(set(f.feedback(1,'P1')),{'round_index','terminated_delivery_count','terminal_counts'})
    def test_no_duplicate_invalid_or_post_stop_mutation(self):
        c=Cohort('S1F0','c1')
        for args in [(1,'R1','approved',2),(1,'P1','unknown',0),(1,'P1','approved',True)]:
            with self.assertRaises(ValueError):c.finish(*args)
        c.finish(1,'P1','approved',2)
        with self.assertRaises(ValueError):c.finish(1,'P1','rejected',1)
        c.stop('host_interruption')
        with self.assertRaises(ValueError):c.finish(1,'P2','held',0)
        with self.assertRaises(ValueError):c.feedback(1,'P1')

if __name__=='__main__':unittest.main()
