"""Deterministic agent-loop teaching baseline. No API calls or side effects."""
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class State:
    observations: list = field(default_factory=list)
    trace: list = field(default_factory=list)
    stop_reason: str = ""
    answer: str = ""

def run(decide: Callable, tools: dict, max_steps: int = 4) -> State:
    if not 1 <= max_steps <= 100:
        raise ValueError("step budget must be 1..100")
    state = State()
    for step in range(max_steps):
        proposal = decide(tuple(state.observations))
        if not isinstance(proposal, dict):
            state.stop_reason = "invalid_decision"
            break
        action = proposal.get("action")
        if action == "finish":
            answer = proposal.get("answer")
            if not isinstance(answer, str) or not state.observations:
                state.stop_reason = "unsupported_finish"
                break
            state.answer = answer
            state.stop_reason = "completed"
            break
        query = proposal.get("query")
        if action not in tools or not isinstance(query, str) or not 3 <= len(query) <= 1000:
            state.stop_reason = "denied_action"
            break
        try:
            result = tools[action](query)
        except TimeoutError:
            state.stop_reason = "tool_timeout"
            break
        state.observations.append(result)
        state.trace.append({"step": step, "action": action, "outcome": "returned"})
    else:
        state.stop_reason = "step_budget"
    return state
