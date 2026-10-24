import unittest
import runner
import collect

class TaskContracts(unittest.TestCase):
    def test_pressure_has_no_segmentation_only_objective(self):
        self.assertNotIn("customer-segmentation",runner.PRESSURE["P1"])
        self.assertIn("delivery window",runner.PRESSURE["P1"])

    def test_eight_cells_balanced_randomized_blocks(self):
        expected={f'N{n}P1T{t}' for t in range(4) for n in range(2)}
        self.assertEqual(set(runner.CONDITIONS),expected)
        self.assertEqual(len(collect.schedule(True)),8)
        formal=collect.schedule()
        self.assertEqual(len(formal),32)
        for block in range(4):
            self.assertEqual({x['condition'] for x in formal[block*8:(block+1)*8]},expected)
        self.assertEqual(formal,collect.schedule())

    def test_frozen_config_matches_actual_actor_input_each_cell(self):
        class EmptyClient:
            def complete(self,*args):return {'choices':[{'message':{'role':'assistant','content':None},'finish_reason':'stop'}]}
        for c in runner.CONDITIONS:
            with self.subTest(c=c):
                ep=runner.run_live_episode(EmptyClient(),c,'fake')
                config=ep.events[0]['configuration']
                self.assertEqual(config['task_family'],c[-2:])
                self.assertEqual(config['buyer_request'],runner.buyer_request(c))
                self.assertEqual(config['pressure_text'],runner.PRESSURE['P1'])
                for e in ep.events:
                    if e['type']=='api_input':
                        self.assertIn(runner.buyer_request(c),e['messages'][1]['content'])
                        self.assertEqual('send_message' in {t['function']['name'] for t in e['tools']},c.startswith('N1'))
        for t in range(4):
            self.assertEqual(runner.buyer_request(f'N0P1T{t}'),runner.buyer_request(f'N1P1T{t}'))
        self.assertEqual(len({runner.buyer_request(f'N0P1T{t}') for t in range(4)}),4)

if __name__=='__main__':unittest.main()
