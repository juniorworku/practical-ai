# Working agent: decisions, tools, evidence and stopping

## Learn the concept

An agent harness owns the action loop. A decision adapter proposes the next action, and the harness validates it. This example uses a scripted adapter so every trace is reproducible. It is a working control-loop exercise, not a claim of autonomous LLM reasoning. Later you can replace only `scripted_decision` with a model adapter returning the same dictionary contract.

A result is not supported merely because a tool ran. The harness requires the proposed citation to appear in retrieved evidence, then returns the exact policy text. This prevents fabricated citation IDs in this small exercise; it does not establish general semantic correctness of arbitrary model-written prose.
## Step 1 — Prepare a separate exercise folder

Download **course & starter** from the Accelerator overview. Extract the ZIP and open `genai-accelerator/starter/advanced` in your terminal. Do not run these commands inside Workshop's application folder. Python 3.12 works on your Intel Mac; there is no GPU or paid API requirement.

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
## Step 3 — Write the agent harness

Read the file in order. First, the adapter chooses `search` or `finish`. Next, `run` enforces input and step budgets. The search branch validates arguments through the tool boundary. The finish branch abstains on no evidence or denies unsupported citations. Unknown actions never execute. Returning structured stop reasons makes a failed run distinguishable from a valid empty search.

Save as `agent.py` (complete file):

```python
"""Scripted agent harness; the decision adapter can later be replaced by an LLM."""
import json
if __package__:
    from .policies import search
else:
    from policies import search

def scripted_decision(question, observations):
    if not observations:
        return {"action": "search", "query": question}
    hits = observations[-1]
    return {"action": "finish", "source_id": hits[0]["id"] if hits else None}

def run(question, decide=scripted_decision, max_steps=4):
    if not isinstance(question, str) or not 3 <= len(question) <= 200:
        raise ValueError("question must contain 3..200 characters")
    if not isinstance(max_steps, int) or not 1 <= max_steps <= 20:
        raise ValueError("max_steps must be 1..20")
    observations, trace = [], []
    for step in range(max_steps):
        proposal = decide(question, tuple(observations))
        if not isinstance(proposal, dict):
            return {"status": "invalid_decision", "trace": trace}
        action = proposal.get("action")
        trace.append({"step": step, "action": action})
        if action == "search":
            try:
                observations.append(search(proposal.get("query")))
            except ValueError:
                return {"status": "invalid_arguments", "trace": trace}
        elif action == "finish":
            if not observations:
                return {"status": "premature_finish", "trace": trace}
            if not observations[-1]:
                return {"status": "abstained", "answer": "No supporting policy found.", "trace": trace}
            hit = next((x for x in observations[-1] if x["id"] == proposal.get("source_id")), None)
            if hit is None:
                return {"status": "unsupported_citation", "trace": trace}
            return {"status": "completed", "answer": hit["text"], "citation": hit["id"], "trace": trace}
        else:
            return {"status": "denied_action", "trace": trace}
    return {"status": "step_budget", "trace": trace}

if __name__ == "__main__":
    print(json.dumps(run("refund requests"), indent=2))
```
## Step 4 — Run a normal request

```bash
python agent.py
```

Expected key fields: status `completed`, citation `policy-1`, answer `Refund requests must be submitted within 30 days.` The trace contains one `search` and one `finish`. Predict those events before running. Change the question to `unicorn vacation` and expect `abstained`; the harness must not invent a policy.

## Step 5 — Exercise budget and authority failures

```python
from agent import run
loop = lambda question, observations: {"action": "search", "query": question}
assert run("refund requests", loop, 2)["status"] == "step_budget"
assert run("refund requests", lambda q, o: {"action": "delete"})["status"] == "denied_action"
```

Run this in a Python session started from the same folder. Notice that a repeated search stops even though it remains a valid tool call. A future real-model adapter must not receive arbitrary code execution or filesystem access just to answer a policy question.

## Step 6 — Test and extend

After creating the graph example, run `python -m unittest test_examples -v`. Before then, the assertions above and `python agent.py` work with the standard library alone. Add a test that returns an invented citation after search, then check `unsupported_citation`. Extend the tool output with a timestamp only if you can define freshness requirements. Keep API integration optional: no keys are used by this example.

## Acceptance checks

Explain why the decision adapter cannot grant itself a new action, why empty evidence produces abstention, and how a step budget differs from a wall-clock timeout. This loop handles a bounded local tool, not network retries or production cancellation.
