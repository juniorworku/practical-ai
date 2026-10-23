# Complete local API, PostgreSQL, migration and worker lab

This lab implements synthetic policy ingestion, scoped reads, a bounded lexical answer, queue delivery and actual PostgreSQL persistence. It is a local teaching service with two fixed demo identities, not production authentication, semantic embeddings or a live model. No secret from Workshop or the academy is used. PostgreSQL and Redis stay on their private network. The API uses **8215**, separate from academy **8080**, Workshop **8000** and the earlier starter **8010**.

## Before running: understand the data path

1. `Upload` validates exact fields and a maximum 10,000-character input. Whitespace-only documents and questions are rejected before persistence or retrieval. Database failures are classified as sanitized 503 responses across routes, preserving the distinction from successful missing-evidence abstention.
2. `quota` uses an atomic Redis increment/expiry script shared by all API processes: each demo organization gets 60 authenticated requests per 60-second window. Exceeding it returns 429 and Retry-After; an unavailable quota store fails closed with 503. The fixed window can permit a boundary burst, and these fixture numbers are not a measured capacity recommendation. `identity` maps an explicit fixture bearer token to one of two organizations. This demonstrates trusted scope binding at the adapter. Anyone who knows a demo token can use it: do not expose this lab publicly.
3. `upload` computes a revision digest and inserts under `UNIQUE(org,digest)`. PostgreSQL arbitrates concurrent duplicates. The same bytes in another organization are a different scoped document.
4. The connection context commits before `enqueue`. A queue failure therefore leaves an observable accepted row. The API returns a 503 with its document ID; an explicit retry route can requeue it. There is no claim of atomic database-and-broker delivery. A production extension would use a transactional outbox.
5. The Celery message contains only the document ID. The worker loads its own row under `FOR UPDATE`, preventing two workers from transforming it simultaneously.
6. In one transaction the worker inserts chunks and marks ready. If an exception occurs before commit, both changes roll back. Duplicate delivery observes ready or the unique chunk key and cannot create another searchable effect.
7. The text parser is intentionally sentence splitting over a synthetic string. It does not parse PDFs or call an embedding service. The parser version is fixed in this fixture; changing parsers requires a new ingestion identity and index migration. Celery runs with a solo pool for this local exercise; do not assume its configured process time limits provide hard interruption in that pool. Database statement timeouts and bounded fixture inputs are separate controls. The state is only accepted, ready or failed here; the richer state machine is taught separately.
8. `status` filters by organization before returning the document or its chunks. The same ID returns 404 to the other demo identity.
9. `ask` checks owner and ready state before loading chunks, matches literal terms and retains the whole small document under a 1,000-character evidence cap; oversized matched documents return 409/context_review_required. Missing evidence yields a null answer with no citations. Token usage remains unknown, not zero.
10. `health` actually queries PostgreSQL. Its 200 does not establish broker or worker health: the end-to-end ingestion check proves that separately.
11. `alembic.ini` locates the migration environment. `env.py` supplies a runtime connection. Revision 001 creates constraints and 002 adds parser metadata without deleting old rows. Destructive downgrade is deliberately refused.
12. The image installs its declared dependencies, runs as UID 10001 and binds inside the container to 8010. Compose publishes only API port 8215. The API and worker wait for the one-shot migration service; each connects to the same private database.

<!-- student-depth:start -->
## Student build walkthrough — prove the handoff between persistence, agent and MCP

Lessons 13, 16 and 25 now include runtime studios for response-envelope invariants, preserving policy exceptions in context and the commit-to-queue gap. Complete them before treating the final MCP integration as one working system. This final project uses its own FastAPI/PostgreSQL/Redis/Celery service and source IDs; no other academy program or Workshop checkout supplies missing code.

### Step 1 — prove response validation offline

Before installing the MCP client SDK, run:

```sh
python3.12 -m unittest -v test_agent test_evidence
```

`valid_evidence` validates a top-level object before indexing fields. It checks exact mode/schema, unique citation IDs bound to the selected document, numeric chunk positions, an actual integer character count and supported-versus-empty-result consistency. Because the API joins chunks with one separating space, answer length equals selected character count plus one space per additional citation. The validator enforces this specific lexical fixture contract. A new provider envelope needs a versioned adapter and new tests, rather than silently relaxing the checks.

