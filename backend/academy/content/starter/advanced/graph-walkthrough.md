# Working LangGraph workflow: retrieve, draft, verify and repair

## Learn the concept

We will use the real LangGraph runtime, not a homemade graph-shaped loop. State is a typed dictionary; nodes return partial state updates. Edges decide the order, and a conditional edge chooses between repair and ending. This workflow deliberately starts with a false draft, rejects it and repairs it from retrieved evidence.

`trace` is explicitly replaced with the old trace plus a node name. No append reducer is configured, so returning only `["draft"]` would overwrite the earlier events. The verifier uses exact evidence matching to keep this example testable; semantic fact checking needs a richer evaluator and labeled cases.
## Step 1 — Prepare a separate exercise folder

Download the program starter kit from the Accelerator overview. Extract the ZIP and open `workspace/advanced` in your terminal. Do not run these commands inside Workshop's application folder. Python 3.12 works on your Intel Mac; there is no GPU or paid API requirement.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The dependency file pins the tested MCP and LangGraph releases. This is a separate environment, not an upgrade of Workshop. If `python3.12` is unavailable, locate your installed Python 3.12 interpreter and use its absolute path. If importing `mcp` fails, check `python -m pip show mcp` and ensure the same interpreter runs your script.
## Step 2 — Create the shared evidence module

Our collection contains two synthetic policies. `search` validates input and returns IDs with evidence. Lexical matching is deliberately simple: it teaches the orchestration boundary, not advanced RAG relevance. Returned text is data, never an instruction to expand tool permissions.

Save as `policies.py` (complete file):

```python
"""Synthetic, allowlisted evidence. No files, network or user database access."""
POLICIES = {"policy-1": "Refund requests must be submitted within 30 days.",
            "policy-2": "Support is available Monday through Friday."}

def search(query: str) -> list[dict[str, str]]:
    if not isinstance(query, str) or not 3 <= len(query) <= 200:
        raise ValueError("query must contain 3..200 characters")
    words = set(query.lower().split())
    return [{"id": key, "text": text} for key, text in POLICIES.items()
            if words & set(text.lower().replace(".", "").split())]
```
## Step 3 — Write nodes and connect the graph

Focus on one node at a time: retrieve returns evidence; draft creates an answer; verify checks support; repair turns off the deliberate fault. `route` ends after acceptance or two drafts. The graph recursion limit provides a second bound. `InMemorySaver` records checkpoints by thread ID while this Python process lives; it does not survive process shutdown or provide production storage.

Save as `graph.py` (complete file):

```python
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
```
## Step 4 — Run and inspect the repair route

```bash
python graph.py
```

Expected trace: `retrieve → draft → verify → repair → draft → verify`. Expect `attempts: 2`, `verdict: accepted` and the exact refund-policy answer. The final checkpoint verdict is `accepted`. Change `initial(bad=True)` to `initial(bad=False)` and predict a three-node trace with only one draft.

## Step 5 — Inspect state and isolate sessions

```python
from graph import build, initial
workflow = build()
config = {"configurable": {"thread_id": "practice-a"}, "recursion_limit": 12}
workflow.invoke(initial(bad=True), config)
snapshot = workflow.get_state(config)
assert snapshot.values["attempts"] == 2
assert snapshot.values["verdict"] == "accepted"
```

Use a new thread ID for an independent run. The included test verifies that an unanswered question in another thread does not overwrite the first thread's evidence. Checkpoint inspection is not crash recovery: durable recovery is a separate extension using a persistent saver and idempotent side effects.

## Step 6 — Force a failure

Change repair so it keeps `simulate_bad_draft` true. The second verify should remain `rejected` and terminate at the two-draft limit. A terminated workflow with a rejected verdict must not be displayed as a successful answer. Restore the function, then run the test suite. Also try an invalid query and observe a validation exception before drafting.

## Run the regression suite

```bash
python -m unittest test_examples -v
```

Expect six passing tests after creating the agent and graph files. They cover supported evidence, abstention, step budgets, denied actions, false citations, repair traces, checkpoint inspection and thread isolation.

## Acceptance checks

Draw the edges without looking at the code. Explain which state updates merge, which lists replace and what stops the repair cycle. Describe the additional persistence, authorization and cancellation work needed before deploying this workflow.
