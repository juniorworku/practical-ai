import unittest
from evaluate import evaluate, summarize
from pipeline import FixtureProvider, ProviderError

class EvaluationTests(unittest.IsolatedAsyncioTestCase):
    async def test_cold_and_warm_fixed_cases(self):
        report = await evaluate(FixtureProvider())
        self.assertEqual(report['observations'],12)
        self.assertTrue(report['gate_passed'])
        self.assertTrue(any(row['cached'] for row in report['rows']))
        self.assertIsNone(report['cost_per_accepted_result'])
        self.assertIsNone(report['input_tokens'])
    async def test_outages_remain_in_report(self):
        class Broken:
            identity='broken'
            async def answer(self,*args): raise ProviderError('synthetic unavailable')
        report=await evaluate(Broken(),repeats=1)
        self.assertFalse(report['gate_passed'])
        self.assertEqual(len(report['rows']),6)
        self.assertTrue(any(row['error']=='ProviderError' for row in report['rows']))
    async def test_critical_failure_is_not_hidden_by_average(self):
        report=await evaluate(FixtureProvider(),repeats=1)
        row=next(row for row in report['rows'] if row['case']=='unauthorized')
        row['passed']=False
        summary=summarize(report['rows'],'fixture')
        self.assertEqual(summary['critical_failures'],['unauthorized'])
        self.assertFalse(summary['gate_passed'])

if __name__=='__main__':unittest.main()
