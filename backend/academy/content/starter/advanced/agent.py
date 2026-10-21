"""Scripted agent harness; the decision adapter can later be replaced by an LLM."""
import json
from copy import deepcopy
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
    if type(max_steps) is not int or not 1 <= max_steps <= 20:
        raise ValueError("max_steps must be 1..20")
    observations, trace = [], []
    for step in range(max_steps):
        proposal = decide(question, tuple(deepcopy(observations)))
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