Predict the counterexample: answer=null with citations=['doc:0'] is invalid_evidence. A legitimate empty search is answer=null, citations=[] and context_chars=0. Broken JSON is service_unavailable. These three states must not become interchangeable.

### Step 2 — observe the committed ingestion boundary

Start the complete Compose stack and run check.py. Upload validation happens before persistence. The document row commits before enqueue; if Redis is unavailable, the API exposes its existing ID and a retryable delivery failure. Starting a worker cannot process a message that was never enqueued. Use the taught retry route for that accepted ID after recovery, then inspect ready and its actual chunks.

Celery loads the document under a PostgreSQL row lock. Chunk inserts and ready state commit together. Duplicate delivery observes ready or the uniqueness boundary. This is not an atomic broker/database transaction or a transactional outbox. Retain accepted and ready as separate observations in the recovery transcript, not a single screenshot of a healthy API.

### Step 3 — preserve policy conditions before the agent sees evidence

The earlier sentence-selection baseline could match “Refund window is 14 days” while omitting “Unused items only.” This capstone’s `evidence.select_document` now selects all sentence chunks from the already authorized small document when any chunk matches. An unmatched exclusion therefore stays attached. Over 1000 selected characters produces HTTP 409/context_review_required rather than silent truncation or false empty success. For no lexical match, the empty-search contract still applies. Lesson 16 teaches and tests this exact function before final integration. This conservative whole-document rule is intentionally local and bounded; it does not replace the earlier evaluation of retrieval strategies for larger corpora.

### Step 4 — trace host-owned evidence through the bounded agent

`run` starts with an empty observation history. The first scripted action is search. A valid empty result is still a completed search observation, so the next finish can abstain rather than searching forever. The host copies observations before giving them to the proposal adapter; proposals cannot mutate trusted evidence in place. A finish before search is missing_evidence; an unknown action is denied; an exhausted step budget is not completion.

Only validated HTTP results enter observations. `finish` returns the latest host-owned answer and citations instead of accepting invented answer text in a proposal. This is a scripted decision adapter. It verifies orchestration and mechanical integrity, not a live model’s ability to choose tools or interpret policies. A matching source ID alone still does not prove semantic support for arbitrary prose.

### Step 5 — test the actual protocol, then locate a failure

Use the earlier pinned client setup and run check_agent.py. It obtains its own document ID from ingestion, polls actual readiness, then launches the MCP server as a child process with that trusted ID in its environment. Initialization and tool discovery precede invocation. The client checks one supported source call, an invalid query and a denied unknown write. Closing the session must close the subprocess. The printed result is real protocol evidence for the pinned environment, not a test of every remote transport or malicious-tool scenario.

| Observation | First check | Expected feedback |
| --- | --- | --- |
| Document stays accepted | Queue delivery and worker logs | Requeue the same ID if enqueue failed |
| HTTP works but agent rejects reply | Exact envelope and cross-field invariant | invalid_evidence, not a fabricated answer |
| Other owner’s citation appears | SQL scope and host’s trusted document ID | Reject before finish |
| Discovery works, tool call fails | Authenticated /ask, then MCP error envelope | Tool error stays out of evidence |
| Empty search reaches step_budget | No-search versus empty-observation state | One search then abstained finish |

Student extension: retain a deliberately malformed envelope in the offline test table, add one unsupported topic to the actual HTTP/agent checks, and rerun both suites. Preserve real document IDs, restart readback, restored IDs/text, and the actual MCP shutdown observation. A passing stdio fixture does not establish OAuth, remote HTTP authorization, cloud reliability or model quality; scope the handover to what you actually observed.
<!-- student-depth:end -->

## Run the complete example

Prerequisite: Docker with Compose. From the folder containing this README and compose.yaml:

```bash
docker compose -p capstone-accelerator up -d --build --wait
python3 check.py
```

Expected: check.py prints `worker_ready: true`, `scope_denial: true`, `deduplicated: true`, an answer containing both `Refund window is 14 days` and `Unused items only`, and `unanswerable_abstained: true`. It uses a fresh synthetic document each run. A failure exits nonzero. The transcript identifies your actual generated document ID; retain it for the following exercises.

## Exercise 1 — observe worker outage and recovery

Predict: an upload can be accepted while no worker is consuming it. Stop only this lab's worker:

```bash
docker compose -p capstone-accelerator stop worker
curl -sS -X POST http://127.0.0.1:8215/documents -H 'Authorization: Bearer demo-one' -H 'Content-Type: application/json' -d '{"text":"Recovery policy fixture. Refund window is 7 days."}'
```

