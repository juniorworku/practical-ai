# Native course books

The three programs teach inside the app. Their original short briefs are now applied case chapters within a sequenced course book. All concepts, implementation examples, case walkthroughs, input/output exercises, checks and reflection prompts are readable there. No workbook or repository redirect is needed.

Concept material and selected review questions are adapted from Rohit Ghumare’s MIT-licensed AI Engineering from Scratch snapshot aae3dc64e53457aae952e90ee9304fd13f9941a8. The source license and credit appear in every lesson. Original academy material includes eighteen client-delivery teaching chapters, sixty specific input/output experiments, contextual case studies and practical rubrics. Source selection and revision are recorded in course-book-manifest.json.

Chapter counts include concept chapters, implementation code studies and applied cases; they are not a count of unique topics. Shared foundations are intentionally retaught where needed so each program remains independent. Coding work runs in a learner’s scratch environment; this application records evidence, it does not execute arbitrary code.

## AI Agent Bootcamp

### 01. From prompts to useful systems

- The Agent Loop: Observe, Think, Act (Concepts & implementation)
- The Agent Loop: Observe, Think, Act · implementation walkthrough (Code study)
- Define the Outcome Before You Choose the Output (Concepts & implementation)
- Apply it: From prompts to useful systems (Worked case & project)

Exercise: Separate a draft from an action

### 02. A reproducible Python workspace

- Python Environments (Concepts & implementation)
- Debugging and Profiling (Concepts & implementation)
- Apply it: A reproducible Python workspace (Worked case & project)

Exercise: Resolve files independently of the shell

### 03. Build a small evaluation dataset first

- Evaluation & Testing LLM Applications (Concepts & implementation)
- Task Spec Format (Concepts & implementation)
- Apply it: Build a small evaluation dataset first (Worked case & project)

Exercise: Keep a holdout case out of tuning

### 04. Prompt contracts and structured outputs

- Prompt Engineering: Techniques & Patterns (Concepts & implementation)
- Structured Outputs: JSON, Schema Validation, Constrained Decoding (Concepts & implementation)
- Structured Outputs: JSON, Schema Validation, Constrained Decoding · implementation walkthrough (Code study)
- Apply it: Prompt contracts and structured outputs (Worked case & project)

Exercise: Validate structure and meaning separately

### 05. Provider adapters, timeouts, and failures

- Function Call Dispatcher (Concepts & implementation)
- Function Call Dispatcher · implementation walkthrough (Code study)
- Caching, Rate Limiting & Cost Optimization (Concepts & implementation)
- Apply it: Provider adapters, timeouts, and failures (Worked case & project)

Exercise: Retry only a safe operation

### 06. Context budgets and source selection

- Context Engineering: Windows, Budgets, Memory, and Retrieval (Concepts & implementation)
- Context Engineering: Windows, Budgets, Memory, and Retrieval · implementation walkthrough (Code study)
- Embeddings & Vector Representations (Concepts & implementation)
- Apply it: Context budgets and source selection (Worked case & project)

Exercise: Fit a context envelope

### 07. Ingestion, normalization, and versioning

- Data Management (Concepts & implementation)
- Data Provenance and Training-Data Governance (Concepts & implementation)
- Apply it: Ingestion, normalization, and versioning (Worked case & project)

Exercise: Activate a source revision deliberately

### 08. Chunking and a lexical retrieval baseline

- Chunking Strategies, Compared (Concepts & implementation)
- Chunking Strategies, Compared · implementation walkthrough (Code study)
- Hybrid Retrieval with BM25 and Dense Embeddings (Concepts & implementation)
- Hybrid Retrieval with BM25 and Dense Embeddings · implementation walkthrough (Code study)
- Apply it: Chunking and a lexical retrieval baseline (Worked case & project)

Exercise: Compare retrieval on fixed labels

### 09. Grounding, citations, and abstention

- RAG (Retrieval-Augmented Generation) (Concepts & implementation)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance (Concepts & implementation)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance · implementation walkthrough (Code study)
- Apply it: Grounding, citations, and abstention (Worked case & project)

Exercise: Reject a misleading citation

### 10. Tools as typed, permissioned interfaces

- The Tool Interface — Why Agents Need Structured I/O (Concepts & implementation)
- Tool Schema Design — Naming, Descriptions, Parameter Constraints (Concepts & implementation)
- Tool Registry with Schema Validation (Concepts & implementation)
- Apply it: Tools as typed, permissioned interfaces (Worked case & project)

