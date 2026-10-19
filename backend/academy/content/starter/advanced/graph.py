"""A real LangGraph workflow with conditional repair and bounded retries."""
import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from policies import search

class State(TypedDict):
    question: str
    evidence: list[dict[str, str]]
    answer: str
    attempts: int
    verdict: str
    trace: list[str]
    simulate_bad_draft: bool

def retrieve(state):
    return {"evidence": search(state["question"]), "trace": state["trace"] + ["retrieve"]}

def draft(state):
    hits = state["evidence"]
    if not hits:
        answer = "No supporting policy found."
    elif state["simulate_bad_draft"]:
        answer = "Refunds are always available."
    else:
        answer = hits[0]["text"]
    return {"answer": answer, "attempts": state["attempts"] + 1,
            "trace": state["trace"] + ["draft"]}

def verify(state):
    valid = (not state["evidence"] and state["answer"] == "No supporting policy found.") or any(
        state["answer"] == x["text"] for x in state["evidence"])
    return {"verdict": "accepted" if valid else "rejected", "trace": state["trace"] + ["verify"]}

def route(state):
    return "finish" if state["verdict"] == "accepted" or state["attempts"] >= 2 else "repair"

def repair(state):
    return {"simulate_bad_draft": False, "trace": state["trace"] + ["repair"]}

def build():
    graph = StateGraph(State)
    for name, node in [("retrieve", retrieve), ("draft", draft), ("verify", verify), ("repair", repair)]:
        graph.add_node(name, node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "draft")
    graph.add_edge("draft", "verify")
    graph.add_conditional_edges("verify", route, {"finish": END, "repair": "repair"})
    graph.add_edge("repair", "draft")
    return graph.compile(checkpointer=InMemorySaver())

def initial(question="refund requests", bad=False):
    return {"question": question, "evidence": [], "answer": "", "attempts": 0,
            "verdict": "pending", "trace": [], "simulate_bad_draft": bad}

if __name__ == "__main__":
    workflow = build()
    config = {"configurable": {"thread_id": "demo"}, "recursion_limit": 12}
    result = workflow.invoke(initial(bad=True), config)
    print(json.dumps(result, indent=2))
    print("Checkpoint verdict:", workflow.get_state(config).values["verdict"])
