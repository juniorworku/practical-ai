# AI Engineering: student teaching review

Review date: 2026-10-20. Scope: all 36 lessons of the independent twelve-week AI Engineering program, including their inline integration chapters. This review changes the teaching and assessment; functioning navigation alone is not evidence of a useful course.

## Teaching corrections

The previous sequence introduced many concepts as short definitions and then asked learners to make much larger integration changes. Each lesson now provides:

1. Concrete prerequisites and three concept explanations, ordered before implementation and exercises. Explanations describe the mechanism, a specific example and an engineering boundary.
2. A causal walkthrough of the baseline's inputs, state and output, followed by the complete executable baseline and its actual observation.
3. A bounded first practice task that extends that baseline, with aligned acceptance criteria. Larger integration work follows this practice rather than being presented as an unexplained first step.
4. Three progressively revealed hints and a complete runnable reference solution, including expected output and a diagnosis of likely failures. The solution is available inline; no workbook is required.
5. Reflection self-review guidance and answer-choice-specific quiz feedback. An incorrect answer explains the selected mistake and offers a direct return to the concept teaching.

There are 108 concept tutorials, 36 complete practice solutions, 108 staged hints, 108 reflection guidance responses and 324 answer-choice feedback entries. These counts describe coverage, not proof of teaching quality. The authored explanations and tasks were reviewed for the actual lesson mechanism and evidence expected from the student.

## Substantive example repairs

- Retrieval evaluation now calculates the fraction of relevant passages recovered, rather than calling any overlap “recall.” A two-gold/one-retrieved case produces 0.5 recall.
- Workspace practice executes approval, authorization, evidence, idempotency and uncertain-result decisions. It no longer compares literal expected/actual labels. Review fingerprints bind the exact proposed payload; changed text under a reused revision is rejected.
- The introductory evaluation executor sends concrete request data through a decision function. The later 120-case integration suite remains separate from the smaller teaching example.
- Tool practice checks record scope as well as the claimed owner. Grounded-stream practice rejects unauthorized citations and events after completion.
- Index activation checks dimensions, finite numeric values and a usable nonzero vector before cosine retrieval.
- Release reporting retains unavailable and unreviewed populations, validates count consistency and enforces a declared quality floor. Missing or untested evidence cannot become readiness through truthiness.
- Container teaching explicitly distinguishes its small unauthenticated network fixture from owner-isolation checks required in the final SaaS. Cloud arithmetic, local quotas and GPU worksheets remain labeled as fixture observations rather than scale benchmarks.

## Verification

Observed results against the updated Docker/PostgreSQL application:

- All 36 exact published practice solutions executed in isolated scratch directories with their expected output. Regression probes cover multi-passage recall, changed-payload approval and real request execution.
- All 36 baseline examples and the 120 concrete contract cases passed; an injected critical failure was detected.
- The browser walkthrough completed every engineering lesson: 198 rendered chapters with code fences compared to the authored source, 108 taught concepts, 36 complete practice references, 108 progressively revealed hints and all 324 answer-choice feedback entries checked against the server.
- Every lesson's wrong answers returned specific feedback, the review button returned to concept teaching, correct retries scored correctly, and saved reflections were read back through the API. Desktop feedback and mobile exercise reading were visually inspected; mobile practice did not overflow the page. No browser JavaScript errors were observed.
- The full Django/PostgreSQL suite passed all 23 tests, including teaching order, protected answer feedback, saved learning state and seeder preservation behavior.
- The original 60-session content audit passed, including 41 executable published Python examples. Shared learning-flow regression checks passed across all four practical programs.
- TypeScript/Vite production build and Docker service health checks passed. No database schema migration was required.

The full walkthrough preceded a final prose-spacing cleanup. All 36 published practice solutions were rerun afterward; all 36 served lesson revisions, chapters, exercise materials, reference solutions and reflection guidance then matched the reviewed source exactly. Final browser spot checks passed lessons 1, 24, 30 and 36 (22 chapters, all 36 answer-choice feedback entries), including corrected release logic and mobile reading. `git diff --check` passed. The machine-readable per-lesson review is in [engineering-student-review.json](engineering-student-review.json); the implementation audit executes the exact reference code published in the lesson data, rather than a separate test-only solution.

The baseline and practice checks are offline contract evidence. They do not establish live speech quality, provider answer quality, remote delivery guarantees, cloud concurrency or GPU capacity. The lessons teach the additional observations required for those claims.