Exercise: Enforce a tool contract in the dispatcher

### 11. State machines and bounded agent loops

- The Agent Loop: Observe, Think, Act (Concepts & implementation)
- The Agent Loop: Observe, Think, Act · implementation walkthrough (Code study)
- Agent Harness Loop Contract (Concepts & implementation)
- Agent State Machines — Graphs, Nodes, Checkpoints (Concepts & implementation)
- Apply it: State machines and bounded agent loops (Worked case & project)

Exercise: Stop a looping agent

### 12. Human approval and idempotent actions

- Human-in-the-Loop: Propose-Then-Commit (Concepts & implementation)
- Checkpoints and Rollback (Concepts & implementation)
- Approval records, atomic claims and uncertain outcomes (Implementation design)
- Apply it: Human approval and idempotent actions (Worked case & project)

Exercise: Bind approval to an exact revision

### 13. HTTP contracts and a usable API

- APIs & Keys (Concepts & implementation)
- Building a Production LLM Application (Concepts & implementation)
- Apply it: HTTP contracts and a usable API (Worked case & project)

Exercise: Use an explicit API status contract

### 14. Persistence, transactions, and data ownership

- Repo Memory and Durable State (Concepts & implementation)
- Stateful Graph Orchestration — Durable Execution and Checkpoints (Concepts & implementation)
- Apply it: Persistence, transactions, and data ownership (Worked case & project)

Exercise: Detect a lost update

### 15. Design reviewable user experiences

- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Choose Prototype, Pilot, or Production Deliberately (Concepts & implementation)
- Apply it: Design reviewable user experiences (Worked case & project)

Exercise: Make status tell the truth

### 16. Build a regression harness

- Eval-Driven Agent Development (Concepts & implementation)
- Capstone Lesson 27: Eval Harness with Fixture Tasks (Concepts & implementation)
- Apply it: Build a regression harness (Worked case & project)

Exercise: Turn a regression into a fixture

### 17. Prompt injection and untrusted documents

- Prompt Injection and the PVE Defense (Concepts & implementation)
- Indirect Prompt Injection — Production Attack Surface (Concepts & implementation)
- Apply it: Prompt injection and untrusted documents (Worked case & project)

Exercise: Treat a retrieved instruction as data

### 18. Observability, cost, and latency budgets

- OpenTelemetry GenAI Semantic Conventions (Concepts & implementation)
- Inference Metrics — TTFT, TPOT, ITL, Goodput, P99 (Concepts & implementation)
- FinOps for LLMs — Unit Economics and Multi-Tenant Attribution (Concepts & implementation)
- Apply it: Observability, cost, and latency budgets (Worked case & project)

Exercise: Measure useful output per cost

### 19. Containerize the complete application

- Docker for AI (Concepts & implementation)
- Security — Secrets, API Key Rotation, Audit Logs, Guardrails (Concepts & implementation)
- Apply it: Containerize the complete application (Worked case & project)

Exercise: Persist outside a disposable container

### 20. Failure recovery and release checklists

- Shadow Traffic, Canary Rollout, and Progressive Deployment for LLMs (Concepts & implementation)
- Chaos Engineering for LLM Production (Concepts & implementation)
- Apply it: Failure recovery and release checklists (Worked case & project)

Exercise: Roll back behavior and compatible data

### 21. Choose orchestration complexity deliberately

- Anthropic's Workflow Patterns: Simple Over Complex (Concepts & implementation)
- Agent Framework Tradeoffs — Graph, Role, and Actor Orchestration (Concepts & implementation)
- Failure Modes — MAST, Groupthink, Monoculture, Cascading Errors (Concepts & implementation)
- Apply it: Choose orchestration complexity deliberately (Worked case & project)

Exercise: Justify orchestration complexity

### 22. Capstone build: support-agent vertical slice

- End-to-End RAG System (Concepts & implementation)
- Capstone Lesson 29: End-to-End Coding Agent on the Harness (Concepts & implementation)
- Apply it: Capstone build: support-agent vertical slice (Worked case & project)

Exercise: Trace a complete support case

### 23. Capstone evaluation and peer critique

- Verification Gates (Concepts & implementation)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance (Concepts & implementation)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance · implementation walkthrough (Code study)
- Apply it: Capstone evaluation and peer critique (Worked case & project)

