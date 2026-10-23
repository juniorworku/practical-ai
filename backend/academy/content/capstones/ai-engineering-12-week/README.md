# ai-engineering-12-week: complete independent student capstone

## Product and prerequisite contract

Ingest a synthetic source through /api/documents/ before asking about it. Trace owner filtering, fixed character chunks, ranking, a 700-character context cap and model routing. Compare routine_fixture with reasoning_fixture; both are transparent local adapters, not real local/frontier LLMs. Request review before the local effect.

Modules 1–3 teach adapter contracts, context/state, retrieval and reviewed actions; Module 4 teaches the release harness; sessions 31–35 teach containers, concurrency, routing and quotas. This is the reproducible local graduation route. Real voice/model/GPU/cloud experiments remain separately configured integrations, not a hidden dependency or a claimed test result.

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
## Student build walkthrough — a bounded local SaaS release, with honest upgrade boundaries

The earlier voice, mixed-media, workspace and evaluation integration files remain separate runnable projects. This graduation service combines a narrower path: persisted synthetic text → scoped lexical retrieval → one of two scripted routes → reviewable draft → local receipt. The two routes do not call real local or frontier models. Cloud autoscaling, speech quality and GPU throughput need the separately taught deployment/provider experiments; this local service cannot certify them.

### Step 1 — carry the actual taught retrieval invariant into the build

Session 8 now contains the exact `select_context` function used by core.py. Run its published tests first:

```sh
python3.12 -m unittest -v test_core
```

The paragraph fixture deliberately places “Opened items are excluded” after character 350. The old fixed-character split could return the rule while dropping that exclusion. The current implementation keeps reviewed paragraph units intact, retains source ID/position/revision, and refuses a relevant unit that exceeds its 700-character allowance. needs_correction is visible and contains no answer or citations. It is safer than silently slicing an exclusion out of evidence.

The allowance counts evidence characters before join separators, not provider tokens. Owner filtering is the SQL adapter’s job before it calls the pure function. An irrelevant oversized paragraph is excluded by ranking; a relevant oversized paragraph requires a reviewed split. This is a deliberate conservative policy, not an optimal semantic chunker.

### Step 2 — follow storage identity and context through one request

`documents` derives an ID from owner and the exact text digest. Same owner/same bytes return the same identity; another owner cannot reuse that ID to read private content. This local fixture keeps every uploaded document searchable. It does not choose active policy versions or resolve contradictory uploads. Keep one approved policy per source for this scoped release; the ingestion/index-migration lessons teach the explicit activation mechanism needed before expanding that claim.

`ask` fetches only the authenticated owner’s documents, then `select_context` ranks whole units. The route selects routine_fixture or reasoning_fixture from the declared query rule. Both extract source text. The candidate cache key uses canonical JSON containing pipeline version, selected route, query and evidence revisions; it is an identity for a future cache, not an implemented hit or measured savings. Source IDs contain owner in this service. A general cache must also bind trusted owner/permission state explicitly and invalidate on revocation.

### Step 3 — interpret the evaluation denominator correctly

Run check.py, then evaluate.py in a fresh quota window as documented. Its 120 HTTP observations cover ten families with twelve variants each. Labels stay in the harness. A timeout or 429 remains a failed observation, not a row to delete. Four clients measure this bounded local workload; they do not simulate thousands of concurrent users or independent semantic tasks.

Session 29’s runtime studio now calculates cost per accepted result from all attempted work and leaves partial cost unknown. In this capstone, cost_usd and provider token usage remain null because no model is called. A passed mechanical release harness is not a measured faithfulness score. Retain a separate source-support review for any future real adapter and record model/prompt/dataset versions and disagreement.

### Step 4 — use failure evidence to decide the next change

| Failure | Repair at the taught boundary | Do not substitute |
| --- | --- | --- |
| Exception lost from context | Reviewed evidence-unit boundary in session 8 | A valid citation ID alone |
| Another owner sees source text | Owner predicate before retrieval | Post-generation redaction |
| Oversized relevant unit | Review its split or change a measured budget | Silent truncation |
| Identical candidate key after source change | Canonical source revision identity | Calling an unimplemented cache a hit |
| Partial cost reported as complete | Unknown-cost counter and undefined ratio | Zero for unavailable billing |

