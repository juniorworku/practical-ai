# Practical academy program guide

All seven programs are free. Suggested weeks describe sustained practice, not a short video course. Time estimates include implementation, debugging and review; learners may proceed at their own pace. Each session has a worked example, a build sequence, a deliberate failure, three acceptance checks, and a specific deliverable. The academy records self-reported completion and private notes; selected browser labs execute Python with deterministic checks. Other project submissions are self-reported evidence and require review; a checked task is not proof of a working deployment.

## AI Agent Bootcamp

8 weeks · 24 build sessions · 50 estimated practice hours

An eight-week engineering path: build a document-backed support agent with explicit tool contracts, evaluation datasets, human approval, and a reproducible deployment.

Prerequisites: Python basics · guided setup

Capstone: A document-backed support agent that drafts answers with citations and proposes, but never silently executes, consequential actions.

- **01. From prompts to useful systems** — 01 · Problem and foundations; `docs/problem-brief.md`
- **02. A reproducible Python workspace** — 01 · Problem and foundations; `README.md`
- **03. Build a small evaluation dataset first** — 01 · Problem and foundations; `data/evaluation.jsonl`
- **04. Prompt contracts and structured outputs** — 02 · Contracts and model boundaries; `app/contracts.py`
- **05. Provider adapters, timeouts, and failures** — 02 · Contracts and model boundaries; `app/providers.py`
- **06. Context budgets and source selection** — 02 · Contracts and model boundaries; `app/context.py`
- **07. Ingestion, normalization, and versioning** — 03 · Retrieval and evidence; `app/ingestion.py`
- **08. Chunking and a lexical retrieval baseline** — 03 · Retrieval and evidence; `app/retrieval.py`
- **09. Grounding, citations, and abstention** — 03 · Retrieval and evidence; `docs/grounding-audit.md`
- **10. Tools as typed, permissioned interfaces** — 04 · Tools and bounded agency; `app/tools.py`
- **11. State machines and bounded agent loops** — 04 · Tools and bounded agency; `app/agent_loop.py`
- **12. Human approval and idempotent actions** — 04 · Tools and bounded agency; `app/actions.py`
- **13. HTTP contracts and a usable API** — 05 · Application and data; `docs/api-contract.md`
- **14. Persistence, transactions, and data ownership** — 05 · Application and data; `docs/data-model.md`
- **15. Design reviewable user experiences** — 05 · Application and data; `docs/usability-review.md`
- **16. Build a regression harness** — 06 · Evaluation and security; `evals/report.json`
- **17. Prompt injection and untrusted documents** — 06 · Evaluation and security; `docs/threat-model.md`
- **18. Observability, cost, and latency budgets** — 06 · Evaluation and security; `docs/operations-metrics.md`
- **19. Containerize the complete application** — 07 · Deployment and reliability; `compose.yaml`
- **20. Failure recovery and release checklists** — 07 · Deployment and reliability; `docs/runbook.md`
- **21. Choose orchestration complexity deliberately** — 07 · Deployment and reliability; `docs/architecture-decision.md`
- **22. Capstone build: support-agent vertical slice** — 08 · Capstone and review; `docs/capstone-evidence.md`
- **23. Capstone evaluation and peer critique** — 08 · Capstone and review; `docs/capstone-review.md`
- **24. Package, hand over, and plan the next release** — 08 · Capstone and review; `docs/release-package.md`

## AI Workshops

6 weeks · 18 build studios · 50.5 estimated practice hours

Six substantial build studios across six weeks: turn documents, meetings, research, and business workflows into tested, reviewable AI applications.

Prerequisites: Beginner to intermediate · practice required

Capstone: A portfolio of six scoped workflows: extraction, meeting actions, grounded research, support triage, content review, and a final app sprint.

