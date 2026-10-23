# Four-program student-depth review

Review date: 2026-10-23. Scope: AI Engineering (36 sessions), AI Agent Bootcamp (24), AI Workshops (18), and GenAI Accelerator (105 lessons/labs). Existing foundational teaching and the distinct program projects remain in place. The review checked progression, published code and reference variations, exercise acceptance, selected-answer feedback and the transition into each final build.

## Teaching repairs

Nine runtime studios supply four explicit teaching steps, prerequisites, a complete independently runnable example, a bounded variation, three hints, a complete reference, exact observations and failure diagnosis. A new applied quiz question and flashcard address each studio’s misconception. Wrong-answer review returns to that studio, rather than an unrelated general definition.

| Program/session | Gap addressed | Student evidence |
| --- | --- | --- |
| Bootcamp 5 | Retry arithmetic did not demonstrate actual coroutine cancellation | Actual event-loop deadline, cleanup events, permanent failure and exhausted-attempt checks |
| Bootcamp 14 | Approval replay needed an inspectable transaction failure | Committed fixture, injected mid-operation rollback, unchanged draft, one local receipt on retry/replay |
| Workshops 2 | Normalized output lost its field-level source evidence | Raw line/value/line-number records, preserved supplier punctuation, conflicting spans and no invented total |
| Workshops 11 | Aggregate routing accuracy could conceal a failed class or missing output | Stable case-ID join, retained missing predictions, per-class denominators and an all-billing regression |
| Engineering 8 | A fixed character cut could separate a policy from its exception | Exact final retriever helper, intact evidence units and explicit refusal of an oversized relevant unit |
| Engineering 29 | Useful-output accounting needed complete attempted populations | Failed-work cost retained, unknown cost separate from zero, zero-acceptance ratio undefined, nearest-rank p95 |
| Accelerator 13 | Shape/type checks alone allowed contradictory response envelopes | Exact object/schema, document-bound unique citations, integer counts and supported/empty-result invariants |
| Accelerator 16 | Sentence selection could omit an unmatched policy condition | Whole small-document context, explicit overflow error, separate no-match outcome |
| Accelerator 25 | Database commit and broker delivery were easy to conflate | Committed accepted row after enqueue failure, explicit requeue, duplicate consumption and content-identity conflict |

Accelerator lesson 62 also rejects null/array proposals and blank queries before execution. Lesson 85 now deep-copies nested observations before passing them to an injected provider transport, teaches why an outer list copy is insufficient, and includes the mutation counterexample in the exercise/reference.

## Final-project repairs

All four capstones now include a program-specific student build walkthrough before their complete inline files. The walkthrough identifies the exact functions, state and storage boundaries, explains each verification step, maps failed observations to the first boundary to inspect and sets bounded extension work. The assembly chapter also includes this teaching before the final build. Tests and complete commands are part of the lesson; no external course or repository supplies missing code.

- **Bootcamp:** pure bounded-agent tests precede HTTP assembly. The guide traces trusted identity, failed-result persistence, exact-payload approval, row locking, local replay and the distinction from remote delivery.
- **Workshops:** the real parser and stored draft retain field_evidence and conflicting spans. Duplicate values cannot silently overwrite a field. Schema correction and human confirmation remain separate states.
- **Engineering:** the actual final retriever preserves reviewed paragraph units and their exceptions, refuses unsafe truncation, and serializes candidate-key inputs canonically. The guide explicitly separates the local scripted SaaS from the earlier voice, mixed-media, workspace and cloud experiments. Active-policy selection and a real answer cache are not implied features.
- **Accelerator:** the actual HTTP context adapter retains the entire bounded policy document once any sentence matches. This prevents a refund rule being returned without its unmatched exclusion. Oversized matched context returns 409/context_review_required. The bounded agent rejects malformed or contradictory evidence before completion; valid empty retrieval and service failure remain different states.

The common DRF capstone adapter also rejects approval of a receipt/non-draft before reading draft-only fields, fixing an HTTP 500 path. Acceptance runners retain partial failed reports, replace stale success reports, preserve nonzero exits and use the same nearest-rank p95 convention as the teaching. Engineering’s evaluation runner retains malformed response objects as failed cases.

## Verification and its limits

The exact published examples and full variation references were executed, rather than separate test-only implementations. This includes the existing 36 Engineering references, 42 technical Bootcamp/Workshops references, 226 Accelerator/Tutor baseline/reference blocks, and the 18 new studio blocks. Separate audits execute 36 Engineering and 41 practical baseline examples and test fixed evaluation cases and injected regressions. The Tutor and business examples are regression coverage, not additional programs changed by this request.

`student-depth-content.json` records all 183 target lesson structures, nine studio feedback targets and four fresh project reconstructions from their inline Markdown. All 17 published pure capstone tests pass from those reconstructed files. `student-depth-checks.py` proves that assertion and dependency failures replace stale successful acceptance reports.

`student-depth-operations.json` records four actual fresh-volume Docker builds from the inline project files. Only host ports were overridden to 8311/8312/8314/8315, preserving the existing learner services on 821x and the academy/Workshop apps. All four passed HTTP acceptance, API-container replacement with the same stored ID, database outage/recovery and a fresh PostgreSQL dump/restore comparison of actual IDs and payload/text. Engineering also passed its actual 120-case HTTP harness and the exception/overflow regressions. Accelerator passed actual persisted ingestion, bounded-agent and MCP initialize/discover/call/error/shutdown checks. Temporary review projects and volumes were removed afterward.

All 183 pre-existing target lesson IDs were retained when publishing, and every deployed target content hash matched the reviewed source. The regression suite checks instructor edits, notes, completions and protected selected-answer feedback. Desktop/mobile reading and feedback evidence is recorded separately in `student-depth-browser.json`.

These observations establish the named local software contracts. They do not establish live-model semantic quality, production authentication, external message delivery, GPU throughput or cloud autoscaling. The lessons explicitly teach what additional evidence those claims require.

## Final application walkthrough

The final Docker-backed browser pass read all **183 lessons / 1,174 chapters** and compared every rendered code block with the authored book. All nine runtime studios passed wrong-answer feedback → correct explanation → successful retry, primary exercise/reference access, flashcard reveal and note save/reload. All four capstone-file APIs matched their source files. Anonymous previews worked without visible credits/license sections. Mobile 390px and 320px checks covered the new teaching and final-project readers, course-sheet access and horizontal overflow; no page errors or failed API responses were observed.

The full 67-test Django run passed 64 checks and exposed three inventory assertions left behind by the earlier Python program addition (program count, kit chapter count and a four-program-only layout test). Those assertions were updated to the seven-program platform, while Python retains its dedicated advanced teaching assertions. All three affected inventory checks passed their focused reruns. No runtime application change was required for those failures. The offline ZIP was synchronized with both final published curriculum JSON files and now describes all five authored programs plus the two imported programs.
