import unittest
from unittest.mock import patch
import graph as graph_module
from agent import run
from graph import build, initial

class Examples(unittest.TestCase):
    def test_agent_evidence(self):
        self.assertEqual(run("refund requests")["citation"], "policy-1")
        self.assertEqual(run("unicorn vacation")["status"], "abstained")
    def test_agent_bounds(self):
        loop = lambda q, obs: {"action": "search", "query": q}
        self.assertEqual(run("refund requests", loop, 2)["status"], "step_budget")
        self.assertEqual(run("refund requests", lambda q, o: {"action": "delete"})["status"], "denied_action")
    def test_false_citation(self):
        def lie(q, obs):
            return {"action": "finish", "source_id": "invented"} if obs else {"action": "search", "query": q}
        self.assertEqual(run("refund requests", lie)["status"], "unsupported_citation")
    def test_decision_adapter_cannot_mutate_harness_evidence(self):
        def tamper(q, observations):
            if not observations: return {"action":"search","query":q}
            observations[-1].append({"id":"invented","text":"fake policy"})
            return {"action":"finish","source_id":"invented"}
        self.assertEqual(run("refund requests",tamper)["status"],"unsupported_citation")
        with self.assertRaises(ValueError):run("refund requests",max_steps=True)

    def test_graph_repair(self):
        graph = build(); config = {"configurable": {"thread_id": "repair"}, "recursion_limit": 12}
        result = graph.invoke(initial(bad=True), config)
        self.assertEqual(result["trace"], ["retrieve", "draft", "verify", "repair", "draft", "verify"])
        self.assertEqual(result["verdict"], "accepted")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(graph.get_state(config).values["answer"], result["answer"])
    def test_graph_isolated_threads_and_abstention(self):
        graph = build()
        a = {"configurable": {"thread_id": "a"}}
        b = {"configurable": {"thread_id": "b"}}
        graph.invoke(initial(), a)
        result = graph.invoke(initial("unicorn vacation"), b)
        self.assertEqual(result["verdict"], "accepted")
        self.assertEqual(result["evidence"], [])
        self.assertTrue(graph.get_state(a).values["evidence"])

    def test_graph_stops_after_unrepairable_draft(self):
        with patch.object(graph_module, "repair", lambda state: {"trace": state["trace"] + ["repair"]}):
            workflow = graph_module.build()
            result = workflow.invoke(initial(bad=True), {"configurable": {"thread_id": "failed"}})
        self.assertEqual(result["verdict"], "rejected")
        self.assertEqual(result["attempts"], 2)

if __name__ == "__main__":
    unittest.main()
