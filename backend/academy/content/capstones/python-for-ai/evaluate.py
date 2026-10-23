"""Measured, versioned contract evaluation; no model-faithfulness certification."""
import argparse
import asyncio
import hashlib
import json
import math
import statistics
import tempfile
import time
from pathlib import Path
from pipeline import FixtureProvider, Store, answer_one

CASES = [
    {"id":"supported", "owner":"team-a", "query":"refund days?", "source":"a-refunds-v1", "critical":False},
    {"id":"punctuation", "owner":"team-a", "query":"refund!", "source":"a-refunds-v1", "critical":False},
    {"id":"missing", "owner":"team-a", "query":"salary", "source":None, "critical":False},
    {"id":"unauthorized", "owner":"team-b", "query":"refund days?", "source":None, "critical":True},
    {"id":"other-owner", "owner":"team-b", "query":"support hours", "source":"b-support-v1", "critical":False},
    {"id":"ambiguous", "owner":"team-a", "query":"how long?", "source":None, "critical":False},
]
DATASET_REVISION = "owner-source-cases-v2"

def summarize(rows, provider_identity):
    if not rows: raise ValueError("No observations")
    times = sorted(row["latency_ms"] for row in rows)
    failed = [row["case"] for row in rows if not row["passed"]]
    critical = [row["case"] for row in rows if row["critical"] and not row["passed"]]
    counts = [row["usage"] for row in rows if row["provider_called"]]
    known = bool(counts) and all(isinstance(u, dict) and type(u.get("input_tokens")) is int and type(u.get("output_tokens")) is int for u in counts)
    return {"dataset_revision":DATASET_REVISION,
        "dataset_sha256":hashlib.sha256(json.dumps(CASES, sort_keys=True).encode()).hexdigest(),
        "provider":provider_identity, "observations":len(rows), "source_accuracy":(len(rows)-len(failed))/len(rows),
        "failed_cases":failed, "critical_failures":critical,
        "p50_ms":statistics.median(times), "p95_ms":times[math.ceil(.95*len(times))-1],
        "latency_population":"every observed attempt, including errors; nearest-rank p95",
        "provider_calls":sum(row["provider_called"] for row in rows),
        "input_tokens":sum(u["input_tokens"] for u in counts) if known else None,
        "output_tokens":sum(u["output_tokens"] for u in counts) if known else None,
        "cost_per_accepted_result":None, "cost_note":"No billing tariff or local resource cost was measured; unknown is not zero.",
        "semantic_quality":"unmeasured; source identity is not claim support",
        "gate_passed":not critical and not failed, "rows":rows}

async def evaluate(provider, *, repeats=2):
    if type(repeats) is not int or not 1 <= repeats <= 100: raise ValueError("Use 1–100 repeats")
    rows = []
    with tempfile.TemporaryDirectory() as folder:
        store = Store(str(Path(folder)/"evaluation.sqlite3"))
        for _ in range(repeats):
            for case in CASES:
                started = time.perf_counter()
                try:
                    result = await answer_one(case["owner"], case["query"], provider, store)
                    row = {"case":case["id"], "passed":result["source"]==case["source"],
                        "critical":case["critical"], "error":None,
                        "provider_called":not result["cached"] and result["provider"]!="not-called",
                        "usage":result["usage"], "cached":result["cached"]}
                except Exception as error:
                    row = {"case":case["id"], "passed":False, "critical":case["critical"],
                        "error":type(error).__name__, "provider_called":True, "usage":None, "cached":False}
                row["latency_ms"] = (time.perf_counter()-started)*1000
                rows.append(row)
    return summarize(rows, provider.identity)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--output", default="evaluation-observed.json")
    args = parser.parse_args()
    report = asyncio.run(evaluate(FixtureProvider(), repeats=args.repeats))
    Path(args.output).write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({key:value for key,value in report.items() if key!="rows"}, indent=2))
    raise SystemExit(0 if report["gate_passed"] else 1)
