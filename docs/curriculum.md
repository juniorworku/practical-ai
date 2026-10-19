# Practical academy program guide

All three programs are free. Suggested weeks describe sustained practice, not a short video course. Time estimates include implementation, debugging and review; learners may proceed at their own pace. Each session has a worked example, a build sequence, a deliberate failure, three acceptance checks, and a specific deliverable. The academy records self-reported completion and private notes; it does not execute or grade submitted code.

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

## Offline lab pack

Six standard-library exercises cover retrieval, extraction validation, citation integrity, bounded agents, routing metrics, and workflow economics. Download from the learning reader or Accelerator. Exercise stubs intentionally fail until implemented; the supplied reference passes 17 tests. Templates cover discovery, scope, evaluation, estimates, change requests, and handover. The original 523 source readings, Accelerator, and Tutor remain available for depth.

## Revision and previous progress

This is `academy-practical-v2`. Recognized original introductory lessons are moved to archived programs, retaining their IDs, learner notes and completion records. They are excluded from active course totals. Their old completions do not assert that the learner completed the new practical sessions. The seeder retains instructor edits and does not reset existing v2 progress.
