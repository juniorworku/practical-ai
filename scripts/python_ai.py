"""Author the independent advanced Python program, preserving other course books."""
import hashlib
import ast
import json
from python_ai_solutions import solution
from python_ai_checks import CHECKS
from python_ai_studios import STUDIOS, studio, measurement
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/academy/content/capstones/python-for-ai'
ENTRY = 'Already write Python functions/classes, use a virtual environment, read tracebacks, run assertions, understand HTTP/JSON and basic SQL. This is an advanced engineering course, not a first programming course. Use Python 3.12. No calculus or model-training background is required.'
# title, module, three concepts, guided teaching, extension, failure, scenario answer/alternatives/explanation
ROWS = [
('Typed boundaries and replaceable providers','01 · Contracts and streaming',
 [('Runtime validation','Type hints describe expectations to tools; they do not reject untrusted runtime values. Validate before allocating provider work.'),('Immutable records','A frozen dataclass prevents attribute reassignment, not mutation of nested lists or dictionaries.'),('Structural interfaces','A Protocol describes required methods without forcing an adapter to inherit from a framework.')],
 '''## Start at the boundary, not at the model
An AI service accepts untrusted data and hands it to expensive dependencies. Treat the request as a contract with a small set of allowed fields. In the example, owner is supplied by trusted application code; query is the only user-controlled value. In the HTTP capstone, credentials determine owner. A type annotation is documentation and static-checker input, so the dataclass still needs a runtime invariant.

## Trace the construction path
1. Python binds the constructor arguments to owner and query.
2. The generated dataclass initializer stores them, then calls __post_init__.
3. The invariant rejects a non-string, empty/whitespace-only query or an excessive character count before an adapter runs.
4. A valid instance is frozen. You can pass it through layers without allowing a downstream function to reassign its query accidentally.
5. The Provider protocol specifies an asynchronous answer method. A fake and a network adapter can satisfy that shape independently.

## Make validation executable
First predict which constructor calls raise. Then run the specimen and compare the observed exception type with the invariant. Add separate cases for a missing value, whitespace, an integer and the exact maximum length. Keep invalid input separate from upstream unavailability: changing the model will not repair a malformed request. Character limits here are an input guard, not token accounting.

## Common mistake: trusting the annotation
A function accepting request: Request can still be called incorrectly at runtime. At an API boundary parse allowed fields explicitly and validate them. Do not deserialize a model-generated owner into a privileged request. Use Protocol for dependency replacement; add an integration test because structural typing does not prove that a remote service behaves correctly.''',
 'Add an explicit owner allowlist containing team-a and team-b. Reject an unknown owner before provider work. Preserve valid-query behavior.',
 'Change query to a list and then to 2001 characters; both must fail. Restore a valid query of exactly 2000 characters and explain why it passes.',
 'A typed request accepts an empty query in production. What should change?', 'Add runtime validation at construction or parsing before the provider call.', 'Switch to a larger model.', 'Assume the annotation will reject empty strings.', 'Python does not enforce a string annotation or its business invariants at runtime. A model swap adds cost without repairing the boundary.'),
('Streaming records without buffering the world','01 · Contracts and streaming',
 [('Framing','Network chunk boundaries do not identify complete JSON records; a delimiter or explicit length frames each record.'),('Backpressure','A consumer should pull bounded work rather than eagerly materialize an unbounded stream.'),('Completion evidence','A partially received stream is not a completed answer; validate the final framing and provider completion signal.')],
 '''## Separate transport chunks from application records
A socket may deliver half a UTF-8 character, three records at once or the beginning of the next record. Decoding each received byte chunk immediately is unsafe. The generator holds bytes until it sees a newline, decodes one complete JSON record and yields it. The caller decides when to request the next record. This is lazy iteration; list(records(...)) is used only for the tiny test fixture.

## Follow the buffer across yields
1. Append the incoming byte chunk to pending.
2. While a delimiter exists, split exactly one record from the remaining bytes.
3. Enforce the record-size limit, skip blank framing lines and parse JSON.
4. Yield the parsed record. Execution pauses here until the consumer resumes.
5. Check the unfinished remainder after each chunk. At end of stream, reject a non-empty unfinished record instead of fabricating a closing brace.

## Observe a split character
The fixture splits café between its two UTF-8 bytes. Because decoding happens after framing, the record remains intact. Remove the last newline to observe a controlled truncation failure. A newline only establishes transport completeness for a record; an actual provider's done flag is a separate semantic signal. Never cache a token fragment as a final answer.

## Bound every layer
max_line bounds an application record after a chunk arrives; it does not bound the chunk allocated by the HTTP client before this function runs. Configure the transport chunk size and overall response budget too. In an async adapter, await consumption and propagate cancellation when the client disconnects. A stream lowers time to first output but may increase assembly complexity and retry waste; measure both first-output latency and total accepted-answer latency.''',
 'Add a maximum record count of two. Stop with ValueError when a third complete record arrives, without silently truncating it.',
 'Feed a missing final newline, a malformed JSON record and a line one byte above max_line. Assert each fails for the expected reason.',
 'A stream sends half of a multi-byte character. How should the parser behave?', 'Retain bytes until a complete framed record is available, then decode.', 'Decode each chunk independently.', 'Discard undecodable bytes.', 'Chunk boundaries are arbitrary. Discarding bytes silently corrupts evidence; framing plus bounded buffering preserves exact content.'),
('Bounded async pipelines and ordered results','02 · Concurrency and recovery',
 [('Worker pool','A fixed number of long-lived consumers bounds active work rather than creating one task per input.'),('Queue pressure','A bounded asyncio.Queue suspends the producer when consumers cannot keep up.'),('Structured concurrency','TaskGroup owns child-task lifetimes and waits for cleanup; a failing child cancels its siblings.')],
 '''## Why a semaphore alone is insufficient
Creating a million tasks and putting a semaphore inside each task still allocates a million task objects. A queue and fixed workers bound both admission and active execution. The example preallocates output slots for a known, deliberately bounded batch; for an unlimited source, emit results to a bounded downstream sink instead.

## Follow producer and consumers
1. The producer enumerates each value and awaits queue.put. A full queue suspends it without blocking the event loop.
2. Two consumer tasks wait for work. Each increments active only while processing an item.
3. Work completes with an await, allowing another consumer to run. This is concurrent I/O-style scheduling, not proof of CPU parallelism.
4. Each consumer stores its output at the original input index, so completion order cannot reorder the returned batch.
5. The producer sends one sentinel per consumer. Every get, including sentinels, has exactly one task_done in finally.
6. TaskGroup exits only after its producer and consumers finish or cancellation cleanup completes.

## Measure the bound
The assertion checks peak active work, not a claimed requests-per-second number. A zero-second sleep yields control; it does not emulate a real provider's latency or rate limit. Change workers and queue capacity independently, then record peak, queue waiting and total latency with a realistic fake delay.

## Error policy is a product decision
Fail-fast cancellation is appropriate when a batch must be all-or-failed. A partial-results API needs explicit per-item statuses and restart semantics; do not catch every exception and replace failed items with success-shaped nulls. If one consumer fails while the producer waits on a full queue, structured concurrency must cancel the producer too.''',
 'Reject workers outside 1–4 before starting tasks. Run 100 items with three workers and assert ordered outputs and peak <= 3.',
 'Raise ValueError for one selected input. Assert the TaskGroup raises an ExceptionGroup and no consumer continues running after it exits.',
 'A service creates 100000 tasks then uses a semaphore of four. What remains unbounded?', 'Task-object allocation and queued inputs; use a bounded producer and fixed workers.', 'Only the number of CPU cores.', 'Nothing; the semaphore limits memory too.', 'The semaphore restricts entry to its protected work but does not prevent eager task allocation or input materialization.'),
('Deadlines, cancellation and cleanup','02 · Concurrency and recovery',
 [('Overall deadline','A timeout around the operation bounds cumulative waiting, including retries, rather than restarting a timer per attempt.'),('Cooperative cancellation','An async task responds at suspension points; blocking Python code can prevent timely cancellation.'),('Resource cleanup','finally runs on normal exit and cancellation; acquired resources must be released along every path.')],
 '''## A deadline is a lifetime boundary
The provider fixture sleeps for a minute; the caller allows only 20 milliseconds. asyncio.timeout cancels the enclosed task when its deadline expires. Outside the context this becomes TimeoutError. The provider's finally sets cleaned, so the test verifies cleanup rather than merely measuring that an exception appeared.

## Run and inspect the control flow
1. Enter the timeout context before awaiting the dependency.
2. The provider suspends, so the loop can run its deadline callback.
3. Cancellation reaches the provider at the await.
4. Its finally runs and marks cleanup complete.
5. The caller receives TimeoutError outside the context and verifies that no success response escaped.

## Preserve cancellation
Do not catch BaseException or CancelledError and return a plausible answer. In a task group, suppressing cancellation can leave other work waiting indefinitely. Cleanup should be short and should not perform an unbounded network request. If cleanup itself needs I/O, give it a separate small budget and record an unresolved resource if it fails.

## Blocking work has different semantics
asyncio.to_thread moves a blocking call off the event loop, but cancelling the awaiting coroutine does not stop the underlying thread. A CPU-bound pure Python loop may need a process worker with admission control. An HTTP client should support native async cancellation plus connect/read/write timeouts. The capstone uses async HTTP for model requests and small off-loop SQLite operations; cancellation does not roll back an already committed cache write.

## Test time deterministically where possible
This fixture asserts cleanup and error type, not an exact 20ms observed latency. Shared machines can schedule later. Use virtual clocks or injected timers for a large timing matrix, and separately measure real deadline overshoot under load.''',
 'Wrap two sequential provider attempts in one overall timeout and prove the second attempt cannot restart the full budget.',
 'Cancel a parent task explicitly. Verify the same cleanup event is set and CancelledError reaches the parent rather than a success value.',
 'Cancelling a coroutine awaiting to_thread returns promptly. Has its thread stopped?', 'No; the thread may continue, so its own timeout and resource bounds still matter.', 'Yes; Python forcibly terminates the thread.', 'Yes, if its function has type hints.', 'Coroutine cancellation and thread termination are different. Design blocking calls with their own timeouts and avoid claiming rollback of completed effects.'),
('Provider adapters with honest usage contracts','03 · Providers and evidence',
 [('Dependency injection','Pass a provider interface into application code so fixed fakes and real transports exercise the same boundary.'),('Response validation','A 200 HTTP status is insufficient: validate completion, field types, output limits and usage values.'),('Unknown usage','Missing token counts are unknown, not zero; estimates and measured provider usage must remain distinct.')],
 '''## Keep network details outside application policy
The application accepts an Adapter instead of importing a vendor SDK throughout the codebase. Its fake returns a complete typed Result without network calls. This lets a test verify timeout placement and output validation independently of nondeterministic model text. The fake is a contract test double, not an AI capability claim.

## Replace the dependency deliberately
1. Construct an adapter with operator-controlled model and endpoint configuration.
2. Build messages from a bounded query and authorized evidence. Evidence is data, never an instruction source.
3. Use an async HTTP client with connect and operation timeouts; reject non-success status codes.
4. Require a completed response with non-empty text and a bounded output length.
5. Preserve supplied prompt/output token counts, or null when absent. Log no secrets or private question bodies.
6. Return the typed result to the application, which applies its own source and cache policy.

## Read the complete real adapter
The additional chapter below publishes OllamaProvider from the final service. It uses /api/chat with stream false and a capped output request. Install the shown dependency only in your isolated workspace. An installed model and its server are separate prerequisites; enrollment does not include compute. Run the fake first, then opt into a supported local model and record its actual behavior.

## Separate transport correctness from semantic quality
A model can return valid JSON containing an unsupported answer. An allowed source ID is a routing invariant, not proof that every generated claim is entailed. Keep automated schema/source checks deterministic and add a labeled semantic review before accepting a real provider. Changing models invalidates the comparison baseline and cache namespace.''',
 'Add a fake returning an empty text and assert application validation rejects it. Then return a valid answer with unknown usage and ensure usage stays null.',
 'Use an installed local model optionally, disconnect its server and verify the application surfaces an unavailable outcome without caching success.',
 'A provider omits token counts. What should the report store?', 'Unknown values plus a separate labeled estimate if needed.', 'Zero cost and zero tokens.', 'The query character count as measured tokens.', 'Absent measurement is not zero consumption. Character counts are not tokenizer counts and local compute still has operational cost.'),
('Retry budgets and idempotent boundaries','03 · Providers and evidence',
 [('Retry classification','Retry only a documented transient failure for a safe operation; input and authorization failures should surface immediately.'),('Bounded backoff','Limit attempts and cumulative elapsed time, and account for the delay between attempts.'),('Uncertain effects','A missing acknowledgement does not prove a remote write failed; reconcile by stable operation identity before replaying it.')],
 '''## Retry a read, not every exception
The example deliberately raises a custom TransientRead twice. retry_read catches only that class, waits using exponential delays and returns the third response. PermissionError is outside its retry policy and escapes immediately. The application wraps the complete retry loop in one overall deadline from the previous lesson.

## Count attempts as work
1. Validate the retry budget before creating work.
2. Call the dependency and return only a completed result.
3. On an explicitly transient error, check whether any attempts remain.
4. Await the bounded delay so other tasks can proceed.
5. Let the final failure propagate; do not turn exhaustion into an empty successful record.

## Adapt to actual HTTP outcomes
An authorized policy read may retry a 503 or a 429 after a bounded Retry-After value. A 401 requires fixing identity, not increasing attempts. Reject unreasonable server delays against the remaining deadline. In production add jitter with an injected random source so tests can fix the schedule, and capture each attempt's duration and usage.

## AI generation and writes need care
Repeating generation can spend compute twice and produce different text. The final capstone therefore does not silently retry generation. A message-send, payment or calendar write has stronger risks: after a timeout, retain uncertain state and reconcile the original destination using its operation key. A local cache cannot undo a remote action.

## What the test establishes
The fixture proves attempt classification and exhaustion behavior. It does not prove provider-side idempotency or distributed exactly-once delivery. Later release evidence must distinguish a replay-safe read, paid computation and an external effect.''',
 'Make the safe read fail on every attempt; assert exactly three calls and the final TransientRead. Keep the overall deadline outside the retry function.',
 'Raise PermissionError on the first call and count calls; the count must stay one. Add a canceled-parent case that stops waiting immediately.',
 'A remote calendar write times out after submission. What comes next?', 'Record uncertainty and reconcile the original operation before deciding whether to replay.', 'Retry forever until any 200 response appears.', 'Assume timeout means no write occurred.', 'The destination may have committed the write before its acknowledgement was lost. Replaying blindly can duplicate the effect.'),
('Grounding pipelines and context selection','04 · Context and persistence',
 [('Owner-first filtering','Apply trusted ownership before ranking candidates; retrieving then filtering can leak data through results or logs.'),('Stable ranking','Use a documented score and deterministic tie-breaker so fixed retrieval cases are repeatable.'),('Context admission','A candidate must fit the context policy and have an identified source; absence should produce abstention.')],
 '''## Separate candidate eligibility from relevance
The fixture contains conflicting refund policies for two owners. The loop checks owner before computing a lexical score. Even a highly matching unauthorized document cannot enter the candidate list. Model instructions cannot replace this application-side authorization boundary.

## Trace one query through the stages
1. Normalize query terms with a documented tokenizer. This regex tokenizer is for lexical matching, not a model token budget.
2. Skip documents outside the authenticated owner.
3. Count unique overlapping terms for eligible candidates.
4. Reject candidates over this fixture's character budget rather than silently cutting a source mid-exception.
5. Sort by decreasing overlap and stable source ID, then keep the top two.
6. Return no context when nothing qualifies. The caller must abstain rather than search another owner's data.

## Understand this baseline before replacing it
A lexical retriever is cheap and auditable but misses synonyms and semantic relationships. A vector index adds model/version/dimension contracts and can cost more latency and maintenance. Compare both on the same labeled queries before claiming an improvement. Source selection quality, answer faithfulness and access control are separate measurements.

## Context windows need explicit allocation
A real prompt needs room for instructions, tool schemas, history, evidence and output. Use the selected model's tokenizer to allocate tokens and preserve source locators. Character and transport-byte guards in these examples protect memory but do not guarantee model-window fit. Record refused oversized evidence so a silent truncation cannot look like a grounded answer.''',
 'Add a second team-a document with an equal overlap score and verify source-ID tie ordering. Keep the conflicting team-b policy excluded.',
 'Reduce the context guard below the policy length. Verify abstention rather than a truncated, misleading policy answer.',
 'A private document scores highest for another owner. Which ordering is correct?', 'Authorize eligible documents first, then rank within that set.', 'Retrieve globally and ask the model to hide private results.', 'Log every retrieved document before filtering.', 'Authorization controls eligibility. Later filtering cannot undo private data already placed in a prompt, result or log.'),
('Versioned caches without cross-tenant reuse','04 · Context and persistence',
 [('Cache identity','Include trusted owner, model identity, prompt revision, source revision and normalized request in the cache contract.'),('Invalidation','A changed dependency requires a changed namespace; time-to-live alone cannot establish current evidence.'),('Completed-only writes','Cache only validated completed results; fragments and upstream failures must never become success entries.')],
 '''## A cache key is part of correctness
The example serializes the exact dependency tuple and hashes it. Stable field ordering and an explicit tuple shape make the identity reproducible. The hash is not authorization or encryption; owner checks are still necessary at read time. Do not put private input text in an observable cache-key label.

## Predict the hits before running
1. Write one answer for owner a using fixture-v1, source-v1 and prompt-v1.
2. Change owner only. The key must miss even if query text is identical.
3. Change the source revision only. The old answer must miss because its policy may have changed.
4. Change model identity. The comparison and cached output now belong to a different computation.
5. Repeat the original tuple. This is the one expected cache hit.

## Measure the actual trade-off
Caching can reduce latency and compute but can amplify stale or unauthorized answers. Measure hit rate, accepted-answer quality and invalidation failures together. A cache hit has lookup cost; do not report it as zero latency. An uncached failed attempt still consumed resources even if no entry was written.

## Be explicit about mutable dependencies
A model tag can point to different weights after an update. Production keys should use an immutable model digest or an operator-maintained release revision. If a provider silently changes behavior, a tag-only key is insufficient. The capstone calls out this limitation rather than pretending its local tag is immutable.

## Persistence comes next
This dictionary intentionally loses all entries when the process exits. Lesson 9 adds transactional SQLite storage and owner predicates. Do not claim restart recovery based on a dictionary hit in the same interpreter.''',
 'Add an output-schema revision to the key. Change it and assert a miss while the original schema revision still hits.',
 'Remove the source revision temporarily and show the stale-hit counterexample after a policy change. Restore the dependency before continuing.',
 'A prompt changed but cached answers still appear. What is missing?', 'Prompt revision in cache identity and a tested invalidation path.', 'A faster dictionary implementation.', 'More threads around the same stale key.', 'Speed does not repair stale dependency identity. New prompt behavior must not reuse a result computed under the old contract.'),
('Durable state, transactions and resource ownership','04 · Context and persistence',
 [('Connection ownership','Opening, transaction scope and closing are distinct; a SQLite connection context alone does not close it.'),('Parameterized queries','Bind untrusted values as SQL parameters instead of assembling executable query text.'),('Durable identity','A composite owner/key primary key prevents one owner from overwriting another owner’s entry at the same logical key.')],
 '''## Prove readback after replacement
The specimen creates a temporary database, writes a row, commits, closes the connection and opens a new connection. The second owner cannot read the first owner's row even when it knows the logical key. This is stronger evidence than reading from the same in-memory dictionary.

## Follow transaction and lifetime separately
1. Open a connection for one unit of work.
2. Create the schema and insert with bound parameters.
3. Exit the transaction context so a successful unit commits; an exception rolls it back.
4. Close the connection explicitly. Python's SQLite connection context manages transactions, not its entire resource lifetime.
5. Reopen and execute an owner-bound SELECT.
6. Close the reopened connection before removing the temporary directory.

## Design for concurrent application code
Use a fresh connection per operation rather than sharing a default thread-bound connection across request threads. Keep write transactions short. Set a bounded busy timeout and surface lock contention as an unavailable operation; a busy timeout is not distributed admission control. Offload small blocking SQLite operations from the async event loop, remembering that cancellation cannot forcibly stop a thread already committing.

## Recovery is not just persistence
A database file surviving restart does not establish a tested backup. Before trusting stored evidence, copy a consistent snapshot using SQLite's backup API, open the restored database and compare scoped records. Never copy a live database file casually and assume its journal/WAL state is complete. The capstone uses a dedicated Docker volume and no shared academy data.

## No remote exactly-once claim
A local commit cannot atomically encompass an unrelated external API. For writes beyond this cache, teach an outbox/inbox and reconciliation policy before claiming durable delivery. Here the only persisted result is a completed read-style computation.''',
 'Attempt two inserts with the same owner/key and assert the primary key rejects the duplicate. Roll back and prove the first committed value is unchanged.',
 'Raise after an insert inside a transaction and verify no row is committed. Close every connection on both success and failure.',
 'Does leaving with sqlite3.connect(...) automatically close its connection?', 'No; it manages transaction commit/rollback, while closing is a separate lifetime responsibility.', 'Yes, always.', 'Only when the query includes a WHERE clause.', 'Connection context-manager semantics differ from file contexts. Use explicit close or a contextmanager that closes in finally.'),
('Deterministic evaluation and performance evidence','05 · Evaluation and service boundaries',
 [('Fixed cases','Hold expected labels and test cases constant while comparing implementations; do not edit expectations to fit observed output.'),('Tail latency','p50 describes the middle; p95 exposes slower cases and needs a declared quantile method and sufficient observations.'),('Layered quality','Schema/source/authorization checks can be deterministic while semantic faithfulness still needs a separate labeled review.')],
 '''## Make one failure visible
The fixed cases contain a deliberately wrong isolation source. The report must show 75% source accuracy and identify isolation as failed. A useful evaluation preserves this failure rather than hiding it inside a single average or replacing the expected source.

## Construct the report step by step
1. Version each case family and its expected source identity.
2. Run the same cases through the changed system.
3. Compare exact source decisions, including explicit no-source outcomes.
4. Keep individual failed case names so a developer can reproduce them.
5. Compute the median and a declared nearest-rank p95 over the latency list.
6. Label all supplied latencies as synthetic. They are not measured provider response times.

## Separate timing from assertions
Use monotonic perf_counter around real operations. Capture queue waiting, provider duration, storage and whole-request latency when instrumenting the capstone. Retain timeout/error outcomes instead of calculating latency only for successful answers. Four fixture samples demonstrate the formula; they cannot support a stable production p95 claim.

## Evaluate changes under one budget
Compare a cached path, a larger model or a retrieval change on fixed cases, with a declared quality floor and resource allowance. Count failed attempts and retries in cost per accepted answer. If local usage counts are missing, report unknown token consumption and measure local resources separately.

## Semantic checks remain a different layer
Exact citation equality does not prove an answer is faithful to its citation. Use human-labeled claim support or a versioned model judge with recorded disagreement. Avoid calling a stochastic judge deterministic truth. Graduation needs both repeatable engineering checks and an honest semantic-quality scope.''',
 'Add one unsupported-answer case and retain the intentionally failing isolation case. Compute the new score by hand before changing the test.',
 'Change observed isolation to the expected value, rerun and show the failure disappears without changing any expected labels.',
 'Four synthetic timings give a p95 of 80ms. What can you claim?', 'The fixture quantile calculation is correct, not a production latency guarantee.', 'The deployment will serve thousands of users below 80ms.', 'The model’s quality improved.', 'A tiny synthetic sample verifies a calculation. Real tail-latency evidence requires measured representative traffic, failures and sufficient observations.'),
('HTTP contracts, admission and readiness','05 · Evaluation and service boundaries',
 [('Readiness','A health response should identify what was actually checked, such as local database access, without claiming provider readiness.'),('Admission control','Bound active expensive requests separately from request-size, per-owner rate and per-batch worker limits.'),('Trusted identity','Derive owner from verified credentials and operator policy, never from a client’s requested owner field.')],
 '''## Put a callable program behind a real boundary
The complete example starts an actual local HTTP server on a random free port, sends a request and shuts it down. This verifies serialization and status behavior through a network boundary. It does not claim a production server, TLS or a working model endpoint.

## Trace the lifecycle
1. Bind only loopback, with port zero asking the operating system for an available port.
2. Start the server in a separate thread so the test can act as a client.
3. Send a GET with a finite client timeout and decode JSON.
4. Assert exactly what readiness promises: the local handler responded, while provider_checked remains false.
5. In finally, stop accepting requests, close the socket and join the worker. Assert no thread was left alive.

## Add controls in the right order
The final service checks path and bearer credentials, derives owner, applies an owner rate window, then attempts a global processing slot. It validates Content-Length and the exact JSON shape before starting a bounded batch. An input error should produce 400/413, an invalid identity 401, exhausted quota 429 and capacity/unavailable outcomes 503/502. Never accept an owner supplied in the body.

## Distinguish the limits
Two simultaneous requests times three workers permits up to six provider operations in one process. The quota limits request arrivals, not total tokens or globally distributed spend. ThreadingHTTPServer can still create request threads before application admission; a public release needs an upstream connection/request limit and a production server. Multiple replicas need a shared limiter and state strategy.

## Keep operational signals honest
A database SELECT can establish local readiness. A model tag in an environment variable cannot establish that the model is installed or has capacity. Separate health, dependency checks and task success, and redact credentials/questions in server logs.''',
 'Send a request to an unknown path and assert 404 using urllib.error.HTTPError. Preserve cleanup even when the probe fails.',
 'Stop the server before probing and verify the client fails instead of returning ready. Explain why readiness is time-specific evidence.',
 'Each of two replicas permits ten requests per minute in memory. Is the service globally limited to ten?', 'No; process-local counters are independent and need shared enforcement for a global quota.', 'Yes; identical Python constants synchronize them.', 'Yes; Docker automatically shares dictionaries.', 'Processes do not share ordinary in-memory state. Replica count changes the effective quota unless admission is coordinated.'),
('Capstone: a bounded, grounded Python service','06 · Integrated delivery',
 [('Integration evidence','Passing isolated functions is necessary but insufficient; exercise browser/client → HTTP → provider/storage → response and restart behavior.'),('Release scope','Mark every requirement passed, failed or untested and limit claims to the deployment and provider actually observed.'),('Reproducible delivery','Publish complete files, dependency versions, commands, test cases and recovery steps so another operator can repeat the result.')],
 '''## Build the service from what you have already learned
This final project combines request contracts from session 1, bounded workers from session 3, deadlines from session 4, the real/fake provider boundary from session 5, authorized context from session 7, versioned keys from session 8, SQLite lifetime management from session 9, evaluation from session 10 and the HTTP lifecycle from session 11. The complete project chapter below contains every file; no other academy program is required.

## Assemble in stages
1. Create a fresh scratch directory and save pipeline.py and test_pipeline.py. Run the fixed tests before adding a server.
2. Trace owner and source IDs through supported and missing-context queries. Inject a provider returning another owner's source and verify no cache write.
3. Save server.py, configure two independent test credentials and probe the HTTP boundary. Keep the keys outside committed files.
4. Repeat supported requests and verify cache hits, then restart the process and verify readback using the same database path.
5. Run malformed JSON, extra owner field, unknown identity, oversize batch, timeout and capacity tests. Record the actual status and unresolved failures.
6. Build the provided image, attach a dedicated volume and rerun probes after container replacement.
7. Optionally select an installed Ollama model, then rerun transport checks and a separately labeled semantic evaluation. Fixed extraction does not establish real model quality.

## Review the deliberately incomplete evidence example
The small release-gate specimen returns local fixture demonstration only because load and model-semantic evidence are absent. This is a decision record, not the capstone implementation. Passing that assertion alone never completes this project. The full files and integration probes are mandatory.

## Explain the operating envelope
The reference is a single-process local deployment. Its policy file, SQL state, credential map and rate counters have explicit ownership and limits. Public scaling requires TLS, managed identity, shared admission, tested backups and measured capacity. Explain which of those you implemented, which you tested and which remain outside the release, instead of treating Docker as proof of production readiness.''',
 'Build the complete files below, run all unit tests and HTTP probes, replace the container, then demonstrate persisted cache and owner isolation. Keep one failed/corrected case.',
 'Change the provider identity and source revision separately; each must miss the previous cache. Remove a required release proof and ensure your graduation record is blocked or limited.',
 'The fixture tests pass, but no real model or load test ran. What is the defensible release scope?', 'A verified local fixture demonstration, with model quality and production capacity explicitly untested.', 'A production-ready globally scalable AI service.', 'An automatic semantic-quality certification.', 'Evidence supports only observed behavior. The project must not turn local contract checks into claims about model faithfulness or unmeasured cloud capacity.')]

