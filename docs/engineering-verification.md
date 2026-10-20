# Curriculum and student verification — 2026-10-20

The subsequent [student teaching review](engineering-student-review.md) records the expanded concept teaching, complete practice solutions and current verification. Counts and checks below describe the initial implementation.

## What changed

The academy now has four independent authored practical programs (96 sessions), plus the independent GenAI Accelerator. The new AI Engineering program has 36 sessions across five modules and twelve weeks, approximately 149 hours of estimated implementation/review work. The final native books contain 420 teaching/implementation/practice chapters, 288 quiz questions, 288 flashcards and 288 reflection prompts.

The teaching contract applies to every program's modules, including imported readings: software interfaces and engineering decisions first; production and failure evidence; explicit latency/cost/quality, deterministic contract evaluation and context/cache boundaries. Authored module endings add four release criteria. Previous learning revisions and instructor edits remain protected by the existing seeder.

Review corrections included:

- Replaced the new course's repeated generic assessment item with 36 session-specific diagnostic questions.
- Added full asynchronous audio gateway/browser files, including bounded PCM transport, cancellation/interruption and stale-connection handling. Offline echo is labeled transport evidence.
- Filled the gap between an embedding index contract and actual vector generation with a complete asynchronous embedding HTTP adapter, batch ordering, no-truncation request and dimension/model/finite-value checks.
- Added complete mixed-media parsing, scoped pgvector SQL, reranking/local-stream adapters, real LangGraph/MCP examples and durable fake workspace state.
- Added authorized Slack/calendar adapters and reviewed Gmail draft creation. No real message, invitation or draft was created during verification.
- Corrected a mismatched lexical query in the SQL exercise and a shell restore drill incorrectly labeled as Python.
- Added a complete CI workflow and distinguished harness regression from actual candidate evaluation, reviewed quality and release readiness.
- Rebuilt the stale 60-session optional archive with all 96 sessions and example files. Curriculum generation now rebuilds that archive automatically.

## Observed checks

- Frontend TypeScript/Vite production build passed; final Docker services healthy with PostgreSQL.
- Full Django/PostgreSQL suite: 21 tests passed. Final teaching/archive tests after the addenda: 3 tests passed.
- Original-program teaching audit: all 60 sessions aligned; 41 exact published Python examples executed with expected stdout; fictional client arithmetic reconciled.
- Engineering teaching audit: all 36 exact published standalone Python examples executed with expected stdout; all 96 sessions' criteria align with their exercises and module gates.
- Evaluation harness: 120 concrete contract cases passed against the clearly labeled deterministic fixture. Injected critical-failure and unavailable-result checks were detected. Semantic review remains zero; these are not model-quality scores.
- Integration tests in Python 3.12.14: real local FastAPI WebSocket authentication/PCM/stop/error behavior; PDF/DOCX/VTT extraction; Slack signature/replay and exact review checks; installed Live SDK shape; real LangGraph interrupt/resume and real MCP stdio client/server call. Embedding HTTP and Gmail draft contracts tested with controlled mock transports; mismatched dimensions and changed recipients were rejected.
- Exact pgvector SQL ran successfully in a disposable pgvector PostgreSQL 16 container. Cosine and lexical queries returned the expected scoped synthetic records. Test container removed.
- Student browser walkthrough: all 96 sessions and the then-current 419 chapters rendered, with every code fence intact and exercise/question/quiz alignment checked. The four final changed lessons (voice, embedding, workspace connectors, CI) then passed a separate walkthrough of all 20 current chapters. The final manifest totals 420 chapters.
- Student learning flows passed for all four practical programs: enrollment, reflection saving, server-side quiz feedback, flashcards, practical submissions, notes, completion, reload persistence and account isolation. Desktop/mobile sage palette and five public program cards checked.
- General account/library/Accelerator/Tutor/download smoke checks passed with PostgreSQL. The existing Vite preview at port 5173 matches Docker at port 8080; saved practice remained available after container replacement.
- CI example YAML parsed locally; hosted GitHub Actions was not executed. `git diff --check` passed.

The resolved local SDK/test dependencies are recorded in engineering-tested-dependencies.txt. They are evidence for this local test environment, not a promise of future provider compatibility.

## Boundaries of the result

No paid provider inference, real microphone quality evaluation, cloud deployment/load test, GPU benchmark or real connector effect was performed. The curriculum explicitly requires those observations before corresponding production claims. Three-dimensional vectors, rule fixtures, fake local effects, in-memory SDK checkpoints and configured concurrency do not establish semantic quality, remote exactly-once effects, durability or scale. Practical submissions are self-reported learning records, not certification.