- **01. Model the document before automating it** — Studio 01 · Document extraction; `studio-01/schema-and-fixtures.json`
- **02. Build a validated extraction pipeline** — Studio 01 · Document extraction; `studio-01/validated_records.jsonl`
- **03. Review queues and extraction evaluation** — Studio 01 · Document extraction; `studio-01/evaluation-and-handover.md`
- **04. Distinguish statements, decisions, and commitments** — Studio 02 · Meeting actions; `studio-02/action-schema.json`
- **05. Build an action register with human confirmation** — Studio 02 · Meeting actions; `studio-02/action-register.csv`
- **06. Evaluate summaries for omissions and false commitments** — Studio 02 · Meeting actions; `studio-02/review-report.md`
- **07. Form a question and an evidence plan** — Studio 03 · Grounded research; `studio-03/evidence-plan.md`
- **08. Build a claim-and-citation notebook** — Studio 03 · Grounded research; `studio-03/claim-notebook.jsonl`
- **09. Run a small benchmark and write a decision memo** — Studio 03 · Grounded research; `studio-03/decision-memo.md`
- **10. Design a taxonomy with an uncertainty route** — Studio 04 · Support triage; `studio-04/taxonomy.md`
- **11. Routing rules, confusion matrices, and fallback** — Studio 04 · Support triage; `studio-04/routing-evaluation.csv`
- **12. Connect triage to a reviewable work queue** — Studio 04 · Support triage; `studio-04/work-queue-demo.md`
- **13. Build a content brief and a factual boundary** — Studio 05 · Content operations; `studio-05/content-brief.md`
- **14. Draft, critique, and revise with a rubric** — Studio 05 · Content operations; `studio-05/revision-log.md`
- **15. Design a responsible publishing workflow** — Studio 05 · Content operations; `studio-05/publishing-runbook.md`
- **16. Scope a useful end-to-end application** — Studio 06 · App sprint; `studio-06/release-scope.md`
- **17. Integrate, persist, and test the workflow** — Studio 06 · App sprint; `studio-06/end-to-end-evidence.md`
- **18. Deliver a portfolio of practical workflows** — Studio 06 · App sprint; `portfolio/README.md`

## Freelancing Masterclass

6 weeks · 18 delivery sessions · 40 estimated practice hours

A six-week client-delivery practicum: validate a problem, scope a paid pilot, build and evaluate a workflow, manage changes, and hand over responsibly.

Prerequisites: One working workflow · synthetic client practice

Capstone: A complete simulated client engagement, from discovery and proposal to acceptance testing and handover; no income or client acquisition is guaranteed.

- **01. Choose a workflow and a buyer** — 01 · Opportunity and customer discovery; `client-01/opportunity-brief.md`
- **02. Conduct discovery with evidence** — 01 · Opportunity and customer discovery; `client-01/discovery-dossier.md`
- **03. Measure the baseline and the decision value** — 01 · Opportunity and customer discovery; `client-01/baseline-model.csv`
- **04. Package a service with a bounded outcome** — 02 · Offer and scope; `client-02/service-offer.md`
- **05. Write a statement of work with acceptance tests** — 02 · Offer and scope; `client-02/statement-of-work.md`
- **06. Estimate effort, support, and pricing assumptions** — 02 · Offer and scope; `client-02/effort-and-cost-model.csv`
- **07. Map data, access, and retention** — 03 · Data and prototype; `client-03/data-access-plan.md`
- **08. Build a thin pilot with visible limitations** — 03 · Data and prototype; `client-03/pilot-evidence.md`
- **09. Use client feedback without losing scope** — 03 · Data and prototype; `client-03/feedback-decision-log.md`
- **10. Create a client-readable evaluation report** — 04 · Quality and delivery; `client-04/evaluation-report.md`
- **11. Plan delivery milestones and manage risk** — 04 · Quality and delivery; `client-04/delivery-plan.md`
- **12. Manage change requests and commercial boundaries** — 04 · Quality and delivery; `client-04/change-requests.md`
- **13. Deploy with client-owned access and a recovery path** — 05 · Handover and operations; `client-05/operations-handover.md`
- **14. Train users and run acceptance testing** — 05 · Handover and operations; `client-05/acceptance-record.md`
- **15. Support boundaries, maintenance, and incident review** — 05 · Handover and operations; `client-05/support-and-maintenance.md`
- **16. Write an evidence-based case study** — 06 · Credibility and repeatability; `client-06/case-study.md`
- **17. Prepare outreach and qualification responsibly** — 06 · Credibility and repeatability; `client-06/outreach-drafts.md`
- **18. Complete the simulated client engagement** — 06 · Credibility and repeatability; `client-06/final-delivery-index.md`