Retain the returned ID. Use it to GET `/documents/ID` with the same header. The state should be accepted if this text has never already been indexed. Asking it before ready returns 409. Do not interpret 202 as completed ingestion. Start the worker:

```bash
docker compose -p capstone-accelerator start worker
```

Poll the status route with the actual ID. It must become ready and contain the transformed chunks. If the state was already ready before the outage, the deduplication key reused a previous fixture: change the synthetic text and repeat.

Feedback: if the document never becomes ready, inspect `docker compose -p capstone-accelerator logs worker` and `docker compose -p capstone-accelerator ps`. If the worker is healthy but the job was never queued, explicitly retry the scoped ID with POST `/documents/ID/retry`. Do not mark it ready by editing the database.

## Exercise 2 — persistence and ownership

Save the ID from check.py. Recreate the API and worker without deleting volumes:

```bash
docker compose -p capstone-accelerator up -d --force-recreate api worker
```

Read the same document with `demo-one`; it must still be ready. With `demo-two`, both the status route and `/ask` must return 404. A recreated process is not a recreated database. Do not use `down -v` for this check.

Feedback: if a new ID appears, you reran check.py instead of reading the saved ID. If the other owner can see the row, inspect the scope predicate before looking at ranking.

## Exercise 3 — fresh PostgreSQL restoration

First run check.py so synthetic rows exist. These commands create a separate restore database and refuse to overwrite an existing dump or database:

```bash
test ! -e accelerator-review.dump
docker compose -p capstone-accelerator exec -T db pg_dump -U learner -d accelerator_lab -Fc > accelerator-review.dump
docker compose -p capstone-accelerator exec -T db createdb -U learner accelerator_restore_review
docker compose -p capstone-accelerator exec -T db pg_restore -U learner --no-owner -d accelerator_restore_review < accelerator-review.dump
docker compose -p capstone-accelerator exec -T db psql -U learner -d accelerator_restore_review -v ON_ERROR_STOP=1 -c 'SELECT id,org,state,digest FROM documents ORDER BY id'
docker compose -p capstone-accelerator exec -T db psql -U learner -d accelerator_restore_review -v ON_ERROR_STOP=1 -c 'SELECT document_id,position,text FROM chunks ORDER BY document_id,position'
```

Compare IDs, digests and text with the source database, not merely counts. Run the same SELECTs against `accelerator_lab`. A restore that produces the same count but different text fails this exercise. This drill never restores into the live lab database.

## Exercise 4 — rate, cost and context decisions

This lab has an input-size cap, shared per-organization Redis request limiter and bounded worker concurrency. It must remain local because its identities are fixed demo tokens. Before public deployment, replace demo authentication and define a total provider deadline, queue admission cap and model spending cap. The Redis limiter is a fixed window; it does not guarantee smooth traffic or upstream model capacity. Implementing a public service is a separate extension after its mechanisms are taught, not a hidden acceptance condition for this bounded lab.

Compare accepted and rejected requests, include failure time in elapsed duration, and record provider cost as not applicable because no model is called. Context uses characters here; compare it with a tokenizer before naming a token limit. Cache keys must include authenticated organization, immutable source digest, prompt and model version. Deletion must invalidate chunks and cached answers.

### Observe overload feedback

After the other exercises, make 61 authenticated GET requests within one minute using a demo identity. Earlier requests count toward the same window. Observe the first 429 with Retry-After, and wait for the fixed window to expire before repeating. A denied or missing document still consumes request quota. The Redis script sets expiry with the first increment atomically, preventing a crash between increment and expiry from leaving a permanent counter. A strict distributed token bucket would be a separate algorithm and evaluation.

## Finish the lab

```bash
docker compose -p capstone-accelerator down
```

Named lab volumes remain for later study. No command targets the academy or Workshop Compose project.

## Implementation references

The teaching and complete code are above. These official references document framework behavior: [Celery task delivery, retries and timeouts](https://docs.celeryq.dev/en/stable/userguide/tasks.html), [Psycopg transaction contexts](https://www.psycopg.org/psycopg3/docs/basic/transactions.html), and [Alembic migration environments](https://alembic.sqlalchemy.org/en/latest/tutorial.html). SDK snapshots are pinned for this example; transitive dependencies resolved during verification are recorded in tested-environment.txt.


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