Exercise: Use unseen cases for the final check

### 24. Package, hand over, and plan the next release

- Multi-Session Handoff (Concepts & implementation)
- Build a Feedback Ratchet with Ownership and Retirement (Concepts & implementation)
- Apply it: Package, hand over, and plan the next release (Worked case & project)

Exercise: Make handover reproducible

## AI Workshops

### 01. Model the document before automating it

- Structured Outputs: JSON, Schema Validation, Constrained Decoding (Concepts & implementation)
- Structured Outputs: JSON, Schema Validation, Constrained Decoding · implementation walkthrough (Code study)
- Text Processing — Tokenization, Stemming, Lemmatization (Concepts & implementation)
- Apply it: Model the document before automating it (Worked case & project)

Exercise: Represent missing fields honestly

### 02. Build a validated extraction pipeline

- Prompt Engineering: Techniques & Patterns (Concepts & implementation)
- Structured Outputs: JSON, Schema Validation, Constrained Decoding (Concepts & implementation)
- Structured Outputs: JSON, Schema Validation, Constrained Decoding · implementation walkthrough (Code study)
- Apply it: Build a validated extraction pipeline (Worked case & project)

Exercise: Validate arithmetic after parsing

### 03. Review queues and extraction evaluation

- Model Evaluation (Concepts & implementation)
- Design Success Metrics Before the Result Exists (Concepts & implementation)
- Design Success Metrics Before the Result Exists · implementation walkthrough (Code study)
- Apply it: Review queues and extraction evaluation (Worked case & project)

Exercise: Choose review over false acceptance

### 04. Distinguish statements, decisions, and commitments

- Dialogue State Tracking (Concepts & implementation)
- Text Summarization (Concepts & implementation)
- Apply it: Distinguish statements, decisions, and commitments (Worked case & project)

Exercise: Track a retracted commitment

### 05. Build an action register with human confirmation

- Agent State Machines — Graphs, Nodes, Checkpoints (Concepts & implementation)
- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Apply it: Build an action register with human confirmation (Worked case & project)

Exercise: Confirm one action revision

### 06. Evaluate summaries for omissions and false commitments

- Evaluation & Testing LLM Applications (Concepts & implementation)
- Design Success Metrics Before the Result Exists (Concepts & implementation)
- Design Success Metrics Before the Result Exists · implementation walkthrough (Code study)
- Apply it: Evaluate summaries for omissions and false commitments (Worked case & project)

Exercise: Score a lost dependency

### 07. Form a question and an evidence plan