## Inline practice and supplementary lab archive

The three core programs teach in the reader itself. They include complete offline worked examples and client-delivery specimens; no workbook or lab-pack download is required. The earlier six-function lab pack remains supplementary material in the independent Accelerator/learning kit, not a prerequisite for core exercises.

## Revision and learner work

The current generated teaching revision is `academy-course-books-v5`. Stable practical lesson IDs retain enrollment, notes and completion. Recognized prior generated text upgrades; instructor-authored edits remain protected. Earlier practice and immutable quiz attempts remain under their earlier activity revisions, so a changed assessment does not silently reuse a previous score.

## Interactive learning workspace

Each session includes prerequisites, focused explanations, a complete worked example, a targeted extension, a boundary challenge, an exercise hint, three specific reflections, three graded checks with explanations, lesson-specific flashcards, an artifact submission with acceptance criteria and private notes. PostgreSQL stores learner work privately. Practical submissions and completion are self-reported; the academy does not execute or certify learner artifacts.

The public syllabus and each program's native lessons are independent of the GenAI Accelerator. All required teaching appears inline with no repository redirect or workbook dependency. `course-books.md` describes the editorial changes; `student-content-audit.json` records the actual defect and replacement for every session. `course-book-manifest.json` is the current inventory, not a teaching-quality score.


## Guided student teaching review

The [current 60-lesson review](practical-student-review.md) documents the step-by-step concept teaching, bounded practice, complete references, progressive hints and selected-answer feedback now available in the original three programs. Larger project work remains an explicit integration stage after practice.

## Python for AI — advanced independent program

12 sessions, 77 teaching chapters and approximately 67 hours of planned implementation/review work across 8–12 self-paced weeks. Entry skills: working Python, classes, tests, HTTP/JSON, virtual environments and basic SQL. The course starts at typed software contracts rather than beginner syntax or algorithm derivations.

1. Typed boundaries, runtime validation and provider protocols.
2. Framed streaming, lazy iteration, UTF-8 and bounded buffering.
3. Fixed worker pools, backpressure, ordering and structured concurrency.
4. Overall deadlines, cancellation propagation and resource cleanup.
5. Fake/real provider adapters, response validation and honest usage accounting.
6. Safe retries, elapsed budgets and uncertain external effects.
7. Owner-first retrieval, stable ranking, abstention and context admission.
8. Owner/model/source/prompt/schema cache identity and invalidation.
9. Transactional SQLite, connection ownership, rollback and restart readback.
10. Fixed evaluation cases, failure reports, quantile conventions and quality scope.
11. HTTP identity, request bounds, readiness, admission and process-local quotas.
12. An integrated containerized knowledge service with the complete files, tests and operating runbook.

Every lesson includes a complete standard-library baseline, a matching assigned extension with complete reference variation, failure experiments, five scenario quizzes with feedback, five flashcards, reflection guidance and practical evidence criteria. The optional real-model adapter uses Ollama `/api/chat` and an installed local model; neither model quality nor live inference is claimed by offline fixture tests. Program source: `scripts/python_ai.py`, examples and complete variations beside it. Final project: `backend/academy/content/capstones/python-for-ai/`.

The student-depth review adds 11 runnable advanced studios, per-stage diagnostics, a self-contained offline HTTPX adapter example, and cumulative pipeline/evaluation/HTTP implementation chapters before the final exercise. Student builds are verified from published text, not hidden repository helpers. The ten source/configuration files plus README include 25 tests, a versioned evaluator, actual HTTP probes and a container replacement/restore runbook.

The full Build · Measure · Operate brief appears only in the engineering paths: Bootcamp, Workshops, AI Engineering, GenAI Accelerator and Python for AI. Each uses its own module scenario. Freelancing and Terminal Tutor retain their contextual delivery/reliability teaching without this engineering overview block.
