import unittest
from agent_lab import run

class AgentLoopTests(unittest.TestCase):
    def test_normal_and_trace(self):
        def decide(obs):
            return {"action": "finish", "answer": "See policy-1"} if obs else {"action": "search", "query": "refund"}
        state = run(decide, {"search": lambda q: {"source_id": "policy-1"}})
        self.assertEqual(state.stop_reason, "completed")
        self.assertEqual(len(state.trace), 1)
    def test_infinite_loop_stops(self):
        state = run(lambda obs: {"action": "search", "query": "refund"}, {"search": lambda q: []}, 2)
        self.assertEqual(state.stop_reason, "step_budget")
        self.assertEqual(len(state.trace), 2)
    def test_denied_action_does_not_execute(self):
        calls = []
        state = run(lambda obs: {"action": "delete", "query": "refund"}, {"search": lambda q: calls.append(q)})
        self.assertEqual(state.stop_reason, "denied_action")
        self.assertEqual(calls, [])
    def test_timeout_is_not_empty_success(self):
        def timeout(q): raise TimeoutError()
        state = run(lambda obs: {"action": "search", "query": "refund"}, {"search": timeout})
        self.assertEqual(state.stop_reason, "tool_timeout")
        self.assertEqual(state.observations, [])
    def test_premature_finish(self):
        self.assertEqual(run(lambda obs: {"action": "finish", "answer": "made up"}, {}).stop_reason, "unsupported_finish")
