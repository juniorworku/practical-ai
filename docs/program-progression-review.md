# Program progression review

Reviewed six independent paths (209 sessions). The 523 historical library readings remain supplementary; they are not hidden prerequisites. This review concerns the teaching sequence and project dependencies, rather than treating a passing UI test as a curriculum review.

## Changes made

| Program | Entry and progression | Final project boundary |
| --- | --- | --- |
| AI Agent Bootcamp | Scope → workspace/cases → model contracts → evidence → bounded actions → API/data → evaluation → deployment → support-agent integration. | Session 22 now maps the required contracts to earlier teaching and requests full supported, unsupported, denied-action and timeout traces. Findings and release packaging continue in 23–24. |
| AI Workshops | Five complete use-case studios teach validation, review, evidence and evaluation before the integration studio. | Select one studio in 16, learn persistence/integration in 17, then demonstrate that app and index the actual studio evidence in 18. The program does not require five deployed applications. |
| Freelancing Masterclass | Buyer/baseline → offer/acceptance/estimate → data/pilot → evaluation/change control → handover/support → case study. | The final simulated client packet must reconcile promises, scope, observed acceptance, recovery and client communication. No real outreach or purchase is required. |
| AI Engineering | Session contracts and streaming precede voice acceptance; provenance/indexing precede grounded chat; tool/state/approval controls precede workspace automation; evaluation precedes release; capacity/budgets precede graduation. | Five project maps distinguish session-level local acceptance from later deployment, concurrency and cloud evidence. Each names the earlier source lessons and required retained counterexamples. |
| GenAI Accelerator | Twenty labs now follow the relevant instruction, rather than appearing after all 85 lessons. The provider decision adapter follows the agent-loop lessons. The early MCP preview moves after protocol foundations. | Each lab explicitly identifies its taught inputs and integration checks. Database/worker examples shown early are previews until the API, migration, queue and Compose sequence is complete. |
| Terminal Tutor | Workspace/exit codes → predict/run/change/debug → tool permissions/instruction inspection → bounded resumption. The first guide now teaches the Python vocabulary before its filesystem specimen. | The resumption project reuses the learner’s actual path, command, exit code, assertions, permission boundary and next action. It requires rerunning evidence after source changes. |

## Instructional corrections

Every lesson begins with its entry/preparation requirements, a recap of the preceding mechanism where applicable, the stage artifact to preserve, and the next connection. Project checkpoints include a taught-to-required evidence map, assembly instructions, and feedback for diagnosing the first broken boundary. The original bounded exercise remains useful practice, but is explicitly distinguished from completing the integrated project.

The module-wide production criteria previously demanded timeout/overload/retained-work experiments even before those concepts were taught. They now assess the current taught boundary. Later project maps still require concrete recovery, ownership, load, quota and release evidence where those concepts have been taught. Unknown and untested values cannot become passing release claims.

The MCP discovery lab had an advertised discovery objective but practiced parallel result merging. It now teaches and tests discovery versus host authorization, exact input schema, denied writes and empty-success semantics. Its complete inline SDK integration remains the separate real protocol exercise. The scenario question, variation, hints and reference now use that same boundary.

## Persistence and instructor ownership

The importer relocates a recognized generated Accelerator sequence in a transaction, first moving rows to unused temporary positions to avoid unique-order collisions. It changes order on existing identities rather than replacing lessons. Notes, completions and old practice revisions remain attached. A manually rearranged or extended instructor sequence is preserved; it is not silently forced back into the generated path. Custom teaching is preserved independently of order changes. Such a custom path may need its own prerequisite review.

Course practice is versioned: previous revision records remain stored; revised practical rubrics have their own practice state. This does not certify historical submissions against the expanded requirements.

## Validation

`tests/progression-audit.py` checks all 209 sessions for earlier, same-program dependencies and all 31 project checkpoint maps for covered source lessons. It also checks that the grouped course outline preserves the interleaved Accelerator sequence, and executes the new Tutor bootstrap’s passing and deliberately failing assertions. This validates structural dependencies, not semantic mastery; the source mappings and project instructions were reviewed against the lesson topics and actual exercises.

Backend regression tests cover original-order upgrades, stable identities/notes/completions/practice, repeat imports, manual-order preservation and public entry requirements. Existing teaching audits execute the published examples and reference solutions. Browser verification checks the deployed entry requirements, interleaved outline, lesson navigation and project chapter rendering.

Final verification on this revision:

- Progression audit: 6 programs, 209 sessions, 31 mapped project checkpoints; no forward prerequisites.
- Browser review: exact served progression/revision parity for all 209 sessions, all six entry panels and 31 project chapters/rubrics; interleaved outline preserved; no browser errors.
- Published teaching: 226 Accelerator/Tutor baseline/reference runs, 47 Bootcamp/Workshop/Freelancing references, 36 Engineering references and 36 Engineering baselines passed. The 120-case evaluation harness retained its critical-failure and unavailable-run probes.
- PostgreSQL backend suite: 32 tests passed, including reorder preservation and repeat-import behavior.
- Frontend TypeScript/Vite build and whitespace checks passed. Academy Docker deployment is healthy at http://127.0.0.1:8080/.

Machine-readable evidence: [dependency map](progression-audit.json), [browser review](progression-browser.json), [imported teaching execution](imported-teaching-audit.json), [practical references](practical-student-review.json), [engineering references](engineering-student-review.json).
