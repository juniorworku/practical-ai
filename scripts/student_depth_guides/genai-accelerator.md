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
