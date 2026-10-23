"""Advanced studio teaching, aligned tasks and scenario feedback for all 12 sessions."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# title, stepwise teaching, assigned advanced evidence, feedback, two application checks
STUDIOS = [
('Design an immutable request boundary', '''A production boundary must reject extra fields as well as wrong value types. A dictionary with an owner supplied by a caller must not overwrite authenticated identity. The parser accepts trusted_owner separately, checks an exact key set and copies source IDs to a tuple. This copy removes the alias back to the caller’s mutable list.

1. Read the allowed fields before constructing the object. The dataclass is the validated internal representation, not the JSON parser.
2. Validate the trusted owner, query and each source ID. Python bool is not a useful string or count substitute.
3. Copy nested values to immutable primitives. frozen prevents reassignment; slots prevents arbitrary new attributes, but neither is a recursive authorization mechanism.
4. Mutate the original input list after parsing. The request must retain its original source tuple.
5. Probe extra owner fields, non-dictionaries, boolean queries and non-string IDs. Each must fail before provider work.

This is boundary design rather than a dataclass syntax exercise. The capstone derives ownership from credentials, validates the complete batch and separates InputError from ProviderError so an upstream failure does not masquerade as a caller mistake.''',
'Reproduce the exact-schema, alias-mutation and wrong-type matrix in the studio. Preserve all valid cases and prove that caller-supplied owner cannot enter the internal request.',
'If mutating the source input changes the parsed request, inspect whether you copied nested values. If extra owner is accepted, reject unknown keys before construction; a frozen object alone cannot repair bad identity.',
('Why convert the caller’s source list to a tuple of strings?', 'To remove the mutable input alias after validating its elements.', 'To freeze only the dataclass while retaining the original mutable source list.', 'To rely on a read-only wrapper around the outer dictionary without copying nested values.', 'Copying immutable primitives breaks the alias. It provides neither encryption nor permission checks; trusted identity still comes from application policy.'),
('The provider returns invalid text for a valid request. Which category should the HTTP layer surface?', 'An upstream contract failure, not a malformed client request.', 'A 400 response because a JSON validator eventually raised ValueError, regardless of which dependency supplied it.', 'A 200 response with empty text that is cached to avoid another upstream attempt.', 'The request can be valid while its dependency is faulty. Distinct exception categories allow the HTTP layer to use 502 instead of blaming the caller with 400.')),
('Prove framing is independent of delivery chunks', '''Testing one convenient network split is weak evidence. The studio enumerates every two-chunk partition of the same UTF-8 byte sequence, including positions inside a multi-byte emoji. It also delivers one byte at a time. These cases simulate segmentation without changing the expected decoded records.

1. Count total bytes before adding a chunk to the pending buffer; reject work beyond the whole-stream allowance.
2. Extract each newline-delimited record and enforce its individual limit.
3. Count nonblank records separately from bytes. Many tiny valid records can exceed work limits despite a small buffer.
4. Validate the unfinished remainder after each chunk and reject truncation at EOF.
5. Hold expected records fixed for every delivery partition. A failed split identifies a framing/decoding defect, not a reason to discard characters.

The parser is a bounded application layer, not a guarantee about the transport’s earlier allocations. The real adapter later reads fixed-size byte chunks and caps the total response before JSON parsing. Its stream=False requests one completed model response; HTTP body streaming is distinct from model token streaming.''',
'Run all partition checks and invalid-stream cases. Implement independent record-size, total-byte and record-count limits; demonstrate that changing segmentation alone never changes valid output.',
'If only ASCII cases pass, inspect where decoding occurs. If many tiny records bypass limits, separate record count from buffer length. Reject a missing completion delimiter rather than silently yielding a fabricated record.',
('Each record is 10 bytes and valid, but the peer sends a million records. What is missing?', 'A whole-stream byte/work allowance and record-count limit.', 'Only an unfinished-buffer cap; complete records can continue forever because each one is small.', 'Collect all decoded records into a list and enforce the count only after the stream finishes.', 'Per-record validity does not bound total work. Count the entire stream and reject excess before producing an unlimited sequence.'),
('The adapter reads HTTP chunks while asking the model for stream=False. Is that token streaming?', 'No; transport body iteration and incremental model token events are different contracts.', 'Yes; treat each received transport chunk as one emitted token event.', 'Yes; record the first HTTP body byte as the first accepted model answer without inspecting completion.', 'HTTP chunk boundaries are arbitrary. The response can be incrementally read for memory bounds while the model API returns one final JSON document.')),
('Force out-of-order completion and measure queue pressure', '''A concurrency test should force the scheduling condition it claims to test. Sleeping for guessed durations can fail on a busy laptop. Here an Event prevents input 0 from completing until input 1 has completed. Original indices preserve output order while a completion list records the opposite execution order. The nested producer/consumer functions are closures over queue and output. nonlocal permits rebinding their shared counters; it is not a thread lock or a cross-process synchronization mechanism.

1. Create a Queue with a finite capacity and a fixed number of consumers, not one task per input.
2. Record queue.qsize after each successful put to observe admitted queued work. Active work is a different count.
3. Increment active only around the operation and decrement it in finally.
4. Store the result by original index; verify the completion list is deliberately out of order.
5. In the primary variation inject a consumer failure, catch ExceptionGroup and assert no active operation survives TaskGroup exit.

Queue capacity bounds queued entries; fixed workers bound active calls. The known batch and output array still occupy O(n) memory, so the capstone also caps the input batch at 20. A truly unlimited input source needs a bounded result sink instead of preallocating its entire output.''',
'Force input 1 to finish before input 0, preserve result order, record queue and active peaks, and retain the consumer-failure cleanup assertion from the primary variation.',
'If outputs reorder, inspect where you append versus index results. If the failure test hangs, verify that the producer and every consumer belong to the same TaskGroup and that cancellation is not swallowed.',
('The queue holds two items and three workers are busy. Is there only two items’ worth of admitted work?', 'No; queued and active work are separate, and input/result storage must also be bounded.', 'Yes; Queue.maxsize counts active consumers as well as waiting entries.', 'Yes; a small queue removes the need to bound the retained input and result arrays.', 'Queue maxsize counts waiting entries. Active operations and retained input/results occupy additional resources.'),
('Why use an Event instead of sleep(.01) to force completion order?', 'It establishes a causal ordering rather than assuming a scheduler speed.', 'A longer sleep would guarantee the same ordering on every busy machine.', 'Sorting outputs afterward proves that the operations actually completed out of order.', 'A causal signal makes the assertion about ordering reproducible. Wall-clock sleeps only make a race likely and can fail under contention.')),
('Separate coroutine cancellation from thread lifetime', '''Cancellation is cooperative and applies to the coroutine you own. A running function in a thread is not forcibly terminated when its asyncio waiter is cancelled. The studio makes this visible with separate entered, release and finished threading events.

1. Start a blocking function with asyncio.to_thread and wait until it has actually entered. The threading.Event.wait calls also run off-loop through to_thread; calling those blocking waits directly in the coroutine would stall its event loop.
2. Cancel the awaiting task and observe CancelledError.
3. Check that the underlying function has not finished. This is the precise counterexample to “cancel stops all work.”
4. Release its independent stop event in finally and wait for its completion with a finite bound.
5. Keep every blocking call’s own timeout. asyncio.run waits for executor cleanup, so abandoning a thread can keep shutdown waiting.

The primary variation wraps both attempts in one timeout and separately tests explicit parent cancellation. Neither test asserts an exact elapsed millisecond value. The capstone includes storage and queue waiting in its overall deadlines, but an already-committed thread write is not rolled back by cancelling its waiter.''',
'Run the thread-lifetime counterexample, prove cleanup even if an assertion fails, and keep both overall-attempt deadline and parent-cancellation tests from the primary solution.',
'If the script stalls at shutdown, inspect the thread’s own stop/timeout path. If cancellation returns success, remove cancellation suppression. Do not “fix” the test by omitting cleanup.',
('A cancelled to_thread cache write has already committed. Should a later retry assume it was rolled back?', 'No; inspect persisted state and use the operation’s identity before deciding what to repeat.', 'Assume the cancelled await rolled back the underlying transaction automatically.', 'Replay an uncertain write unconditionally because the caller did not receive its acknowledgement.', 'Cancelling a coroutine does not reverse a completed transaction. Reads and idempotent cache replacement have different replay risks from external writes.'),
('An operation has an item deadline and a batch deadline. Why keep both?', 'One bounds an individual dependency; the other includes queue waiting and the combined request lifetime.', 'Reset the whole batch timer whenever another item starts, so every item receives the full request allowance.', 'Use a connection-establishment timeout as the only bound on queue and database waiting.', 'Separate scopes bound different waits. Both still rely on cooperative cancellation and do not provide hard CPU or thread termination.')),
('Reject success-shaped upstream failures', '''The studio tests five invalid provider values rather than relying on a single empty-string example. Explicit ProviderError validation runs in ordinary execution; assertions verify outcomes and are never the production guard.

1. Reject an unexpected object type before reading its attributes.
2. Require nonempty bounded text and the selected authorized source label.
3. Validate usage as a nonnegative integer or unknown. bool subclasses int, so type(count) is int intentionally rejects True.
4. Preserve None for missing measurements. Accept a real measured value without assuming every provider behaves like the fake.
5. Run the optional adapter chapter’s HTTPX mock first. It checks the actual request path, completed JSON and usage without installing a model.

The real adapter reads at most 64 KiB of decoded response bytes before JSON parsing and closes the stream/client on every path. A call-scoped client is simple but sacrifices pooling reuse; a long-lived async service should inject a client scoped to its event loop. The threaded teaching server must not share an async client across unrelated event loops.''',
'Run the complete invalid-response matrix and offline HTTP adapter check. Verify that a missing usage count remains unknown and a malformed upstream response is never cached or labeled client input error.',
'If True passes as a usage count, inspect exact integer validation. If a malformed message raises AttributeError, validate object shape first. A passing mock transport test establishes the adapter contract, not real model faithfulness.',
('Why cap response bytes before calling response.json?', 'An output-text limit after parsing cannot bound an arbitrarily large response body already buffered in memory.', 'The requested num_predict token limit is already sufficient to bound any response payload the server sends.', 'Read and parse the entire response first; a final message-length check bounds the earlier body allocation.', 'Transport allocation, JSON parsing and semantic output validation are separate layers. Bound the body before parsing and validate text/usage afterward.'),
('May one global AsyncClient be reused by unrelated asyncio.run calls in request threads?', 'Do not assume so; scope the client and its pool to a compatible event-loop lifecycle.', 'Yes; a thread lock around client construction makes the resulting async connection pool usable from every event loop.', 'Yes; close the client later from any fresh asyncio.run call when a request has finished.', 'Async connection pools have lifecycle ownership. The teaching adapter uses call-scoped cleanup; a real async service can reuse one correctly scoped client.')),
('Make retry policy deterministic with an injected clock', '''The original example teaches bounded attempts. The advanced studio separates policy time from real I/O time so backoff decisions can be tested without waiting or relying on a lucky scheduler.

1. Compute one end time from the total policy budget.
2. Catch only TransientRead. Permission and malformed-input failures escape immediately.
3. Choose the greater of exponential backoff and the adapter’s validated Retry-After delay.
4. Reject a sleep that consumes the remaining allowance, rather than exceeding the budget and hoping the next call succeeds.
5. Inject clock and sleep. The fake sleep advances policy time and records exact delays; production still needs an async timeout around real network work.

The TransientRead exception carries already-parsed retry metadata in this local fixture. A real adapter must validate and cap upstream header values first. Optional jitter may reduce synchronized retries in production but needs its own seeded/bounded test policy. This read-only capstone intentionally does not auto-retry provider failures; callers see honest errors without hidden amplification.''',
'Demonstrate exact allowed backoff and refusal of a Retry-After longer than the remaining budget. Preserve the primary tests for exhaustion and one-attempt authorization failure.',
'If the fake clock test passes but a real call can hang, add the actual I/O deadline; policy accounting alone cannot interrupt an await. If denied permission is retried, narrow the caught exception class.',
('Retry-After is two seconds but only one second remains. What should this policy do?', 'Stop with a budget outcome instead of sleeping beyond the overall allowance.', 'Sleep for the server delay, then start another full attempt deadline even though the caller budget has expired.', 'Retry immediately to avoid consuming the remaining budget in sleep.', 'An upstream delay cannot enlarge the caller’s budget. Surface an unavailable/budget outcome instead of creating an unbounded wait or retry storm.'),
('What does an injected clock test establish?', 'The specified attempt/backoff decisions; real transport deadlines and latency need separate tests.', 'The fake backoff transcript proves that the real network call always completes within that budget.', 'Advancing the policy clock also tests actual socket cleanup and remote rate-window enforcement.', 'A fake clock controls policy inputs. It cannot establish actual network scheduling, provider behavior or semantic quality.')),
('Allocate whole authorized context, not independent chunk limits', '''Two individually small documents can exceed a total request allowance. The studio constructs the exact local JSON envelope before accepting each source, reserves output space and never clips the exception sentence off a policy merely to make it fit.

1. Validate the total allowance and reserve. Check the instruction/query envelope even when no document fits.
2. Filter by trusted owner before considering context candidates.
3. Build a candidate envelope with the complete next policy. Measure its encoded UTF-8 bytes plus reserve.
4. Keep the complete policy only when it fits; otherwise omit it and preserve an explicit no-evidence path.
5. Compare emoji character length with encoded bytes to show why units matter.

This is an exact byte allowance for the local serialization, not the model’s hidden chat template or tokenizer. A production token budget requires the selected model’s tokenizer/template, output reservation and actual usage monitoring. Stable ties in lexical retrieval do not resolve conflicting authoritative policies: retain both with revision rules or send the ambiguity to review.''',
'Prove aggregate allowance, wrong-owner exclusion and preservation of the entire policy exception. Keep the lexical-tie checks and explain why a stable order alone does not choose the authoritative policy.',
'If each document passes but the whole envelope is too large, measure the combined serialization and reserve. If no document fits, abstain; do not silently truncate a legally meaningful exception or add another owner’s source.',
('A whole policy exceeds the remaining allowance because of its exception paragraph. What is defensible?', 'Omit it and abstain/retrieve a better authorized unit, preserving the missing-evidence outcome.', 'Trim the exception paragraph and keep labeling the result as an answer grounded in the complete policy.', 'Enforce only the individual document size and allow the full context envelope to exceed its reservation.', 'Budgeting cannot silently change the meaning or authority of evidence. Missing context must remain visible and scoped.'),
('Two equal-ranked policies disagree. Does deterministic sorting establish the correct policy?', 'No; authority/revision rules or a reviewed ambiguity decision are still required.', 'Use stable ID order as the authority rule even when the IDs do not encode approval or recency.', 'Send conflicting policies to the model and omit any conflict/revision record from the result.', 'Deterministic execution and factual authority are different. A reproducible tie still needs a valid source-selection policy.')),
('Coalesce duplicate work without crossing owners or lifetimes', '''A cold durable cache can receive two identical requests simultaneously. A plain get→compute→put sequence can compute both. The studio adds a per-event-loop in-flight registry; it does not replace durable storage or a distributed lock.

1. The key is already scoped by owner and revisions. Look up a strongly retained task before starting another computation.
2. Register one created task and attach a completion callback that removes only that exact task identity.
3. Await it through shield so cancelling one waiter does not cancel work still needed by another.
4. Retrieve abandoned exceptions and own an explicit close method that cancels/awaits outstanding tasks.
5. Cancel the first waiter, release the shared computation and prove the second receives the answer after exactly one call.

Shield is not permission to leak tasks. The service owns the underlying task until completion or close. Its completion callback retrieves an abandoned failure so it is observed, but awaiting callers still receive that failure. close snapshots the tasks, cancels them and awaits gather(return_exceptions=True) to finish every cleanup rather than leaving on the first error. The threaded capstone deliberately does not share this async registry across request-loop lifetimes; its durable owner/revision cache remains valid even if simultaneous cold requests duplicate safe read work.''',
'Run the two-waiter cancellation test and prove one underlying call plus an empty registry after close. Retain separate schema/source/model cache invalidation checks; do not claim cross-process coalescing.',
'If one cancelled caller kills everyone’s result, inspect the awaited task ownership. If tasks remain after shutdown, ensure close cancels and awaits them. Do not remove owner/revision fields merely to increase coalescing.',
('A single-flight registry is scoped to one event loop. Does it deduplicate across service replicas?', 'No; another process needs a separate coordination policy if that guarantee is required.', 'Use the same key in each process and assume its separate asyncio.Lock objects coordinate globally.', 'Rely on SQLite row uniqueness to prove that only one remote provider request was executed.', 'Local in-flight coalescing and durable cache uniqueness are separate from distributed coordination. Never claim exactly-once remote effects from this registry.'),
('Why must shielded tasks still have an explicit close path?', 'A cancelled waiter can leave the underlying task running, and the service must own its cleanup.', 'Drop the task reference after a waiter cancels and rely on garbage collection to release its network operation.', 'Suppress CancelledError in every layer so no service-owned task ever needs to be stopped.', 'Cancellation isolation changes ownership responsibilities. Retain tasks, retrieve errors and cancel/await remaining work during service shutdown.')),
('Test rollback and a consistent restored snapshot', '''Reopening one connection checks persistence. A recovery test is stronger: use SQLite’s backup API, open the snapshot as a new store and re-run scoped queries against it.

1. Commit the original owner/key row using bound SQL parameters.
2. Use source.backup(target) with both connection lifetimes owned explicitly.
3. Start a second transaction, insert a new row and raise before commit. Verify it rolled back.
4. Open the snapshot separately and check the original owner’s value and the other owner’s denial.
5. Close every connection before deleting the temporary directory. A database context commits/rolls back; closing is still separate.

Keep a snapshot outside the same failure domain for a real backup policy; another file on the same destroyed volume is only a restore-mechanics exercise. The next chapter assembles pipeline.py from capabilities already taught. Locate cache_key, validate_reply, answer_one and answer_batch and identify their owner, resource and exception boundaries before continuing.''',
'Produce a consistent snapshot, recover the owner-bound value from it and prove rollback of a failed second transaction. Trace blocking SQL offload and explain why coroutine cancellation does not reverse a committed write.',
'If the snapshot misses committed data, check backup direction and transaction completion. If cross-owner reads work, restore the owner predicate. Do not copy a live SQLite file while ignoring its journal/WAL state.',
('A backup file is stored on the same volume as the live database. What has the exercise proved?', 'Snapshot/restore mechanics, not resilience to loss of that entire volume.', 'Evidence that the backup survives destruction of that same storage volume.', 'Proof that a raw copy of a live database file would be equally consistent without its journal.', 'A recovery mechanism and a recovery placement policy are distinct. Surviving volume loss requires a tested copy in a separate failure domain.'),
('Why open a new connection inside each offloaded Store operation?', 'Default SQLite connections have thread ownership; short local lifetimes avoid sharing one across request threads.', 'Set check_same_thread=False on one shared connection and assume that alone serializes every transaction safely.', 'Create a connection on the request thread and pass it to unrelated executor threads without changing ownership.', 'A fresh connection keeps ownership aligned with the executing thread. Transactions, busy timeouts and explicit close still matter.')),
('Measure a running pipeline with a versioned gate', '''The warm-up report teaches quantiles using supplied numbers. The advanced studio records actual perf_counter durations around executed operations, including an exception. The cumulative evaluation chapter then supplies evaluate.py and its tests against the assembled pipeline.

1. Freeze cases, source expectations and a dataset digest before running a candidate.
2. Run every case; append an observation whether it succeeds or raises. Keep error class and case ID, excluding private prompts from logs.
3. Calculate p50 and nearest-rank p95 over all observed attempts. Report error outcomes separately; fast failures are not successful low latency.
4. Count actual noncached provider calls. Preserve missing usage and monetary cost as unknown rather than inventing zeros.
5. Block the contract gate on any failed expected source, especially unauthorized evidence. Source correctness is not semantic faithfulness.

Run the published runner with --repeats 20 for 120 local case observations, cold then warm. Repeated tiny fixtures are not representative load, an independent large dataset or proof of model quality. The report declares that scope. A reviewed model evaluation needs separate supported/unsupported claim labels, judge configuration/version and disagreement review.''',
'Run the measured studio and cumulative evaluator; retain a failing outage report and passing fixture report without changing expected labels. Explain the cold/warm population, provider calls, unknown cost and unmeasured semantic support.',
'If failed calls disappear from latency rows, append observations in the error path. If the report says zero cost because usage is missing, keep it unknown. A passing source-ID gate cannot approve unsupported generated claims.',
('A warm cache makes most calls free of provider requests. How should the report describe this?', 'Declare the cold/warm population and observed provider-call count; do not generalize the warm timing to a cold deployment.', 'Combine the observations without cache labels and describe the result as cold-start latency.', 'Remove unavailable attempts before reporting latency and accepted-output cost.', 'The cache policy changes the workload. A reproducible report identifies its population and preserves the failures and real calls that occurred.'),
('The expected owner-isolation case fails but the overall average remains high. May the release gate pass?', 'No; the isolation failure is a critical gate, regardless of average quality or speed.', 'Allow a 99% average threshold to override the explicitly mandatory owner-isolation rule.', 'Change the expected source to the observed leaked source so the unchanged implementation passes.', 'Mandatory invariants cannot be traded away through averages. Keep fixed labels and surface critical failures explicitly.')),
('Wire identity, rate, capacity and failures into HTTP', '''A /health demonstration alone does not teach the capstone’s POST boundary. First run the quota/slot studio, then assemble the complete server.py and test_http.py in the next chapter.

1. The server factory owns trusted keys, Store, Provider and Admission. Tests create isolated servers rather than relying on hidden module globals.
2. Compare bearer credentials outside model output, derive owner, then enforce its rolling rate window under a thread lock.
3. Acquire a nonblocking processing slot independently of rate allowance. Release it in finally on every admitted path.
4. Validate framing, Content-Type, complete body, exact JSON fields and every query before starting expensive work. InputError maps to 400; malformed upstream data maps to 502.
5. Preserve nested TaskGroup failures when classifying errors. The request deadline maps to 504, quota to 429 and capacity to 503.
6. Test actual loopback requests: wrong owner, malformed input, real saved/readback state, a held provider, forced timeout, slot recovery and a clock-advanced quota window.

These are read-only computations; completed per-item cache entries may exist after a later provider failure, but no completed batch is returned. Client fixtures remain available for a deliberate safe retry. The stdlib server still creates threads before application admission. Public hosting requires upstream connection limits, a production server, TLS and coordinated quotas across replicas.''',
'Run the clock/slot studio, then the complete HTTP test file. Reproduce 401, 400, 413, 415, 429, 502, 503 and 504; prove slot recovery and a new server’s cache readback.',
'If a provider schema failure returns 400, separate InputError from ProviderError. If capacity never recovers after a timeout, inspect finally. If one owner exhausts another’s quota, check the window key and trusted identity source.',
('The quota allows a request but all processing slots are occupied. What should happen?', 'Reject with a capacity outcome; request rate and active concurrency are independent controls.', 'Queue unlimited pending work because the rolling request window already admitted the caller.', 'Use the processing semaphore instead of keeping a separate arrival-rate policy.', 'A rate window counts arrivals over time. A processing slot bounds active expensive work; neither substitutes for the other.'),
('A valid request triggers malformed provider JSON inside a TaskGroup. Which status is appropriate here?', '502 for an upstream contract failure, preserving the valid caller’s input.', '400 because a JSON parser raised ValueError, without distinguishing upstream data from caller data.', '200 with an empty answer because the upstream HTTP connection itself succeeded.', 'Exception categories must retain responsibility across task groups. A malformed upstream payload does not make a valid caller request invalid.')),
('Build, measure, recover and defend the release scope', '''The final project is the integrated service, not the small release-scope dataclass. Its code is published in complete named files, and the runbook includes exact commands and expected observations.

1. Save every file from the complete-project chapter into a fresh directory. Install the pinned dependency in a Python 3.12 virtual environment.
2. Run unittest discovery, the versioned evaluator and its intentional failure tests. Check the named failure families, not only an aggregate green line.
3. Start the real server with synthetic credentials, run probe.py, stop/restart it and run the same probes against the committed database.
4. Build its Docker image, mount only its dedicated state volume, replace the container and prove cache readback and owner isolation again.
5. Exercise snapshot restoration, malformed upstream response, timeout and capacity cleanup using the supplied tests. Explain which assertions cover each behavior.
6. Compare provider, source and prompt revision changes independently. Keep real model semantics and representative load marked untested until you actually evaluate them.

## Understand the container before the build exercise

An image is an immutable packaged filesystem and startup configuration; a container is one running instance. Replacing a container removes its writable layer, so durable SQLite state belongs in the separate named volume supplied with --mount. A local snapshot on the same volume is still not an off-volume disaster backup.

Read the published Dockerfile in order. FROM selects the Python runtime; WORKDIR sets /app; copying/installing requirements before application files lets dependency layers be reused. COPY . . respects .dockerignore, which excludes credentials and local state. The image creates a nonroot learner and gives it ownership of /state before USER switches execution to that identity. ENV supplies the default state path and internal port; CMD starts the service. The named volume initially inherits the mounted directory ownership, so this user can write its database.

Inside a container the service binds 0.0.0.0 so container networking can reach it. The host publication -p 127.0.0.1:8094:8094 limits access to your own computer: left port is the host port, right port the container listener. EXPOSE documents a port; it does not publish one. --env STUDENT_KEYS explicitly forwards that variable; an operator shell variable is not automatically present inside the container. docker rm -f replaces only the named exercise container; it does not remove its named volume. Do not use an academy or workshop volume for this project.

Before proceeding, docker version must show a working client and server/daemon. If the daemon is unavailable, start your installed Docker runtime rather than changing the Python code. The following runbook supplies the complete build, probe, replacement and cleanup sequence.

The capstone reuses boundary validation (1), bounded transport (2), worker ownership (3), deadlines (4), provider validation (5), retry classification (6), authorized evidence (7), revision identity (8), recovery (9), measured evaluation (10) and HTTP admission (11). It intentionally does not add agent planning, model training or cross-replica coordination as untaught graduation requirements.''',
'Build the project from published files only, execute its tests/evaluator/HTTP probes and container restart. Submit a capability-to-evidence map with actual outputs, one corrected failure and explicit untested claims.',
'If a file imports another academy module, the project is incomplete: use the self-contained files shown. If all evidence is a screenshot or checkbox, execute the named tests and attach reproducible output. Keep production/model claims bounded by what ran.',
('Does passing this capstone certify an autonomous multi-agent system?', 'No; it certifies only the observed bounded read-only service contracts and explicitly tested deployment scope.', 'Yes; every API wrapper is automatically an autonomous agent.', 'Yes; Docker proves all AI engineering capabilities.', 'The final project deliberately uses the software taught in this path. Extra agent autonomy or distributed guarantees need their own teaching and evidence.'),
('Which graduation artifact best demonstrates reproducibility?', 'Named complete files, pinned setup, fixed cases, actual test/probe output and a scoped recovery/runbook record.', 'A fluent chat screenshot and a renamed production image.', 'A claim that unrun live-model checks passed.', 'Another student must be able to reproduce the observed result. Screenshots and names cannot replace executable contracts and honest scope.'))
]

def studio(index):
    title, teaching, task, feedback, *_ = STUDIOS[index-1]
    body=f'## {title}\n\n{teaching}\n\n'
    if index<=11:
        code=(ROOT/f'python_ai_drills/{index:02}.py').read_text()
        body+='## Complete advanced studio\n\nSave this entire block as studio.py and run `python -I studio.py` with Python 3.12. It is a standalone standard-library exercise; it does not import another lesson. Predict the assertion outcomes before running.\n\n```python\n'+code.strip()+'\n```\n\n'
    body+='## Required evidence and diagnostic feedback\n\n'+task+'\n\n'+feedback
    return {'id':'advanced-studio','title':title,'kind':'Advanced engineering studio','body':body}

MEASURES = [
 ('Boundary acceptance and rejected aliases','Compare the valid and invalid schema matrix; provider calls must stay at zero for rejected requests. Record parser timing only if measured, with the exact input set.','Exact keys, trusted owner, immutable copied source IDs and 2000-character boundary.','Character count is an input limit, not token usage. Reject extra source/owner fields before computing any prompt.'),
 ('Record/work allowances','Hold the decoded records constant across every split and one-byte delivery. Report accepted records, rejected oversized/truncated cases and maximum permitted input bytes; do not infer model speed.','Chunk-invariant UTF-8 records, line budget, total-byte budget and record-count rejection.','Record bytes, cumulative bytes and semantic completion separately. Keep the final provider signal distinct from record framing.'),
 ('Queue versus active work','Run one and three workers on the same bounded values. Record output order, active peak and queue peak; measure elapsed time separately if using representative I/O.','Forced completion disorder, ordered results, bounds and no surviving worker after a selected failure.','Batch storage, queued entries and active operations all consume resources; a semaphore alone does not bound task allocation.'),
 ('A deadline with a cleanup obligation','Record the timeout/cancellation category and whether each owned resource completed cleanup. Do not assert exact elapsed milliseconds on a shared machine.','Both attempts share one deadline; explicit cancellation propagates; a thread has its own stop condition.','Cancelled context work may already have committed. Preserve operation/source identity when deciding whether a safe retry is valid.'),
 ('A transport contract before model quality','Count valid, empty, incomplete, malformed and unavailable responses. Preserve actual supplied usage and unknown counts; a mock has no measured provider bill.','HTTPX request shape, status handling, 64 KiB response limit, nonempty text, allowed source and integer-or-unknown usage.','Bound input/evidence serialization and response bytes, and reserve model output separately. Transport bytes do not equal tokens.'),
 ('Attempts and remaining retry budget','Use the injected clock transcript to show calls and exact backoff. Real network latency and resource cost require separate observations.','Three-attempt exhaustion, one-attempt permission denial and refusal to sleep beyond the remaining budget.','A retried request retains its query/source revision. Never substitute a partial stream or stale cached result for an unavailable read.'),
 ('The complete context envelope','Keep owner and query fixed while changing the local serialization allowance. Record which whole source IDs fit and when the result abstains; do not relabel a byte allowance as tokens.','Aggregate budget, output reserve, exception preservation, owner-first selection and stable-but-unresolved conflicts.','Include instruction, query, evidence and output reservation. A real tokenizer/template budget remains a separate model-specific requirement.'),
 ('Cold cache, duplicate work and cancellation','Record hits/misses separately for owner, schema, source, prompt and model changes. Count one computation for the two-waiter studio, limited to its one event loop.','Independent revision misses, one underlying call, cancellation-isolated waiters and registry cleanup.','Full dependency identity stays in durable and in-flight keys; source/permission changes invalidate prior results rather than increasing apparent hit rate.'),
 ('Commit, reopen and restore','Measure SQL work only if you run it, noting the temporary filesystem and lock conditions. Compare cold computation with cache readback, not merely dictionary lookup.','Duplicate rejection, transaction rollback, explicit close, consistent backup, restored owner-bound read and denied other-owner lookup.','A snapshot has a source revision and owner scope. Another file on the same disk proves restore mechanics, not disk-loss resilience.'),
 ('A measured gate with declared population','Run evaluate.py on the unchanged cases, cold then warm, retaining all error rows. Report p50/p95, source acceptance and provider calls; leave monetary cost unknown without a tariff/resource measurement.','Dataset digest, stable labels, visible outages and a critical owner gate that averages cannot override.','Freeze model/source/prompt/schema versions when comparing candidates. Provider usage and semantic-support review remain distinct from source equality.'),
 ('HTTP failure and admission evidence','Record status outcomes for the actual request matrix and the held-provider capacity test. Keep per-request limits separate from item workers and owner windows.','Validate before work; distinguish input 400 from upstream 502; check 401/413/415/429/503/504, slot cleanup and restart readback.','Credentials determine owner outside JSON. Bodies and logs must not retain private prompts or secrets merely to make debugging convenient.'),
 ('A defensible integrated release','Retain actual tests, evaluator, HTTP probes and container-replacement output. Separate contract acceptance, local fixture timings, optional model semantics and untested production load.','Every published file, all named failure families, owner isolation, revision misses, snapshot restore and persisted cache after replacement.','Carry authorized source identities and versioned allowances through HTTP, provider and storage. Do not add untaught agent autonomy or distributed guarantees to graduation.')
]

def measurement(index):
    title,performance,checks,context=MEASURES[index-1]
    return f'''## {title}

### Latency vs. Cost vs. Quality

{performance}

### Deterministic evaluation

{checks} Keep fixed expected values. These assertions do not establish semantic model faithfulness. A model judge requires a recorded rubric/configuration and reviewed disagreements.

### Context management

{context}

## Required evidence

Retain the actual command, input/revision, observed result, a failing/corrected case and the current operating limit. Mark each unmeasured value unknown. The studio's diagnostic feedback identifies the boundary to revisit before you advance.
'''