def build():
    program = dict(slug='python-for-ai', title='Python for AI', category='Advanced', order=6,
      description='Advanced Python for reliable AI applications: typed interfaces, bounded async pipelines, streaming, model adapters, owner-scoped context, durable state and measured deployment. Build and test the software around the model.',
      audience='Practicing Python developers who want to engineer AI services beyond notebooks. Python, HTTP/JSON, tests and basic SQL are required.',
      outcome='A tested, containerized knowledge service with bounded concurrency, optional real local-model inference, owner isolation, persistent versioned cache and a reproducible evaluation/recovery runbook.',
      duration='8–12 weeks · self-paced', level='Advanced · Python, HTTP, tests and SQL required', lessons=[], _capstone='bounded knowledge service')
    for index, row in enumerate(ROWS, 1):
        title, module, concepts, teaching, extension, failure, prompt, right, wrong1, wrong2, why = row
        advanced = STUDIOS[index-1]
        teaching = teaching.replace('typed Result','typed Reply').replace('Adapter instead','Provider instead').replace('Result without','Reply without')
        code = (ROOT/f'scripts/python_ai_examples/{index:02}.py').read_text()
        prerequisites = {1:'Before enrolling, independently parse a JSON dictionary, write a function/class, run a failing unittest and a parameterized SQLite query, and explain HTTP status vs response data. If those are new, strengthen working Python first. Async scheduling is taught here, not assumed.',2:'Bring the exact-schema and immutable request checks from session 1.',3:'Bring the bounded stream/record checks from session 2; distinguish lazy input from an eagerly allocated task per input.',4:'Bring the TaskGroup failure/cleanup test from session 3.',5:'Bring response-byte bounds from session 2 and cancellation/deadlines from session 4.',6:'Bring the distinct provider error contract from session 5 and overall deadline from session 4.',7:'Bring trusted query identity from session 1 and the evidence/usage contract from session 5.',8:'Bring owner-first selection and complete context allowance from session 7, plus provider identity from session 5.',9:'Bring the full dependency cache key from session 8 and thread-cancellation limits from session 4.',10:'Bring the assembled pipeline.py and restored-snapshot checks from session 9.',11:'Bring pipeline.py from session 9 and evaluate.py with fixed cases from session 10. HTTP/JSON is an entry skill; server factory, locks, slots and status classification are taught below.',12:'Bring pipeline.py, the versioned evaluation report and the complete HTTP boundary from sessions 9–11. Preserve the earlier baseline and failure transcripts.'}[index]
        chapter_intro = f'''## Before this session

{ENTRY if index==1 else 'Complete sessions 1–'+str(index-1)+' first. Bring the previous assertions, failure notes and versioned scratch workspace. New Python mechanisms are explained before the exercise below.'}

## Bring these checked capabilities

{prerequisites}

## What you will be able to do

{teaching.split('## ')[1].split(chr(10),1)[-1].strip().split(chr(10)+chr(10))[0]}

## Your route through this lesson

Read the concept explanation, predict the complete example, run it unchanged and inspect its failure case. Only then attempt the assigned variation. Save exact commands and observed output; a checked box is a self-report, not a runtime test.
'''
        worked = f'''## Predict before executing

Use a fresh directory, Python 3.12 and a virtual environment. Save the entire block as lesson.py and run `python -I lesson.py` with assertions enabled. This specimen uses only the standard library; do not install a model package to repair a failing assertion. Session 11 briefly binds a loopback test server and closes it in finally. Other specimens use synthetic data and make no provider calls.

```python
{code.strip()}
```

## Read the assertions as the contract

Follow each assertion back to the corresponding teaching step. Run the file twice from a fresh interpreter. Explain its printed outcome in your own words and distinguish fixture values from measured values. If a traceback appears, retain it and locate the earliest violated invariant before changing the implementation.

## Deliberate failure experiment

{failure}

## What this does not establish

The executable specimen tests this session's named mechanism. It does not establish semantic model quality, paid-provider availability or production capacity. The final integrated service requires the taught components and its full acceptance procedure, not just these assertions.
'''
        practice = f'''## Input and baseline

Use the exact complete specimen in the worked-example chapter. Keep a clean copy as baseline.py and copy it to exercise.py. Run the unchanged baseline and save its output before editing. Do not concatenate files from previous sessions; move a helper only after its input/output contract is explicit.

## Your implementation task

{extension}

## Verification procedure

1. Write the expected valid and invalid outcomes before changing code.
2. Preserve every original assertion in the baseline and add a failing assertion for the new requirement.
3. Implement only the assigned boundary. Run `python -I exercise.py` and retain the actual result.
4. Run the deliberate failure: {failure}
5. Restore the valid path and run both files again. Record any behavior you have not tested.

## Diagnostic feedback

If the baseline fails, check interpreter version, copied imports, indentation and exact input before changing the algorithm. If the extension passes only the happy path, isolate the negative case as its own assertion. If results change between runs, locate shared mutable state, missing cleanup or an unstated timing assumption. Do not weaken an expected label just to obtain a pass.

## Bring forward

Retain the implementation contract, one negative-case assertion and its failure/repair evidence. The capstone coverage map names where this capability is reused.
'''
        chapters = [dict(id='preparation',title='Prerequisites and learning outcomes',kind='Learning path',body=chapter_intro),dict(id='concept-tutorial',title='Learn each concept step by step',kind='Guided concept teaching',body=teaching),dict(id='worked-implementation',title='Complete example: predict, run, inspect',kind='Runnable example and failure analysis',body=worked),dict(id='practice',title='Build the assigned variation',kind='Guided implementation',body=practice),dict(id='engineering-pillars',title='Measure the engineering decision',kind='Production review',body=measurement(index))]
        chapters.insert(3,studio(index))
        if index == 5:
            source=(BASE/'pipeline.py').read_text()
            tree=ast.parse(source)
            lines=source.splitlines()
            definitions=[]
            for node in tree.body:
                if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in {'Reply','ProviderError','validate_reply','OllamaProvider'}:
                    start=min([node.lineno]+[d.lineno for d in node.decorator_list])-1
                    definitions.append('\n'.join(lines[start:node.end_lineno]))
            provider_source='import os, json, asyncio\nfrom dataclasses import dataclass\n\n'+'\n\n'.join(definitions)
            provider_source += """

async def main():
    import httpx
    evidence={'id':'p1','text':'Unused items may be returned within 14 days.'}
    def respond(request):
        payload=json.loads(request.content)
        assert payload['stream'] is False and payload['messages'][1]['role']=='user'
        return httpx.Response(200,json={'done':True,'message':{'content':'14 days'},'prompt_eval_count':11,'eval_count':3})
    fake=OllamaProvider('offline-test-tag',transport=httpx.MockTransport(respond))
    result=await fake.answer('refund window?',evidence)
    assert result==Reply('14 days','p1',11,3)
    bad=OllamaProvider('offline-test-tag',transport=httpx.MockTransport(lambda request:httpx.Response(503)))
    try:await bad.answer('refund window?',evidence)
    except ProviderError:print('Offline HTTP transport success and failure contracts verified')
    else:raise AssertionError('upstream failure became success')
    if os.environ.get('RUN_LIVE_MODEL')=='1':
        real=OllamaProvider(os.environ['OLLAMA_MODEL'])
        print(await real.answer('refund window?',evidence))
if __name__=='__main__':asyncio.run(main())
"""
            chapters.insert(4,dict(id='real-provider',title='Complete adapter: offline contract first, optional local model',kind='Real integration',body="""## Run the complete adapter without a model first

Use a virtual environment and install `python -m pip install httpx==0.28.1`. Save the entire block as provider_lab.py and run `python provider_lab.py`. It includes its own Reply, ProviderError and validator: no future project file is required. The mock transport executes the real HTTPX request and response code; its answer text is deliberately fixed.

## Trace transport and resource ownership

1. Construct the messages from the bounded query and authorized evidence, keeping data separate from operator instructions.
2. Enter the client and streaming-response context managers. The model request says stream=False; HTTP body iteration bounds memory, not model token events.
3. Reject non-success status, then accumulate at most 64 KiB in 4096-byte decoded chunks before parsing JSON.
4. Require a dictionary, completion signal and message dictionary; validate text/source/usage explicitly with ProviderError.
5. Both contexts close on success, malformed JSON, oversize body or cancellation. This simple call-scoped client sacrifices pool reuse; do not share a global async pool across unrelated request-thread event loops.
6. Run the 503 mock and observe a dependency error rather than a successful empty answer. The capstone tests add the complete malformed/completion/usage matrix.

```python
"""+provider_source+"""
```

## Optional real inference and its different evidence

Install and run Ollama separately, choose an installed tag your machine supports, set OLLAMA_MODEL and optionally OLLAMA_ORIGIN, then set RUN_LIVE_MODEL=1 and run again. No model is downloaded or called by the academy. Keep connection failures as real integration outcomes. Independently review claim support and actual usage; a passing mock cannot certify model faithfulness. A mutable model tag is not an immutable digest. Real inference remains untested unless you run it.
"""))
        if index in {9,10,11}:
            names={9:['pipeline.py'],10:['evaluate.py','test_evaluate.py'],11:['server.py','test_http.py']}[index]
            explanation={9:'Assemble the capabilities from sessions 1–9 in pipeline.py. Trace validate_query → owner-selected evidence → cache_key → Store.get → validated provider → Store.put. Then trace producer/consumers through answer_batch. Store.backup uses the consistent snapshot mechanism just taught. Use a fresh student project directory; the file imports only the standard library unless you opt into the HTTPX adapter.',10:'Keep pipeline.py from session 9 in the same directory. Save evaluate.py and test_evaluate.py below. Run python -m unittest -v test_evaluate, then python evaluate.py --repeats 20 --output evaluation-observed.json. Cases and expected labels are fixed; the unavailable-provider test must produce a failing report while the test itself passes. All 120 timing observations are local repeated fixture cases, not representative production load.',11:'Keep pipeline.py from session 9 and install the pinned HTTPX dependency before full project test discovery. Save server.py and test_http.py below; run python -m unittest -v test_http. make_server binds an isolated loopback port for tests. The factory captures trusted configuration; Admission separates a thread-safe rate window from processing slots. The tests force timeout/capacity/error branches and verify cleanup using actual HTTP requests.'}[index]
            body='## Assemble the next working slice\n\n'+explanation+'\n\n'
            for name in names:
                body+='### '+name+'\n\n```python\n'+(BASE/name).read_text().strip()+'\n```\n\n'
            chapters.insert(-1,dict(id='project-slice',title={9:'Assemble the scoped pipeline and recovery store',10:'Run the measured, versioned evaluation gate',11:'Assemble and test the real HTTP boundary'}[index],kind='Cumulative project implementation',body=body))
        if index==12:
            body=(BASE/'README.md').read_text()+'\n\n## Capability coverage — no untaught imports\n\n'+ '\n'.join(f'- Session {i}: {r[0]}.' for i,r in enumerate(ROWS[:11],1))+'\n\n## Save every project file\n\n'
            for path in sorted(BASE.iterdir()):
                if not path.is_file() or (path.suffix!='.py' and path.name not in {'Dockerfile','requirements.txt','.dockerignore'}):continue
                language='python' if path.suffix=='.py' else 'text'
                body+=f'### {path.name}\n\n```{language}\n{path.read_text().strip()}\n```\n\n'
            chapters.insert(4,dict(id='capstone-build',title='Build the complete final project from these files',kind='Complete student capstone',body=body))
        def quiz(qid, question, answers, explanation):
            shift=int(hashlib.sha256(f'{index}:{qid}'.encode()).hexdigest(),16)%3
            tagged=[(True,answers[0]),(False,answers[1]),(False,answers[2])]
            tagged=tagged[shift:]+tagged[:shift]
            choices=[{'id':chr(97+i),'text':value} for i,(_,value) in enumerate(tagged)]
            correct=next(chr(97+i) for i,(ok,_) in enumerate(tagged) if ok)
            return {'id':qid,'review_chapter':('advanced-studio' if qid.startswith('advanced-') else 'concept-tutorial'),'prompt':question,'options':choices,'correct':correct,'explanation':explanation,'option_feedback':{choice['id']:(('Correct. ' if choice['id']==correct else 'Revisit the boundary. ')+explanation) for choice in choices}}
        quizzes=[quiz('decision',prompt,[right,wrong1,wrong2],why)]
        for number, (question, answer, alternative1, alternative2, explanation) in enumerate(CHECKS[index-1], 1):
            quizzes.append(quiz(f'applied-{number}', question, [answer, alternative1, alternative2], explanation))
        for number, (question, answer, alternative1, alternative2, explanation) in enumerate(advanced[4:], 1):
            quizzes.append(quiz(f'advanced-{number}', question, [answer, alternative1, alternative2], explanation))
        practice += '\n\n## Required advanced studio evidence\n\n'+advanced[2]+'\n\n## If the advanced case fails\n\n'+advanced[3]
        next(c for c in chapters if c['id']=='practice')['body']=practice
        learning=dict(chapters=chapters,concepts=[dict(term=a,definition=b) for a,b in concepts],questions=[dict(id='transfer',prompt=f'Explain the failure boundary in “{title}”. What remains bounded, what can still fail, and which observation would falsify your claim?',guidance=f'Name the concrete input, invariant and observed failure from this session. {why} Separate fixture evidence from the production behavior you have not tested.')],quiz=quizzes,flashcards=[dict(id=f'card-{i}',front=a,back=b) for i,(a,b) in enumerate(concepts,1)]+[dict(id=f'advanced-card-{i}',front=q[0],back=q[1]) for i,q in enumerate(advanced[4:],1)],exercise=dict(steps=['Run the complete baseline and predict every assertion.',extension,failure,advanced[2],'Retain commands, actual outputs, one failed/corrected case and the three-pillar trade-off.'],hint=advanced[3],hints=[advanced[3],f'Locate the contract before editing: {concepts[0][1]}',f'Write the counterexample as one assertion before implementing: {failure}',f'Keep the original baseline unchanged. {why}'],material=practice,solution=f'''## Review after your attempt

The reference baseline is the complete worked specimen, not a hidden answer. For the assigned extension, the required invariant is: {extension}

A sound solution rejects the named invalid path before expensive or privileged work and retains the valid output. Add independent positive/negative assertions rather than merely printing the expected answer. Trace the failing input through the guided teaching above; use its exact resource and identity boundaries. {why}

For the integrated capstone, all reference files and unit tests are provided in its complete-project chapter. Compare your own attempt only after preserving its failure evidence.'''),task=dict(title=title+' — implementation evidence',deliverable=('python-ai/capstone/README.md' if index==12 else f'python-ai/session-{index:02}/exercise.py'),criteria=[advanced[2],'The unchanged baseline and the assigned variation run with Python 3.12 and assertions enabled.','The named invalid input or failure path is reproduced, diagnosed and checked without weakening expectations.','Evidence includes commands, actual outputs, measured or explicitly unknown latency/cost/quality, context boundaries and remaining limitations.']),progression=dict(entry=ENTRY,coverage=([dict(capability=r[0],lessons=[f'python-ai:v1:{i:02}']) for i,r in enumerate(ROWS[:11],1)] if index==12 else [])))
        learning['exercise']['solution'] += '\n\n## Complete reference variation\n\nSave as solution.py and run with Python 3.12 and assertions enabled. Preserve your own attempt before comparing.\n\n```python\n' + solution(index) + '\n```\n'
        if index<=11:
            learning['exercise']['solution'] += '\n\n## Complete advanced studio reference\n\n'+advanced[3]+'\n\n```python\n'+(ROOT/f'scripts/python_ai_drills/{index:02}.py').read_text().strip()+'\n```\n'
        learning['revision']=hashlib.sha256(json.dumps(learning,sort_keys=True).encode()).hexdigest()
        content='# '+title+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in chapters)
        program['lessons'].append(dict(order=index-1,title=title,module=module,minutes=720 if index==12 else 300,content=content,task='\n'.join(learning['exercise']['steps']),source_id=f'python-ai:v1:{index:02}',source_url='',content_hash=hashlib.sha256(content.encode()).hexdigest(),resources={'revision':'academy-course-books-v-python-ai-2','learning':learning,'artifact':learning['task']['deliverable']}))
    return program

if __name__ == '__main__':
    target=ROOT/'backend/academy/starter_curriculum.json'
    existing=json.loads(target.read_text())
    program=build();program.pop('_capstone')
    # Record exact authored fingerprints before replacement, preserving database edits.
    history_path=ROOT/'backend/academy/course_book_history.json'
    history=json.loads(history_path.read_text())
    for version in [p for p in existing if p['slug']==program['slug']]+[program]:
        for lesson in version['lessons']:
            item=history.setdefault(lesson['source_id'],{'content':[],'learning':[]})
            for field,value in [('content',lesson['content_hash']),('learning',lesson['resources']['learning']['revision'])]:
                if value not in item[field]:item[field].append(value)
    history_path.write_text(json.dumps(history,indent=2)+'\n')
    target.write_text(json.dumps([p for p in existing if p['slug']!=program['slug']]+[program],indent=2,ensure_ascii=False)+'\n')
    print('Python for AI:',len(program['lessons']),'advanced sessions;',sum(len(l['content'].split()) for l in program['lessons']),'words;',sum(len(l['resources']['learning']['chapters']) for l in program['lessons']),'chapters')
