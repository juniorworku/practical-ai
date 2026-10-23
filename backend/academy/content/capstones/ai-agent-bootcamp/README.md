# ai-agent-bootcamp: complete independent student capstone

## Product and prerequisite contract

Ask a supported refund question; an unsupported topic must abstain and a requested write must be denied. The bounded loop permits search and draft only, enforces evidence-before-draft and stops at its step budget. Confirm a stored draft with a reviewer and prove replay creates the same local receipt.

Sessions 4–6 define the model contract and budget; 7–9 teach source identity and grounding; 10–12 teach bounded actions and approval; 13–14 teach HTTP/data ownership; 16–20 teach tests, traces, containers and recovery.

The assembly mechanics below repair the previously missing connection between separate lesson examples. Read them before attempting the final project. Every file follows inline in the course; the optional program download contains the identical capstone/ directory. Python 3.12 and Docker Compose are required. There is no import from another academy program, Workshop checkout or private app database.

## Connect the pieces before changing them

1. Read core.py first. Its process(input, mode, documents) function returns a status, text and evidence IDs. It must never receive the expected test answer. The provider is a named scripted fixture, so a passing run proves control flow, not model quality.
2. Read app.py's exact and identity functions. Reject extra fields and blank input before retrieval. Demo bearer strings resolve to a trusted owner/role at the server; a JSON owner field is rejected. These published fixture tokens are local teaching identities, not production authentication.
3. Trace ask: validate → owner-filter persisted sources → core workflow → save result → return ID. A timeout is a stored failed result, not an empty successful answer. Health runs a real query against the required table.
4. initialize is a one-shot schema release job. It creates the records and quota tables before Gunicorn starts. PostgreSQL bucket is a fixed-minute quota window: avoid the reserved SQL word window. Parameterized values stay outside SQL syntax. The ON CONFLICT increment is atomic across both HTTP workers; a Python dictionary counter would not be shared.
5. PostgreSQL JSONB stores an object, but Django raw cursors may return its JSON text. Decode a string at the storage boundary before accessing fields. Do not serialize an already serialized value twice. All reads include owner before payload leaves the database.
6. Approval digests bind text, source version and citations using one canonical server serialization. The UI uses the server's digest rather than trying to recreate Python JSON spacing in JavaScript. The submitted version and digest must match the row locked by SELECT FOR UPDATE. Only reviewer-one can approve owner one's draft. The effect is a local outbox row, never an external message, refund or calendar event.
7. The same transaction writes the local effect and approval status. A stable effect key plus the row lock makes simultaneous duplicate confirmation return the same receipt. A timed-out external write would need reconciliation; this local transaction does not claim distributed exactly-once delivery.
8. Browser code displays response text with textContent and retains the input on errors. It shows the stored result before review. An HTTP 201 says a result was saved; inspect status to distinguish needs_review, failed, abstain, denied or needs_correction.
9. Compose starts an isolated PostgreSQL volume, runs the schema job once, and publishes only the API on loopback. Recreating an API container must retain records because the database volume is separate. Dependency outage yields 503; health is not a substitute for the full check script.
10. check.py sends real HTTP requests and reads back their actual IDs. It tests changed approvals, wrong owners, malformed input, failures and concurrent duplicate review. Latency is measured around actual requests. Unknown token usage and spend remain null, not fabricated zero. This sequential local sample is not a cloud concurrency benchmark.

## Make the three pillars observable

Compare two core candidates on the same unchanged cases; retain failed and rejected work in the report. Measure HTTP latency separately from any future provider latency and report accepted-output quality. Preserve exact deterministic invariants while recording factual review separately. Context budgets here are explicitly characters; token accounting belongs in an actual model adapter. Scope and source revisions belong in any future cache key; no cache-hit or savings claim is made by these local projects.

## Diagnose a failed build or check

If schema exits nonzero, inspect that service's log before testing the API. If HTTP succeeds but the saved result differs, inspect core.process and the stored JSON separately. If a restart loses data, inspect the named volume and compose project name. If a duplicate approval changes receipts, inspect the row-lock/transaction boundary, not the prompt. Preserve the failed output with its repaired rerun.

<!-- student-depth:start -->
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
<!-- student-depth:end -->

## Build from a fresh folder

Create exactly the files shown in the course with their shown paths. From this directory:

```sh
docker compose -p capstone-boot up -d --build --wait
python3 check.py --base http://127.0.0.1:8211 --kind bootcamp --output observed.json
```

Open http://127.0.0.1:8211/ . Submit the prefilled synthetic example. Inspect the saved result, then confirm that exact draft using the demo reviewer button. The browser result must say approved in the local outbox and external_delivery false.

Expected: check.py exits zero and prints a passed check count plus the report path. The report contains actual IDs, individual checks and measured local p50/p95. Do not copy a prior report and call it your experiment. Nonzero exit or a missing report is incomplete work.

## Restart and outage acceptance

Retain draft_id from observed.json. Replace ID below with that exact value:

```sh
docker compose -p capstone-boot up -d --force-recreate api
curl --fail -H 'Authorization: Bearer student-one' http://127.0.0.1:8211/api/records/ID/
docker compose -p capstone-boot stop db
curl -i http://127.0.0.1:8211/api/health/
docker compose -p capstone-boot start db
```

After recreation, the same ID and payload must still exist. During database outage health returns 503. After starting db, wait until health is ready and repeat readback. A process merely being running is insufficient.

## Actual backup and restore

Stop new writes for this small synthetic comparison. These commands preserve both source and restore databases. Pick a fresh restore name if repeating:

```sh
docker compose -p capstone-boot exec -T db pg_dump -U learner -d capstone -Fc > capstone-backup.dump
docker compose -p capstone-boot exec -T db createdb -U learner capstone_restore
docker compose -p capstone-boot exec -T db pg_restore -U learner -d capstone_restore < capstone-backup.dump
docker compose -p capstone-boot exec -T db psql -U learner -d capstone -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > before.txt
docker compose -p capstone-boot exec -T db psql -U learner -d capstone_restore -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > restored.txt
python3 -c "from pathlib import Path; assert Path('before.txt').read_bytes()==Path('restored.txt').read_bytes(); print('restore readback matches')"
```

A created dump without matching restored records is not a recovery pass. Never substitute an academy or client database. The local app uses a one-shot initial schema; evolving it requires a reviewed forward migration, not deleting the volume. Cloud hosting would also require real identity, secret management, TLS, rollout and measured load evidence.

## Student extension and feedback

Change one approved source/case or extraction rule, preserve its counterexample, and add a new input/output case to check.py before changing the implementation. Run through the browser and HTTP check path again. Submit the actual report, restart readback and restore comparison with an explanation of a deliberately broken case. If you change scope, rebuild expected fixtures deliberately; never weaken a failing isolation or approval check.

Clean up only this project using `docker compose -p capstone-boot down`. It preserves the synthetic volume. No other app uses this project name or port.
