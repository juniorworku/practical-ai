"""Offline response-contract probes; check_agent.py tests the actual HTTP/MCP path."""
import unittest
from unittest.mock import patch
from agent import run,valid_evidence
GOOD={'mode':'lexical_fixture','answer':'14 days','citations':['doc:0'],
      'context_chars':7,'usage_tokens':None}

class ContractTests(unittest.TestCase):
    def test_empty_success_and_supported_response(self):
        self.assertTrue(valid_evidence(GOOD,'doc'))
        empty={**GOOD,'answer':None,'citations':[],'context_chars':0}
        self.assertTrue(valid_evidence(empty,'doc'))
        with patch('agent.search',return_value=empty):
            self.assertEqual(run('doc','refund')['status'],'abstained')

    def test_malformed_evidence_is_not_abstention_or_completion(self):
        invalid=[None,[],{**GOOD,'answer':None},{**GOOD,'citations':[]},
                 {**GOOD,'citations':['doc:0','doc:0']},{**GOOD,'citations':['other:0']},
                 {**GOOD,'citations':['doc:not-a-position']},
                 {**GOOD,'context_chars':True},{**GOOD,'unknown':'extra'}]
        for row in invalid:
            with self.subTest(row=row),patch('agent.search',return_value=row):
                self.assertEqual(run('doc','refund')['status'],'invalid_evidence')

    def test_broken_json_is_a_service_failure(self):
        with patch('agent.search',side_effect=ValueError('invalid JSON')):
            self.assertEqual(run('doc','refund')['status'],'service_unavailable')

    def test_proposal_and_budget(self):
        self.assertEqual(run('doc','refund',lambda o:[])['status'],'invalid_proposal')
        self.assertEqual(run('doc','refund',lambda o:{'name':'finish'})['status'],'missing_evidence')
        with patch('agent.search',return_value=GOOD):
            self.assertEqual(run('doc','refund',max_steps=1)['status'],'step_budget')
            self.assertEqual(run('doc','refund')['status'],'completed')

if __name__=='__main__':unittest.main()
