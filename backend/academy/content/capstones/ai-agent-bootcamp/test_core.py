import unittest
from core import run,process

class AgentTests(unittest.TestCase):
    def test_budget_and_evidence_before_draft(self):
        self.assertEqual(run('refund','fixture',max_steps=1)['error'],'step_budget')
        with self.assertRaises(ValueError):run('refund','fixture',lambda o:{'name':'draft'})

    def test_proposal_shape_is_not_authority(self):
        for action in [None,[],{'name':'draft','owner':'other'}]:
            with self.subTest(action=action), self.assertRaises(ValueError):
                run('refund','fixture',lambda o:action)
        self.assertEqual(run('refund','fixture',lambda o:{'name':'delete'})['status'],'denied')

    def test_supported_negative_and_unknown_are_distinct(self):
        self.assertIn('Opened items are excluded.',process('opened refund','fixture',[])['text'])
        self.assertEqual(process('wallpaper','fixture',[])['status'],'abstain')
        self.assertEqual(process('delete refunds','fixture',[])['status'],'denied')
        with self.assertRaises(TimeoutError):process('refund','timeout',[])

if __name__=='__main__':unittest.main()
