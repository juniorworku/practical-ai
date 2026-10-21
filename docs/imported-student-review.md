# Accelerator and Terminal Tutor: student teaching review

Scope: all **85 Accelerator lessons, 20 labs and 8 Terminal Tutor guides**. This review changes what learners are taught and practice, rather than treating a working page as evidence of teaching quality. The original imported snapshot remains in `backend/academy/content/imported_curriculum.json`; the active reviewed books are generated in `reviewed_workshop.json`.

## Teaching defects corrected

- Short snippets followed by “add imports and integration” tasks are replaced by complete, independently executable specimens. The reading now teaches the mechanism, traces the fixture, explains a counterexample and states the verification boundary before practice.
- Each exercise names a bounded change to the demonstrated code. It has three staged hints, a complete executable reference, exact expected output, diagnostic guidance and an evidence checklist. Larger integration examples have their own complete files and prerequisites.
- Accelerator lesson 41 previously inferred a conflict from any differing version labels. It now groups revisions by policy identity, so unrelated policies can have different versions without a false conflict.
- The backup lesson previously compared a copied dictionary with itself. It now backs up to a separate database connection and reads restored content. The extended case performs an actual PostgreSQL dump and fresh restoration, comparing IDs and text.
- Failure injection now invokes the failing dependency through the service boundary. Provider errors cannot be mistaken for fabricated successful answers. Retry examples account for an overall deadline; worker examples perform state changes rather than merely returning a job ID.
- Retrieval examples distinguish passage recall from hit rate, keep duplicate IDs from inflating scores and filter tenant scope before ranking or context assembly.
- Approval/checkpoint/replay examples bind authenticated owner, payload identity, reviewer and expiry. In-memory ledgers and checkpoint savers are explicitly distinguished from durable multi-worker guarantees.
- Lesson 85 no longer imports Workshop-only modules or directs learners to its management commands/settings. It teaches an independently validated provider-decision adapter with an injected offline transport.
- The included MCP server/client used an incompatible API surface. Complete files now use the tested MCP 1.30.0 interfaces: FastMCP, stdio_client, ClientSession, initialize and isError. The Markdown walkthrough and dependency snapshot match those files.
- Terminal Tutor no longer depends on a missing tutor ZIP, unavailable source panels or another agent to supply the teaching. Its eight guides teach real workspace paths, process exits, prediction, entry points, debugging, tool/protocol boundaries, instruction-package inspection and revision-aware session recall. Installing a coding agent is optional and is not required to complete the course.

## Student sequence and feedback

Every reviewed lesson includes concept teaching, a complete worked specimen, the three engineering pillars, aligned practice, private reflections, quiz explanations, flashcards and a practical evidence submission. The examples are software-first: inspectable interfaces and real error paths precede optional frameworks. All three pillars are applied before exercises: latency/cost/quality, repeatable evaluation and bounded scoped context/cache decisions.

The code specimens are deterministic synthetic fixtures. Semantic support is separately labeled; a known citation is never described as proof that prose is factual. Unknown provider usage remains unknown. Local assertions do not certify a cloud deployment or model quality.

Quiz answer keys and per-choice feedback stay server-side until submission. All 113 sessions have an authored applied checkpoint with specific distractor feedback. These address concrete misconceptions, including retry deadlines, missing release evidence, citation membership, revision conflicts, stale approvals and false judge acceptances. Reference solutions do not automatically run or grade student code; reflection comparison is explicitly self-review.

## Complete operational case

The inline `accelerator_stack` case provides every file for FastAPI, PostgreSQL, Alembic, Redis and Celery. It demonstrates committed accepted state, real worker ingestion, transactional chunk/ready writes, deduplicated delivery, scoped HTTP reads, bounded lexical context, a shared Redis request quota, migration and recovery.

Its two demo identities and fictional policies make it a local teaching service. It is not production authentication, semantic embeddings, a live model, a transactional outbox or a cloud scaling demonstration. The API uses port 8012, the academy 8080 and Workshop 8000. Neither database is published to the host.

## Verification evidence

- `docs/imported-teaching-audit.json`: 113 lessons; **226 exact published baseline/reference executions** under Python 3.12; 608 rendered teaching chapters; task alignment, staged hints, reflection guidance and feedback coverage.
- `docs/imported-stack-review.json`: real HTTP → Redis/Celery → PostgreSQL → answer checks; worker outage/recovery; process recreation/readback; database outage/recovery; PostgreSQL fresh restore; incremental migration; request 61 denied with 429/Retry-After; quota dependency failure/recovery.
- The original starter's locked environment installs successfully; its 13 tests pass. Its evaluation retains the known common-word false candidate on the unknown question, rather than claiming a repaired retriever.
- Seven advanced agent/graph checks pass, including unsupported citations, bounded execution, isolated thread state, adapter mutation isolation and unrepaired rejection. The actual MCP subprocess test passes discovery, valid call, resource read, invalid query and shutdown, reporting negotiated protocol 2025-11-25.
- Twenty-nine academy tests pass, including source upgrades without replacing lesson IDs, preserved notes/completions/prior practice, instructor edits, protected feedback and complete Tutor downloads.
- `docs/imported-browser-review.json` records the full 113-session/608-chapter browser pass, then a final five-session/29-chapter pass over the corrected infrastructure, agent and retrieval examples. `docs/imported-feedback-review.json` verifies all 113 final published books and all 678 feedback choices after the final content changes.
- `tests/imported-student.cjs` exercises every book and reference through the browser, then checks staged hints, wrong-answer feedback, remediation, retry, private reflection persistence and mobile reading. Its source-parity pass verifies all 113 served lessons against their reviewed files.

Reproduce with `python3.12 tests/imported-teaching-audit.py`, `node tests/imported-student.cjs`, and the isolated stack README. The full stack review requires that dedicated Compose project to be running and only uses synthetic data. Course import retains learner identities and recognizes authored teaching fingerprints; unrecognized instructor changes are preserved.