Student extension: before modifying the retriever, add a policy whose exclusion occurs after the old cut and prove the complete exclusion survives HTTP readback. Then add a relevant oversized unit and require needs_correction. Keep this test corpus separate from evaluate.py’s frozen corpus: injecting an intentionally oversized relevant policy changes the candidate environment. Use a dedicated fresh Compose project/volume for the extension, then run restart, outage and restoration drills on its exact IDs. Do not delete another project’s data to get a clean score.

### Read a failed acceptance report

The HTTP check starts a fresh report before its first request and updates it as checks run. A failed assertion or dependency exception leaves completed=false, the checks observed so far and error_type; it still exits nonzero. A completed=true report means the whole procedure finished. Latency p95 uses nearest rank, ceil(.95*n)-1, over its labeled sample. Do not reuse an older successful report after a new failed run, and do not mistake twelve sequential observations for a capacity benchmark.
<!-- student-depth:end -->

## Build from a fresh folder

Create exactly the files shown in the course with their shown paths. From this directory:

```sh
docker compose -p capstone-engineering up -d --build --wait
python3 check.py --base http://127.0.0.1:8214 --kind engineering --output observed.json
```

Open http://127.0.0.1:8214/ . First click Ingest source, then submit a refund question. Inspect the saved result, then confirm that exact draft using the demo reviewer button. The browser result must say approved in the local outbox and external_delivery false.

Expected: check.py exits zero and prints a passed check count plus the report path. The report contains actual IDs, individual checks and measured local p50/p95. Do not copy a prior report and call it your experiment. Nonzero exit or a missing report is incomplete work.

## Restart and outage acceptance

Retain draft_id from observed.json. Replace ID below with that exact value:

```sh
docker compose -p capstone-engineering up -d --force-recreate api
curl --fail -H 'Authorization: Bearer student-one' http://127.0.0.1:8214/api/records/ID/
docker compose -p capstone-engineering stop db
curl -i http://127.0.0.1:8214/api/health/
docker compose -p capstone-engineering start db
```

After recreation, the same ID and payload must still exist. During database outage health returns 503. After starting db, wait until health is ready and repeat readback. A process merely being running is insufficient.

## Actual backup and restore

Stop new writes for this small synthetic comparison. These commands preserve both source and restore databases. Pick a fresh restore name if repeating:

```sh
docker compose -p capstone-engineering exec -T db pg_dump -U learner -d capstone -Fc > capstone-backup.dump
docker compose -p capstone-engineering exec -T db createdb -U learner capstone_restore
docker compose -p capstone-engineering exec -T db pg_restore -U learner -d capstone_restore < capstone-backup.dump
docker compose -p capstone-engineering exec -T db psql -U learner -d capstone -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > before.txt
docker compose -p capstone-engineering exec -T db psql -U learner -d capstone_restore -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > restored.txt
python3 -c "from pathlib import Path; assert Path('before.txt').read_bytes()==Path('restored.txt').read_bytes(); print('restore readback matches')"
```

A created dump without matching restored records is not a recovery pass. Never substitute an academy or client database. The local app uses a one-shot initial schema; evolving it requires a reviewed forward migration, not deleting the volume. Cloud hosting would also require real identity, secret management, TLS, rollout and measured load evidence.

## Student extension and feedback

Change one approved source/case or extraction rule, preserve its counterexample, and add a new input/output case to check.py before changing the implementation. Run through the browser and HTTP check path again. Submit the actual report, restart readback and restore comparison with an explanation of a deliberately broken case. If you change scope, rebuild expected fixtures deliberately; never weaken a failing isolation or approval check.

Clean up only this project using `docker compose -p capstone-engineering down`. It preserves the synthetic volume. No other app uses this project name or port.


## Run the actual 120-case release harness

In a fresh minute quota window after other drills, run `python3 evaluate.py`. It sends 120 concrete requests across ten families at four concurrent clients to this actual API and PostgreSQL. Expected labels remain only in the harness, never in the request. The report preserves individual failures, HTTP errors, missing evidence, malformed output and denied ownership. Twelve variants per family do not become 120 independent semantic tasks. Inspect evaluation-observed.json and require all mechanical cases to pass. A quota hit remains a failed run to report; wait for a fresh quota window and rerun instead of dropping it. Actual semantic LLM judging, GPU throughput and cloud autoscaling remain untested.
