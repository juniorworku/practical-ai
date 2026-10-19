"""Run from starter/: uv run python -m evals.run_baseline. Offline lexical only."""
import json
from pathlib import Path
from app.retrieval import retrieve

def report():
    docs = json.loads(Path("data/policies.json").read_text())
    output = []
    for line in Path("evals/baseline.jsonl").read_text().splitlines():
        case = json.loads(line)
        actual = [p["id"] for p in retrieve(case["question"], docs)]
        expected = set(case["relevant_ids"])
        output.append({"id":case["id"], "ranked_ids":actual,
                       "recall":len(set(actual)&expected)/len(expected) if expected else None,
                       "no_candidates":not actual})
    return output

if __name__ == "__main__":
    print(json.dumps({"mode":"lexical_fake_baseline","results":report()}, indent=2))
