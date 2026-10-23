# Python for AI: student teaching review

This review follows the 12 lessons in order, runs the published examples/answers, and assembles the final project from the files printed in the lesson. The intended entry level is working Python, HTTP/JSON, tests, environments and basic SQL. Async ownership, streaming boundaries, fault injection, durable state and operational evidence are taught here. Entry self-checks and explicit carry-forward artifacts are included.

## Findings and corrections

| Session | Gap in the earlier course | Reviewed teaching and practical evidence |
|---|---|---|
| 1. Contracts | An owner allowlist alone was too small an advanced assignment; frozen objects could retain mutable input aliases. | Exact-schema parser, credential-derived owner, immutable nested values, alias mutation and invalid-type tests; explicit caller versus upstream error responsibility. |
| 2. Streaming | One UTF-8 split and a per-record limit did not test segmentation invariance or cumulative work. | Every two-chunk partition and one-byte delivery, separate total/record/count bounds, malformed/truncated failures and transport versus token-event streaming. |
| 3. Concurrency | Consumer failure was assigned without a convenient injected operation or a complete failure reference. | Injectable async operation, forced completion disorder using events, ordered output, active/queue peaks, blocked-producer/sibling cancellation and cleanup assertions. |
| 4. Cancellation | The extension depended on small sleep races and did not show the running-thread caveat. | One deadline across attempts, explicit parent cancellation, cooperative cleanup and a complete to_thread counterexample with an independently released/timeout-bound thread. |
| 5. Adapters | Production validation used assertions; the optional adapter needed future definitions and buffered an entire body before its output check. | Explicit ProviderError, shape/text/source/usage validation, byte-bounded response reading, complete standalone offline HTTPX example and transport failure matrix. Optional live inference remains separate. |
| 6. Retries | Attempts were bounded, but the reference did not demonstrate remaining backoff allowance or Retry-After decisions. | Injected clock/sleep, exact attempt/delay transcript, refusal to exceed the remaining budget, nonretryable permission failure and exhaustion. The capstone intentionally does not add hidden automatic retries. |
| 7. Context | Individually small sources did not establish aggregate context fit or preserve a policy exception under truncation. | Whole serialized-envelope allowance and output reserve, owner-first selection, complete source inclusion or abstention, conflicting-policy limitations and explicit bytes/characters/tokens distinction. |
| 8. Caching | Versioned dictionary keys did not address simultaneous cold duplicates or cancelled waiters. | Independent model/source/prompt/schema misses; a complete per-loop single-flight studio with shielded waiters, strong task ownership and explicit close. It is not presented as distributed coordination. |
| 9. Persistence | Connection replacement was mistaken for a complete recovery procedure. | Closing plus transaction ownership, rollback and duplicate checks, SQLite backup and restored scoped read; the full cumulative pipeline is published before later imports require it. |
| 10. Evaluation | The only report calculated fixed supplied numbers. | An actual versioned pipeline evaluator retaining cold/warm calls and errors, dataset digest, measured latency rows, nearest-rank p95, unknown cost, a mandatory owner gate and separate unmeasured semantic quality. |
| 11. HTTP | A GET health example did not explain the POST capstone controls or error classifications. | Complete server factory and actual HTTP tests: identity, exact schema, whole-batch validation, framing/body bounds, owner quota, capacity, 400/401/413/415/429/502/503/504, cleanup and restart readback. |
| 12. Capstone | A release-scope dataclass could be mistaken for the project, and probes/evaluation were mostly described rather than supplied. | Ten complete source/configuration files plus the runbook; 25 tests, evaluator, executable HTTP probe, container replacement and snapshot restoration. The release fixture is explicitly insufficient. |

Every lesson now has an advanced studio before the assigned exercise, specific diagnostic feedback, a complete primary reference and (where applicable) a complete studio reference. There are 77 teaching chapters, 60 scenario questions and 60 flashcards across approximately 67 planned practice hours. Quiz distractors address plausible engineering mistakes. Advanced question feedback points to its own studio rather than the basic tutorial. Counts describe inventory; executable evidence and alignment are the review criteria.

## Appropriate use of Build · Measure · Operate

Keep the engineering brief in AI Agent Bootcamp, AI Workshops, AI Engineering, GenAI Accelerator and Python for AI. Python has six explicit stage contracts instead of falling through number-based agent/RAG heuristics. Workshops retain extraction, meetings, research, triage, content and app scenarios. The Bootcamp application/data module has an API/storage brief rather than an unrelated calendar-agent requirement.

Do not show this dense engineering overview block in Freelancing Masterclass or Terminal Tutor. Their own client-delivery, command-safety, review, reliability and measurement teaching remains available. The underlying learning principles are useful broadly; the same engineering assignment is not appropriate everywhere.

## Release integrity and verification

Earlier Python releases were not registered in the authored fingerprint history, so the safe seeder preserved some outdated lessons as if they were instructor edits. The review recognized only exact earlier generated text/learning variants, recorded their hashes and added automatic history recording to future Python generation. The upgrader continues to preserve unrecognized instructor changes. A regression test checks that recognized updates retain lesson IDs, enrollment, notes and completion while preserving an actual instructor edit.

The student runner `tests/python-ai-content.py` executes the actual published code blocks, not just generator helper files. It reconstructs the capstone in a temporary directory from its lesson text, compares its complete files and runs unit/HTTP/adapter/evaluation tests there. The evaluator runs six fixed cases twenty times (120 local observations); this is not a 120-case independent dataset or representative load test.

The capstone Docker image runs as a nonroot user. Its published .dockerignore excludes credentials, environments, state databases and observed reports. A container HTTP check validates owner isolation, malformed input, cached readback after replacement and quota behavior using only synthetic data.

Real model inference, semantic faithfulness and representative public-hosting load require separate evidence. A fixture, allowed source label or Docker build does not establish those results. The optional Ollama integration is supplied and its HTTP contract is exercised with an offline mock; no model is installed or contacted by these tests.

Technical behavior was checked against the official [Python 3.12 task/cancellation documentation](https://docs.python.org/3.12/library/asyncio-task.html) and [HTTPX async streaming/lifecycle documentation](https://www.python-httpx.org/async/). Their API behavior informs the examples; the academy supplies the complete teaching here.
