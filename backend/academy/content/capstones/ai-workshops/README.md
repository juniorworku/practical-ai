# ai-workshops: complete independent student capstone

## Product and prerequisite contract

Choose the document-extraction studio. Submit Supplier, Quantity, Unit price and Currency lines. The deterministic parser accepts only the taught schema, uses Decimal for exact money, and routes missing/duplicate/invalid fields to needs_correction. Confirm a valid purchase-request draft; this does not place an order.

Studio 1 sessions 1–3 teach the schema, extraction and review checks. Session 16 chooses this use case. Session 17 introduces the complete persistence/API connection. Other studios are portfolio practice, not five additional deployed app requirements.

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
## Student build walkthrough — extraction evidence to confirmed purchase draft

This capstone implements one selected studio, document extraction. It does not silently require deploying the other four portfolio workflows. Studio 1 session 2 now supplies the exact parser and its line-provenance studio; session 11 supplies a separate per-class routing report for the triage studio. Do not substitute routing accuracy for extraction acceptance.

### Step 1 — reproduce the source-to-field calculation

Before starting Docker, run:

```sh
python3.12 -m unittest -v test_core
```

The parser enumerates lines from 1, splits each at the first colon, stores raw source spans in `field_evidence`, and trims the value for validation. For the four-line fixture, quantity is supported by line 2, unit price by line 3, and Decimal('10.00') multiplied by 2 produces '20.00'. This is exact arithmetic after validation, not model extraction or an inferred purchase price.

Add a second Quantity line. Predict needs_correction, both line spans retained, no computed record and no reviewable answer. The duplicate cannot overwrite the first value and become a successful record. A colon in a supplier name must survive because splitting occurs only once. If your code loses that punctuation, repair parsing rather than editing the source fixture.

### Step 2 — read the two different review boundaries

A needs_correction record tells the student to repair ambiguous or invalid input. It is not approvable. A needs_review record has passed this schema but still requires human confirmation. Schema validation cannot prove the request was authorized by a real business or that the supplier is legitimate. The teaching identities and inputs are synthetic; there is no external purchase action.

The HTTP route stores the original input, normalized record, field evidence, issue codes and status in one draft payload. On readback, compare `field_evidence` with that exact input, not a subsequently edited document. Correcting the source means submitting another request and reviewing its new ID. This simple capstone does not implement an editable revision editor or automatic linkage between those IDs.

### Step 3 — inspect actual HTTP failure and approval behavior

Run the documented Compose and check.py commands. Missing fields and invalid quantities are domain results with needs_correction; malformed HTTP shape is 400; missing identity is 401; a student trying to approve is 403; stale or changed approval is 409. Database dependency failure is 503. These statuses guide different learner actions, rather than one generic “something went wrong” response.

The approver confirms the normalized text, citation and source-version digest returned by the server. The unchanged stored input and spans remain available for inspection. The local receipt records approval only; external_delivery=false. An effect row is not proof that a supplier received anything.

### Step 4 — retain a small evidence table before extending

| Input variation | Expected parser result | What to inspect |
| --- | --- | --- |
| Four valid fields, quantity 2, price 10.00 | needs_review, total 20.00 | Line 2/3 evidence and exact Decimal total |
| Missing price | needs_correction | Missing-field issue, no invented zero |
| Two conflicting price lines | needs_correction | Both raw spans, no computed record |
| Negative quantity or NaN price | needs_correction | Validation before arithmetic |
| Extra Owner line | needs_correction | Exact declared schema, no client authority |

For a useful extension, add a second supported currency only after defining its schema and test cases. Do not add currency conversion rates or a provider call as an unexplained requirement. Keep both field correctness and whole-record acceptance in your report: three correct fields and one wrong price must not become a fully accepted purchase draft. Measure reviewer workload separately from parser latency. Retain failures, restart readback and the restore comparison alongside your final portfolio case study.

### Read a failed acceptance report

The HTTP check starts a fresh report before its first request and updates it as checks run. A failed assertion or dependency exception leaves completed=false, the checks observed so far and error_type; it still exits nonzero. A completed=true report means the whole procedure finished. Latency p95 uses nearest rank, ceil(.95*n)-1, over its labeled sample. Do not reuse an older successful report after a new failed run, and do not mistake twelve sequential observations for a capacity benchmark.
<!-- student-depth:end -->

## Build from a fresh folder

Create exactly the files shown in the course with their shown paths. From this directory:

```sh
docker compose -p capstone-workshop up -d --build --wait
python3 check.py --base http://127.0.0.1:8212 --kind workshops --output observed.json
```

Open http://127.0.0.1:8212/ . Submit the prefilled synthetic example. Inspect the saved result, then confirm that exact draft using the demo reviewer button. The browser result must say approved in the local outbox and external_delivery false.

Expected: check.py exits zero and prints a passed check count plus the report path. The report contains actual IDs, individual checks and measured local p50/p95. Do not copy a prior report and call it your experiment. Nonzero exit or a missing report is incomplete work.

## Restart and outage acceptance

Retain draft_id from observed.json. Replace ID below with that exact value:

```sh
docker compose -p capstone-workshop up -d --force-recreate api
curl --fail -H 'Authorization: Bearer student-one' http://127.0.0.1:8212/api/records/ID/
docker compose -p capstone-workshop stop db
curl -i http://127.0.0.1:8212/api/health/
docker compose -p capstone-workshop start db
```

After recreation, the same ID and payload must still exist. During database outage health returns 503. After starting db, wait until health is ready and repeat readback. A process merely being running is insufficient.

## Actual backup and restore

Stop new writes for this small synthetic comparison. These commands preserve both source and restore databases. Pick a fresh restore name if repeating:

```sh
docker compose -p capstone-workshop exec -T db pg_dump -U learner -d capstone -Fc > capstone-backup.dump
docker compose -p capstone-workshop exec -T db createdb -U learner capstone_restore
docker compose -p capstone-workshop exec -T db pg_restore -U learner -d capstone_restore < capstone-backup.dump
docker compose -p capstone-workshop exec -T db psql -U learner -d capstone -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > before.txt
docker compose -p capstone-workshop exec -T db psql -U learner -d capstone_restore -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > restored.txt
python3 -c "from pathlib import Path; assert Path('before.txt').read_bytes()==Path('restored.txt').read_bytes(); print('restore readback matches')"
```

A created dump without matching restored records is not a recovery pass. Never substitute an academy or client database. The local app uses a one-shot initial schema; evolving it requires a reviewed forward migration, not deleting the volume. Cloud hosting would also require real identity, secret management, TLS, rollout and measured load evidence.

## Student extension and feedback

Change one approved source/case or extraction rule, preserve its counterexample, and add a new input/output case to check.py before changing the implementation. Run through the browser and HTTP check path again. Submit the actual report, restart readback and restore comparison with an explanation of a deliberately broken case. If you change scope, rebuild expected fixtures deliberately; never weaken a failing isolation or approval check.

Clean up only this project using `docker compose -p capstone-workshop down`. It preserves the synthetic volume. No other app uses this project name or port.
