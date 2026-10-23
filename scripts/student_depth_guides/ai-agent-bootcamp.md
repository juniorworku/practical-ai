## Student build walkthrough — trace one draft all the way to its receipt

This project has two layers. `core.py` is the scripted, bounded read-only agent. `app.py` is the HTTP, identity, quota and PostgreSQL adapter. Keep those responsibilities separate: a proposal function never receives a database connection or reviewer authority. Sessions 5 and 14 now contain runtime studios for actual asynchronous deadlines and transaction rollback; complete those before this integration.

### Step 1 — prove the pure control flow before starting containers

From your fresh capstone directory, run:

```sh
python3.12 -m unittest -v test_core
```

Read each assertion in `test_core.py`. A one-step allowance permits a search but cannot also finish. A proposal to draft before searching raises an evidence error. A proposal with an extra owner field fails its exact shape check; an unknown operation is denied. The policy contains both the refund rule and the opened-item exclusion. A known negative policy answer must preserve that exclusion, while an unrelated wallpaper question abstains. These are actual control-flow assertions over a scripted fixture, not tests of a model’s understanding.

Prediction checkpoint: `run('refund','fixture',max_steps=1)` must return failed/step_budget, not needs_review. If it succeeds, inspect where the step counter is decremented. Do not increase the expected budget just to hide a missing transition.

### Step 2 — trace request validation and persisted failure

Start Compose and run the complete HTTP check from the earlier section. Follow one request through these statements in `app.py`:

1. `identity` maps the demo bearer token to a trusted owner and role. `exact` rejects a client-provided owner. Admission uses the shared PostgreSQL quota rather than a process-local dictionary.
2. `ask` validates input and fixture mode, then calls `process`. The policy corpus in this Bootcamp build is the explicit constant in `core.py`; `documents` is an intentionally unused common adapter parameter. There is no hidden upload or vector-search feature.
3. `TimeoutError` becomes a failed result with provider_timeout, null text and no citations. The route then saves that result. Inspect the returned status as well as HTTP 201: 201 means this result record was created, not that generation succeeded.
4. `record` binds JSON as a parameter and stores it in JSONB. `get_record` includes owner in the SQL query and decodes raw JSON text if required by the driver. Use the returned ID to read the same stored input/result.

This failure mode is injection at the workflow boundary. It does not enforce a real provider network deadline; the earlier asynchronous studio teaches that adapter responsibility.

### Step 3 — bind review to exactly what was displayed

The server computes approval_digest over text, citation IDs and source version with one canonical serialization. Copy that returned digest and version when approving. Never reconstruct the hash from JavaScript object formatting. Inside `transaction.atomic`, `get_record(..., lock=True)` locks the owner-scoped row. Only after role, version, digest and state checks succeed can it insert the deterministic `effect:<draft_id>` local receipt and update the draft.

Predict the two concurrent callers: the first holds the lock and commits one receipt; the second then reads approved and returns that receipt. The HTTP check exercises four replays. This proves a local database boundary. It does not mean a remote refund or message can be retried safely after a lost response.

### Step 4 — break, diagnose and repair the integrated path

| Observed result | First boundary to inspect | Required evidence |
| --- | --- | --- |
| Unsupported question gets a policy answer | `process` topic gate and unchanged unknown-topic case | Actual request, status, text and citations |
| Wrong owner reads the draft | Owner predicate in `get_record`, before JSON leaves SQL | Same stored ID, two identities, 200 versus 404 |
| Stale approval succeeds | Version/digest comparison inside the lock | Changed digest gets 409 and no receipt |
| Timeout returns plausible text | Exception classification before saving | Failed record read back under the original ID |
| Recreated API loses the result | Compose database volume and project name | Same ID and payload before/after replacement |

Student variation: add one explicit forbidden operation and its case to `test_core.py` before changing the gate. Preserve the unsupported-topic and opened-item exclusion cases. Run the pure tests, actual HTTP checks, restart readback and fresh restore comparison. Your release evidence must include the failed case and corrected rerun; a successful browser button alone is insufficient.

### Read a failed acceptance report

The HTTP check starts a fresh report before its first request and updates it as checks run. A failed assertion or dependency exception leaves completed=false, the checks observed so far and error_type; it still exits nonzero. A completed=true report means the whole procedure finished. Latency p95 uses nearest rank, ceil(.95*n)-1, over its labeled sample. Do not reuse an older successful report after a new failed run, and do not mistake twelve sequential observations for a capacity benchmark.
