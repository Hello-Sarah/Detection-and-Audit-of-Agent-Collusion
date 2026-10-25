import tempfile,unittest
from pathlib import Path
from .collector import _summary
from workspaces.sarah.repeated_partnership_v8_1.budget import BudgetLedger

class ProgressTests(unittest.TestCase):
 def test_only_fully_resolved_allocation_is_completed(self):
  with tempfile.TemporaryDirectory()as tmp:
   b=BudgetLedger.create(Path(tmp)/'budget.sqlite',cap_nusd=8*10**9,max_requests=64,approval_ref='OFFLINE_FIXTURE_ONLY')
   self.addCleanup(b.close)
   m={'allocation':[{'episode_id':f'slot{i}','condition':'C0','block':1}for i in range(16)]}
   self.assertEqual(_summary(m,[],b,None,True)['status'],'in_progress')
   rows=[{'episode_id':f'slot{i}','condition':'C0','state':'terminal','terminal':'held','initial_input_confirmed':True}for i in range(16)]
   self.assertEqual(_summary(m,rows,b,None,True)['status'],'completed')
   self.assertEqual(_summary(m,rows,b,'ExportFailure',True)['status'],'stopped')

if __name__=='__main__':unittest.main()
