# Student teaching review — 20 October 2026

The three independent programs retain their projects and sequences: 24 bootcamp sessions, 18 workshop studios and 18 freelancing sessions. This revision addresses the actual teaching rather than using word, chapter or question totals as proxies for quality.

## What was wrong

The previous generator concatenated broad upstream chapters, raw code studies and imported exercises. This introduced unrelated NLP/ML tutorials into extraction and triage, code-review assistants into the policy-agent project, and technical cost/caching material into commercial delivery lessons. Some Python fences were syntactically invalid; others needed files or helpers the lesson never supplied. Several statements incorrectly implied prompts guarantee structure, existing citations guarantee support, or unmeasured percentage claims establish safety/cost savings.

The per-session findings and replacements are in `student-content-audit.json`. Each of its 60 rows identifies the defect, replacement teaching, targeted extension, boundary challenge and acceptance checks.

## The revised learning path

Every session begins with prerequisites, a decision explained in context, and definitions of the concepts its assessments actually use. Students then study a complete worked example, explain its mechanism and limits, make a targeted change and build the session artifact against explicit acceptance checks. Exercises retain concrete inputs and expected outcomes; reflections now use the session's actual extension and boundary challenge.

The 41 single-file Python examples include imports, synthetic fixtures, assertions, expected stdout and explanatory walkthroughs. They run independently in isolated scratch directories without paid calls or missing support files. Their stated boundaries matter: a fake adapter does not establish model quality; a view-state dictionary is not a browser usability test; a database helper is not proof of an HTTP integration; an in-memory ledger does not establish concurrent durable effect guarantees. The capstone exercises explicitly add those missing boundaries.

Bootcamp session 19 supplies a complete seven-file DRF/PostgreSQL/Nginx Docker experiment with runtime configuration, a private database network, a named volume and dependency-backed readiness. Its deliberately plain static UI isolates deployment boundaries; the student's capstone still uses its own React interface and authenticated application. The loopback-only synthetic lab is not a production deployment template. It has a separate build, browser save/readback, container replacement and database-outage verification. The following recovery session also supplies a complete PostgreSQL dump/isolated-restore script, executed against the synthetic lab and checked by source/restored content equality.

The 18 freelancing sessions retain the authored client-delivery concepts and now include completed, explicitly fictional artifacts: discovery evidence, baseline and sensitivity calculations, offer, acceptance register, effort/support estimates, data flow, pilot record, feedback triage, client report, milestone risks, change assessment, ownership handover, trainee observation, incident review, case-study claim audit, unsent outreach and final promise-to-evidence audit. These are analysis specimens, not claims that a real customer was interviewed or helped.

Each lesson has three focused quiz questions: its authored scenario, a concept distinction and a new question about the worked example's mechanism or limitation. Unrelated imported quizzes and glossary cards are removed. Fewer aligned questions are preferable to a large question bank that tests material the session never teaches.

## Verification boundary

`tests/student-content-audit.py` extracts and executes the exact published Python code blocks, compares stdout, parses all Python fences, checks exercise/acceptance alignment and recalculates the fictional economics. It does not substitute a hidden reference implementation. `tests/student-reading.cjs` renders all 60 lessons and checks that every chapter and full code fence reaches the learner; those rendering checks complement the editorial review rather than certify pedagogical quality.

Learner practical evidence remains self-reported. A code assertion establishes its specific local invariant, not production readiness or semantic correctness. Real factual support, usability, fresh-operator setup and client acceptance still require the observations stated in the exercises. No real client messages or public posts are sent.

The GenAI Accelerator and its original source library remain independent. Stable practical lesson IDs and versioned activity history preserve earlier learner work. Recognized generated content can upgrade; instructor-authored edits remain protected. The source MIT notice is retained without learner redirects or a workbook dependency.
