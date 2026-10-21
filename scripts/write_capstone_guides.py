"""Assembly teaching discovered while building the final projects as a learner."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'backend/academy/content/capstones'
SERVICE_GUIDE='''## Connect the pieces before changing them

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
'''
for slug,name,port,case,learned in [
 ('ai-agent-bootcamp','boot',8211,'Ask a supported refund question; an unsupported topic must abstain and a requested write must be denied. The bounded loop permits search and draft only, enforces evidence-before-draft and stops at its step budget. Confirm a stored draft with a reviewer and prove replay creates the same local receipt.','Sessions 4–6 define the model contract and budget; 7–9 teach source identity and grounding; 10–12 teach bounded actions and approval; 13–14 teach HTTP/data ownership; 16–20 teach tests, traces, containers and recovery.'),
 ('ai-workshops','workshop',8212,'Choose the document-extraction studio. Submit Supplier, Quantity, Unit price and Currency lines. The deterministic parser accepts only the taught schema, uses Decimal for exact money, and routes missing/duplicate/invalid fields to needs_correction. Confirm a valid purchase-request draft; this does not place an order.','Studio 1 sessions 1–3 teach the schema, extraction and review checks. Session 16 chooses this use case. Session 17 introduces the complete persistence/API connection. Other studios are portfolio practice, not five additional deployed app requirements.'),
 ('ai-engineering-12-week','engineering',8214,'Ingest a synthetic source through /api/documents/ before asking about it. Trace owner filtering, fixed character chunks, ranking, a 700-character context cap and model routing. Compare routine_fixture with reasoning_fixture; both are transparent local adapters, not real local/frontier LLMs. Request review before the local effect.','Modules 1–3 teach adapter contracts, context/state, retrieval and reviewed actions; Module 4 teaches the release harness; sessions 31–35 teach containers, concurrency, routing and quotas. This is the reproducible local graduation route. Real voice/model/GPU/cloud experiments remain separately configured integrations, not a hidden dependency or a claimed test result.')]:
 folder=BASE/slug
 readme=f'''# {slug}: complete independent student capstone

## Product and prerequisite contract

{case}

{learned}

The assembly mechanics below repair the previously missing connection between separate lesson examples. Read them before attempting the final project. Every file follows inline in the course; the optional program download contains the identical capstone/ directory. Python 3.12 and Docker Compose are required. There is no import from another academy program, Workshop checkout or private app database.

{SERVICE_GUIDE}

## Build from a fresh folder

Create exactly the files shown in the course with their shown paths. From this directory:

```sh
docker compose -p capstone-{name} up -d --build --wait
python3 check.py --base http://127.0.0.1:{port} --kind {'bootcamp' if name=='boot' else 'workshops' if name=='workshop' else 'engineering'} --output observed.json
```

Open http://127.0.0.1:{port}/ . {'First click Ingest source, then submit a refund question.' if name=='engineering' else 'Submit the prefilled synthetic example.'} Inspect the saved result, then confirm that exact draft using the demo reviewer button. The browser result must say approved in the local outbox and external_delivery false.

Expected: check.py exits zero and prints a passed check count plus the report path. The report contains actual IDs, individual checks and measured local p50/p95. Do not copy a prior report and call it your experiment. Nonzero exit or a missing report is incomplete work.

## Restart and outage acceptance

Retain draft_id from observed.json. Replace ID below with that exact value:

```sh
docker compose -p capstone-{name} up -d --force-recreate api
curl --fail -H 'Authorization: Bearer student-one' http://127.0.0.1:{port}/api/records/ID/
docker compose -p capstone-{name} stop db
curl -i http://127.0.0.1:{port}/api/health/
docker compose -p capstone-{name} start db
```

After recreation, the same ID and payload must still exist. During database outage health returns 503. After starting db, wait until health is ready and repeat readback. A process merely being running is insufficient.

## Actual backup and restore

Stop new writes for this small synthetic comparison. These commands preserve both source and restore databases. Pick a fresh restore name if repeating:

```sh
docker compose -p capstone-{name} exec -T db pg_dump -U learner -d capstone -Fc > capstone-backup.dump
docker compose -p capstone-{name} exec -T db createdb -U learner capstone_restore
docker compose -p capstone-{name} exec -T db pg_restore -U learner -d capstone_restore < capstone-backup.dump
docker compose -p capstone-{name} exec -T db psql -U learner -d capstone -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > before.txt
docker compose -p capstone-{name} exec -T db psql -U learner -d capstone_restore -At -c 'SELECT id,owner,kind,payload FROM records ORDER BY id' > restored.txt
python3 -c "from pathlib import Path; assert Path('before.txt').read_bytes()==Path('restored.txt').read_bytes(); print('restore readback matches')"
```

A created dump without matching restored records is not a recovery pass. Never substitute an academy or client database. The local app uses a one-shot initial schema; evolving it requires a reviewed forward migration, not deleting the volume. Cloud hosting would also require real identity, secret management, TLS, rollout and measured load evidence.

## Student extension and feedback

Change one approved source/case or extraction rule, preserve its counterexample, and add a new input/output case to check.py before changing the implementation. Run through the browser and HTTP check path again. Submit the actual report, restart readback and restore comparison with an explanation of a deliberately broken case. If you change scope, rebuild expected fixtures deliberately; never weaken a failing isolation or approval check.

Clean up only this project using `docker compose -p capstone-{name} down`. It preserves the synthetic volume. No other app uses this project name or port.
'''
 (folder/'README.md').write_text(readme)
p=BASE/'ai-engineering-12-week/README.md'
p.write_text(p.read_text()+'\n\n## Run the actual 120-case release harness\n\nIn a fresh minute quota window after other drills, run `python3 evaluate.py`. It sends 120 concrete requests across ten families at four concurrent clients to this actual API and PostgreSQL. Expected labels remain only in the harness, never in the request. The report preserves individual failures, HTTP errors, missing evidence, malformed output and denied ownership. Twelve variants per family do not become 120 independent semantic tasks. Inspect evaluation-observed.json and require all mechanical cases to pass. A quota hit remains a failed run to report; wait for a fresh quota window and rerun instead of dropping it. Actual semantic LLM judging, GPU throughput and cloud autoscaling remain untested.\n')
# Complete operator teaching for the two non-web deliverables.
(BASE/'freelancing-masterclass/README.md').write_text('''# Complete simulated client engagement

The capstone is a coherent client delivery, not a claim that a real client signed off. Use Python 3.12; no third-party package, model account or another program is needed. The client/ files are complete synthetic artifacts, and engagement.py actually runs their pilot and recovery checks.

## Build the engagement in order

1. Read baseline.json: 40 items × (8−5) minutes − 30 maintenance minutes = 90 projected minutes/week. These are fictional assumptions; they are not observed ROI. Match the buyer and workflow to the discovery and baseline lessons 1–3.
2. Compare offer.json and scope.json from lessons 4–6. Every promise must be in scope and have an acceptance ID. Automatic publication, real hosting and factual client acceptance are explicitly excluded. A fixed estimate is not permission to expand scope.
3. Read data-policy.json and requests.csv from lessons 7–9. Only id, source and text are approved. policy-v1 permits a verbatim source draft. An empty source or unapproved revision routes to needs_source; no model fills the gap.
4. acceptance.json fixes expected outcomes before the pilot runs. engagement.py opens a fresh SQLite file, writes drafts, closes it and reads back independently. It compares actual statuses and text with those unchanged cases. A passed schema or exact string is mechanical evidence, not general semantic review.
5. changes.json and support.json carry lessons 10–15 forward: reject an automatic-publication scope change, name manual fallback and assign maintenance/retention responsibility. The script creates a real backup, restores into a distinct file and compares rows through fresh connections. It does not simply trust a supplied recovery=true flag.
6. The report, client-email.md and case-study.md carry lessons 16–18 into the same client identity. They distinguish local checks, illustrative projections and unperformed human acceptance. Do not replace untested fields with passed to make the handover look complete. The generated email is a local file; nothing is sent.

## Run the delivered pilot and its counterexamples

From this directory:

```sh
python3 engagement.py --inputs client --output my-delivery
python3 check.py
```

Use a fresh output folder for each run; existing pilot databases are preserved rather than overwritten. Expected: scoped_local_handover true, client_acceptance not_performed; check.py prints actual pilot/acceptance/restore success and blocks four changed inputs. Inspect my-delivery/acceptance-report.json, client-email.md, case-study.md and restored.sqlite3. The source artifact hashes bind the report to the files you actually ran.

## Transfer and useful feedback

Change the buyer, source and baseline consistently across the client packet. Write the new acceptance cases before running the pilot. Deliberately add an unsupported promise and confirm it blocks handover; then restore the scoped offer. A failing expected label means the candidate disagrees with the fixed contract; it is not permission to rewrite labels after observing output. A human still needs to review factual usefulness, client authority and real deployment acceptance before any real engagement. Submit both the failed output and the scoped correction. Latency/restore duration are measured locally, costs stay unknown, and source/retention boundaries are explicit.
''')
(BASE/'terminal-tutor/README.md').write_text('''# Complete evidence-bound Terminal Tutor project

Use Python 3.12 and a terminal. No external coding agent, cloud account or other program is required. This capstone assembles the workspace, process, counterexample, permission and resumption lessons into three real commands.

## Understand the state before execution

1. init creates a scratch folder, a complete exercise.py and an inspectable instructions.json. It refuses to overwrite an existing exercise. Read the files before running them. The exercise uses the selection function and assertions taught in guides 3–5.
2. owned rejects a symlinked child or a child resolving outside the selected folder. Path ownership checks do not make arbitrary Python safe. Run only this inspected exercise under your own account; -I isolates Python import configuration and is not an OS sandbox.
3. run launches the current Python interpreter with -I, one exact script path and no shell. It captures stdout, stderr, exit status and a three-second deadline. Failure is preserved in evidence.json and the command exits nonzero. The script records SHA-256 hashes of the actual source and instruction package, as taught by the source revision and package-inspection concepts.
4. resume reads the evidence in a new process. It compares source, instructions and workspace before trusting that evidence. Changed source or permissions require a rerun. A passing execution produces a small next-action note; a failed execution produces a diagnosis action, not a success claim. The note is capped at 1000 characters; it contains only synthetic task evidence.
5. The fixed instructions permit the exercise file only. They are teaching configuration, not host security enforcement. No arbitrary shell command, network grant or external agent installation is implemented by this tutor.

## Build, run and resume

Copy tutor.py and check.py from the inline course. From their directory:

```sh
python3 tutor.py init my-scratch
python3 tutor.py run my-scratch
python3 tutor.py resume my-scratch
python3 check.py
```

Expected: the generated exercise prints two sources selected; empty capacity; original retained. Evidence reports exit_code 0. A separately launched resume reports passed_local_checks and a next action. check.py tests new processes, stale source, retained assertion failure and denied instruction expansion.

## Student extension and feedback

Add a negative-capacity test to my-scratch/exercise.py. Before rerunning, resume must reject stale evidence. Run the new file, inspect its real exit code and resume again. Introduce an assert False temporarily: run must exit nonzero and resume must say failed_or_timed_out. Repair the assertion without deleting the original failed transcript. If you see old output, inspect the absolute workspace, source hash and interpreter before changing your expected answer. Submit the changed code, observed evidence and bounded resume note. Execution time is measured locally; model cost is unknown/not applicable and no live tutoring quality has been evaluated.
''')
p=BASE/'genai-accelerator/README.md';s=p.read_text().split('\n\n# Final integration:',1)[0];s+='''

# Final integration: persisted source → bounded agent → real MCP

Read this after the API/worker, bounded-agent and MCP lessons. Unlike the earlier independent policy fixtures, agent.py now calls this project's actual HTTP /ask endpoint and uses the document ID returned by its own ingestion API. No private Workshop modules or another academy project are imported.

1. Start the complete stack above. check.py establishes ingestion, worker completion, scope denial and deduplication.
2. Read agent.request: fixture identity is configured outside the proposal; urllib has a five-second call deadline and non-2xx responses remain errors. The agent checks an allowlisted exact proposal shape, owns copied observations and stops within a maximum step budget. Its fixed proposal adapter is explicitly scripted; a real model is a separately evaluated adapter, not silently simulated intelligence.
3. search returns API-owned citation IDs bound to the ingested document. finish cannot run before a search, and the proposal cannot substitute its own answer or invented citations. Successful empty retrieval abstains; HTTP failure is service_unavailable. Lexical matching is a known retrieval limitation, not semantic embeddings.
4. mcp_server.py captures the selected document and configured identity from trusted environment. Its only tool is a bounded read-only search. It wraps HTTP errors as ToolError instead of passing error prose as evidence. The tool caller cannot choose another tenant.
5. check_agent.py uploads a real synthetic document, polls persisted readiness, runs agent counterexamples, then launches the SDK server as a real child process. It initializes, discovers tools, calls the actual persisted policy, rejects blank queries and unknown writes, then closes the subprocess. The server needs CAPSTONE_DOCUMENT_ID; the check supplies it from the upload result rather than requiring a placeholder.

Install the pinned client SDK into a fresh Python 3.12 environment; the API dependency environment is separate:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-client.txt
python check.py
python check_agent.py
```

Expected: observed-agent.json contains a real document ID, completed search/finish trace and true SDK protocol checks. No model tokens, paid calls or external writes occur. If the worker never makes the document ready, inspect worker and migration logs; do not change the document to ready by hand. If discovery works but the call fails, test the authenticated HTTP boundary first, then the MCP error envelope. A local lexical/scripted fixture is not evidence of live-model quality or production hosting.

Extend the tool with a separately labeled unsupported question, retain the no-evidence and denied-write cases, and run both API and actual MCP checks again. Submit their real reports plus the previously taught restart and restore transcripts.
''';p.write_text(s)