- Define the Outcome Before You Choose the Output (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First · implementation walkthrough (Code study)
- Discover the Workflow People Actually Perform (Concepts & implementation)
- Discover the Workflow People Actually Perform · implementation walkthrough (Code study)
- Apply it: Form a question and an evidence plan (Worked case & project)

Exercise: Define a research decision

### 08. Build a claim-and-citation notebook

- RAG (Retrieval-Augmented Generation) (Concepts & implementation)
- Query Rewriting: HyDE, Multi-Query, and Decomposition (Concepts & implementation)
- Apply it: Build a claim-and-citation notebook (Worked case & project)

Exercise: Match a citation to its claim

### 09. Run a small benchmark and write a decision memo

- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance (Concepts & implementation)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance · implementation walkthrough (Code study)
- Design Success Metrics Before the Result Exists (Concepts & implementation)
- Design Success Metrics Before the Result Exists · implementation walkthrough (Code study)
- Apply it: Run a small benchmark and write a decision memo (Worked case & project)

Exercise: Compare candidates on common cases

### 10. Design a taxonomy with an uncertainty route

- Logistic Regression (Concepts & implementation)
- Handling Imbalanced Data (Concepts & implementation)
- Apply it: Design a taxonomy with an uncertainty route (Worked case & project)

Exercise: Leave an uncertainty route

### 11. Routing rules, confusion matrices, and fallback

- Model Evaluation (Concepts & implementation)
- Classical Metrics (Concepts & implementation)
- Apply it: Routing rules, confusion matrices, and fallback (Worked case & project)

Exercise: Read a confusion matrix by error

### 12. Connect triage to a reviewable work queue

- Anthropic's Workflow Patterns: Simple Over Complex (Concepts & implementation)
- Guardrails, Safety & Content Filtering (Concepts & implementation)
- Apply it: Connect triage to a reviewable work queue (Worked case & project)

Exercise: Keep routing and effect separate

### 13. Build a content brief and a factual boundary

- Prompt Engineering: Techniques & Patterns (Concepts & implementation)
- Context Engineering: Windows, Budgets, Memory, and Retrieval (Concepts & implementation)
- Context Engineering: Windows, Budgets, Memory, and Retrieval · implementation walkthrough (Code study)
- Apply it: Build a content brief and a factual boundary (Worked case & project)

Exercise: Define a factual content boundary

### 14. Draft, critique, and revise with a rubric

- Self-Refine and CRITIC: Iterative Output Improvement (Concepts & implementation)
- Eval-Driven Agent Development (Concepts & implementation)
- Apply it: Draft, critique, and revise with a rubric (Worked case & project)

Exercise: Critique against an observable rubric

### 15. Design a responsible publishing workflow

- Human-in-the-Loop: Propose-Then-Commit (Concepts & implementation)
- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Apply it: Design a responsible publishing workflow (Worked case & project)

Exercise: Invalidate approval after editing

### 16. Scope a useful end-to-end application

- Choose the Smallest Slice That Can Change the Decision (Concepts & implementation)
- Choose Prototype, Pilot, or Production Deliberately (Concepts & implementation)
- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Apply it: Scope a useful end-to-end application (Worked case & project)

Exercise: Choose an end-to-end sprint slice

### 17. Integrate, persist, and test the workflow

- Building a Production LLM Application (Concepts & implementation)
- Verification Gates (Concepts & implementation)
- Apply it: Integrate, persist, and test the workflow (Worked case & project)

Exercise: Prove state survives the interface

### 18. Deliver a portfolio of practical workflows

- Build a Feedback Ratchet with Ownership and Retirement (Concepts & implementation)
- Model, System, and Dataset Cards (Concepts & implementation)
- Apply it: Deliver a portfolio of practical workflows (Worked case & project)

Exercise: Present evidence across six studios

## Freelancing Masterclass

### 01. Choose a workflow and a buyer

- Buyer, workflow, and economic unit (Client delivery)
- Define the Outcome Before You Choose the Output (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First · implementation walkthrough (Code study)
- Apply it: Choose a workflow and a buyer (Worked case & project)

Exercise: Identify the buying roles

### 02. Conduct discovery with evidence

- Discovery interviews and evidence synthesis (Client delivery)
- Discover the Workflow People Actually Perform (Concepts & implementation)
- Discover the Workflow People Actually Perform · implementation walkthrough (Code study)
- Apply it: Conduct discovery with evidence (Worked case & project)

Exercise: Separate interview evidence

### 03. Measure the baseline and the decision value

- Baseline measurement and sensitivity analysis (Client delivery)
- Design Success Metrics Before the Result Exists (Concepts & implementation)
- Design Success Metrics Before the Result Exists · implementation walkthrough (Code study)
- FinOps for LLMs — Unit Economics and Multi-Tenant Attribution (Concepts & implementation)
- Apply it: Measure the baseline and the decision value (Worked case & project)

Exercise: Include the work automation leaves behind

### 04. Package a service with a bounded outcome

- Service packaging and staged commitments (Client delivery)
- Choose the Smallest Slice That Can Change the Decision (Concepts & implementation)
- Choose Prototype, Pilot, or Production Deliberately (Concepts & implementation)
- Apply it: Package a service with a bounded outcome (Worked case & project)

Exercise: Package a bounded pilot

### 05. Write a statement of work with acceptance tests

- Statements of work as executable acceptance (Client delivery)
- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Scope Contracts and Task Boundaries (Concepts & implementation)
- Apply it: Write a statement of work with acceptance tests (Worked case & project)

Exercise: Write a repeatable acceptance case

### 06. Estimate effort, support, and pricing assumptions

- Effort estimation, unit economics, and support capacity (Client delivery)
- FinOps for LLMs — Unit Economics and Multi-Tenant Attribution (Concepts & implementation)
- Caching, Rate Limiting & Cost Optimization (Concepts & implementation)
- Apply it: Estimate effort, support, and pricing assumptions (Worked case & project)

Exercise: Distinguish estimate from price

### 07. Map data, access, and retention

- Data inventory and least-privilege delivery (Client delivery)
- Data Provenance and Training-Data Governance (Concepts & implementation)
- Security — Secrets, API Key Rotation, Audit Logs, Guardrails (Concepts & implementation)
- Apply it: Map data, access, and retention (Worked case & project)

Exercise: Trace one data record

### 08. Build a thin pilot with visible limitations

- Prototype, pilot, and production evidence (Client delivery)
- Choose the Smallest Slice That Can Change the Decision (Concepts & implementation)
- Choose Prototype, Pilot, or Production Deliberately (Concepts & implementation)
- Apply it: Build a thin pilot with visible limitations (Worked case & project)

Exercise: Choose a useful pilot question

### 09. Use client feedback without losing scope

- Feedback triage and bounded iteration (Client delivery)
- Build a Feedback Ratchet with Ownership and Retirement (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First · implementation walkthrough (Code study)
- Apply it: Use client feedback without losing scope (Worked case & project)

Exercise: Route feedback to its owner

### 10. Create a client-readable evaluation report

- Client-readable evaluation and decision reports (Client delivery)
- Design Success Metrics Before the Result Exists (Concepts & implementation)
- Design Success Metrics Before the Result Exists · implementation walkthrough (Code study)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance (Concepts & implementation)
- RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance · implementation walkthrough (Code study)
- Apply it: Create a client-readable evaluation report (Worked case & project)

Exercise: Write a scoped result claim

### 11. Plan delivery milestones and manage risk

- Milestones, dependency risk, and delivery forecasting (Client delivery)
- Build an Evidence-Backed Execution Plan (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First (Concepts & implementation)
- Map Assumptions and Resolve the Riskiest One First · implementation walkthrough (Code study)
- Apply it: Plan delivery milestones and manage risk (Worked case & project)

Exercise: Plan around an access dependency

### 12. Manage change requests and commercial boundaries

- Change control and commercial conversations (Client delivery)
- Scope Contracts and Task Boundaries (Concepts & implementation)
- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Apply it: Manage change requests and commercial boundaries (Worked case & project)

Exercise: Assess a tiny request by its effects

### 13. Deploy with client-owned access and a recovery path

- Operational ownership, rollout, and recovery (Client delivery)
- Docker for AI (Concepts & implementation)
- Shadow Traffic, Canary Rollout, and Progressive Deployment for LLMs (Concepts & implementation)
- Apply it: Deploy with client-owned access and a recovery path (Worked case & project)

Exercise: Transfer operational ownership

### 14. Train users and run acceptance testing

- Training design and user acceptance rehearsal (Client delivery)
- Verification Gates (Concepts & implementation)
- Write Specifications That Preserve Judgment (Concepts & implementation)
- Write Specifications That Preserve Judgment · implementation walkthrough (Code study)
- Apply it: Train users and run acceptance testing (Worked case & project)

Exercise: Separate attendance from acceptance

### 15. Support boundaries, maintenance, and incident review

- Support design and incident learning (Client delivery)
- SRE for AI — Multi-Agent Incident Response, Runbooks, Predictive Detection (Concepts & implementation)
- Build a Feedback Ratchet with Ownership and Retirement (Concepts & implementation)
- Apply it: Support boundaries, maintenance, and incident review (Worked case & project)

Exercise: Recover from a stale policy

### 16. Write an evidence-based case study

- Portfolio claims and evidence-backed case studies (Client delivery)
- Model, System, and Dataset Cards (Concepts & implementation)
- Design Success Metrics Before the Result Exists (Concepts & implementation)
- Design Success Metrics Before the Result Exists · implementation walkthrough (Code study)
- Apply it: Write an evidence-based case study (Worked case & project)

Exercise: Support a portfolio claim

### 17. Prepare outreach and qualification responsibly

- Qualification and problem-specific outreach preparation (Client delivery)
- Define the Outcome Before You Choose the Output (Concepts & implementation)
- Discover the Workflow People Actually Perform (Concepts & implementation)
- Discover the Workflow People Actually Perform · implementation walkthrough (Code study)
- Apply it: Prepare outreach and qualification responsibly (Worked case & project)

Exercise: Separate a public fact from an inference

### 18. Complete the simulated client engagement

- Engagement synthesis and repeatable delivery (Client delivery)
- Multi-Session Handoff (Concepts & implementation)
- Build a Feedback Ratchet with Ownership and Retirement (Concepts & implementation)
- Apply it: Complete the simulated client engagement (Worked case & project)

Exercise: Audit the complete engagement
