"""Original client-delivery teaching, not market-rate or legal advice."""
CHAPTERS = [
('Buyer, workflow, and economic unit', '''
### Start with the unit of work
A service becomes specific when it names one repeatable unit: a support ticket, a purchase record, or a participant handout. Write its trigger, input, current operator, output, and completion rule. A department is too large a unit for a first pilot. A single generated sentence is too small if it cannot finish an actual handoff. Use the fictional training provider throughout this course: the unit is one reviewed handout made from approved course notes.

### Separate three customers
The operator feels the friction, the operational owner is accountable for quality, and the budget owner can fund a change. An instructor may like your demo while the operations lead cannot provide source access and finance has not agreed to recurring costs. Draw three columns and put a named role in each. A single person may occupy multiple columns, but never infer authority from enthusiasm. Ask who accepts the deliverable and who maintains it after you leave.

### Score feasibility without hiding uncertainty
Use four gates before scoring attractiveness: permission to use representative inputs, an observable output standard, a reviewer with time, and a reversible fallback. Failure of a gate means investigate or decline. For opportunities that pass, compare monthly volume, minutes of avoidable work, cost of a wrong accepted output, and your familiarity with the workflow. Keep evidence and assumptions in separate fields. A score of four based on an assumption is not stronger evidence than a score of two based on observation.

### Worked opportunity comparison
Suppose course handouts occur 40 times a month, take 20 minutes each, and always receive instructor review. A payroll adjustment occurs 10 times, takes 8 minutes, and can move money. Even if payroll looks easier to automate technically, the first engagement has a more reversible draft boundary. Choose the handout workflow because you can observe review quality and stop before distribution. The decision is about the test you can run, not the most impressive demo.

### Write a falsifiable offer hypothesis
Use: “For [operator], we will test whether [bounded workflow] improves [observable measure], while [guardrail] stays within [limit], using [permitted inputs].” Add what would disprove it. For the training provider, a failed hypothesis might be that source notes are too incomplete for a reviewer to accept drafts without rewriting. That result should trigger source cleanup or a different service, rather than a stronger prompt.

### Practice record
Create rows for unit, operator, owner, authorizer, monthly volume, evidence source, unknown, and next test. Complete three candidate workflows. Select one and explain which missing fact could reverse your decision. Your output is a defensible opportunity choice; it is not evidence that someone will buy it.
'''),
('Discovery interviews and evidence synthesis', '''
### Observe the work before proposing a solution
A discovery interview should reconstruct a recent completed case. Start with “Show me the last handout you prepared.” Ask which source arrived, how the operator decided what to include, which correction took longest, who approved it, and what happened after approval. Follow the artifact through the workflow. Asking whether AI would help invites a prediction; observing a recent correction gives you evidence.

### Use an interview sequence
Begin with context and permission. Move to a specific recent example. Trace its normal path. Ask for an exception and its consequence. Identify the people and systems involved. Finish by summarizing your understanding and asking what you missed. Keep questions neutral: “What happens when a note is incomplete?” gives more information than “Would automatic completion solve missing notes?” The latter hides the possibility that completing missing information is unacceptable.

### Keep an evidence ledger
Use four columns: observation, interpretation, assumption, and unresolved question. “The instructor corrected three objectives in the example” is an observation. “Objectives are the largest source of rework” is an interpretation requiring more examples. “This happens every week” is an assumption until you inspect records or hear a supported account. Write a source and date beside each observation. Mark role-play data as simulated.

### Resolve disagreement instead of averaging it
An operator says review takes ten minutes; a manager says two. Both can be describing different intervals. Ask each to identify start and end events. One may count source lookup while the other measures only approval clicks. Define a common timing rule, observe a case, and keep the disagreement in the record until resolved. Do not average incompatible measurements into a confident six-minute baseline.

### Handle access as a separate decision
Permission to discuss a document is not permission to upload it. Use a redacted or synthetic sample during initial discovery. Record who can authorize production access, which fields can leave the organization, and whether provider processing is permitted. If those answers are missing, your next deliverable may be a data-access map rather than a prototype.

### Interview exercise
Role-play an operator who wants faster drafts and an instructor whose main problem is factual errors. Ask eight questions without proposing a product. Produce a current-state map, three observations, two contradictions, one disconfirming finding, and a follow-up test. A good discovery summary can recommend no build when the bottleneck is approval ownership rather than text generation.
'''),
('Baseline measurement and sensitivity analysis', '''
### Specify the measurement contract
Define the unit, start event, stop event, sample selection, and exception policy before timing. For handouts, start when approved notes are available and stop when an instructor accepts a distributable draft. Include source lookup, correction, and rework. Measuring only model response time would omit most of the business workflow. Record individual cases rather than one remembered average.

### Calculate net benefit
Use an illustrative model: net monthly minutes = volume × (manual minutes − assisted preparation − assisted review − exception proportion × exception minutes) − monthly maintenance. The units must agree. If volume is 40, manual work 20, assisted preparation 4, review 10, exception proportion 0.2, exception work 15, and maintenance 30, the result is 40 × (20 − 4 − 10 − 3) − 30 = 90 minutes. It is not the 640 minutes implied by comparing manual work with generation alone.

### Distinguish capacity from cash
Ninety minutes returned to a salaried team is capacity, not automatically money saved. It may support faster response or additional work; it becomes a cash saving only under a separately justified staffing or expense change. Report time and financial assumptions separately. Do not multiply every saved minute by a billable rate and label the result profit.

### Stress the uncertain inputs
Run conservative, expected, and optimistic cases. Change review effort and exception rate first if those were unmeasured. With review at 14 minutes and exceptions at 30%, the same workflow can have negative benefit. That observation is useful: your pilot should measure review and exception cost before you promise scale. Use ranges to choose the next experiment, not to make a weak case look precise.

### Use paired comparisons carefully
Where possible, compare manual and assisted handling on comparable cases, with the same quality rubric. Avoid training the operator on every test case and then claiming general improvement. Keep some unseen cases for the final check. Report sample size, case mix, median time, range, and material failures. A small pilot guides a local decision; it does not establish universal productivity gains.

### Decision exercise
Build a table with ten synthetic cases, observed stages, error types, and acceptance outcomes. Calculate benefit after exceptions and maintenance. Identify the input at which benefit crosses zero. Write a stop rule such as “If more than two of ten drafts require reconstruction, investigate source quality before extending the pilot.” Explain the uncertainty that remains.
'''),
('Service packaging and staged commitments', '''
### Package a decision, not an unlimited capability
A diagnostic, a pilot, and production support answer different questions. A diagnostic identifies the workflow and feasibility. A pilot tests a bounded change with named users and representative inputs. Production requires ownership, access controls, monitoring, support, and recovery. Give each stage its own deliverable and decision gate. A successful diagnostic does not silently authorize production use.

### Build a service boundary
Describe supported input formats, volume, roles, output, review duty, and exclusions. For example, the handout pilot accepts approved UTF-8 course notes in one template, produces draft handouts with source IDs, and requires instructor approval. It excludes scanned documents, new curriculum creation, automated distribution, and confidential learner data. Exclusions are useful when they prevent a buyer from inferring a capability you have not tested.

### Make dependencies visible
List what the client must provide: representative samples, a reviewer, access decisions, a test environment, and an acceptance owner. Attach a date and consequence to each dependency. If approved samples arrive late, the evaluation schedule changes. Avoid a fixed delivery date that assumes inputs you do not control. A dependency table makes negotiation about the actual work possible.

### Offer useful alternatives
If the source material is inconsistent, offer a data-readiness diagnostic before implementation. If the buyer cannot assign a reviewer, offer a read-only search tool rather than a drafting workflow that needs review. Alternatives should preserve the desired outcome while changing the operational burden. They should not be arbitrary tiers that differ only in the number of prompts.

### Test the offer with teach-back
Give the one-page service description to a reviewer and ask: What will you receive? What can it do with incomplete notes? Who approves a draft? What costs recur? What happens when it fails? Any mismatch between their answers and your intent is a specification defect. Revise the offer before treating agreement as informed.

### Packaging exercise
Write diagnostic, pilot, and expansion cards. Each needs a decision question, inputs, outputs, exclusions, client duties, acceptance evidence, and stop condition. Use fictional costs if practicing. No card should guarantee an income, accuracy rate, or saving that has not been measured.
'''),
('Statements of work as executable acceptance', '''
### Translate outcomes into observable behavior
A scope document should connect every deliverable to an acceptance scenario. “Accurate AI summaries” is not testable. “For each approved note, the draft links every factual objective to a source section; missing objectives are flagged for review” identifies behavior a reviewer can inspect. Add negative cases as well as the normal path. Treat this as a delivery planning exercise; real contractual language requires context-specific review.

### Use given, when, then, evidence
Write: Given a named dataset and role, when an action occurs, then an observable result follows, proven by an artifact. Example: Given note N03 with no objective, when a reviewer creates a draft, then the objective is marked missing and export is blocked until reviewed; evidence is the saved draft revision and review event. Include environment and dataset revisions so the test can be repeated.

### Define status categories
Use passed, failed, not tested, and deferred. A deferred condition needs an owner, reason, risk, and explicit acceptance decision. “We did not see a problem” is not equivalent to passed. A demo using one known good document cannot establish behavior on missing fields or failed provider calls. Keep screenshots as supporting evidence rather than the entire test record.

### Define the change boundary
A request to support scanned PDFs changes ingestion, OCR quality, evaluation data, latency, and probably hosting. It is a scope change even when the interface still shows an upload box. The change process should identify affected requirements, effort, acceptance tests, and decision owner. Preserve the original agreement until the change is explicitly accepted.

### Include operational acceptance
Add client-owned accounts, backup/restore, reviewer permissions, and fallback operation where appropriate. A feature can pass its happy path while remaining impossible for the client to operate. Tie handover and access removal to acceptance, not to an informal promise after the project ends.

### Acceptance exercise
Create eight scenarios: normal note, missing objective, contradictory source, malformed input, duplicate submission, unauthorized reviewer, provider failure, and stale edit. Assign each to an owner and an evidence file. Have a peer challenge one ambiguous condition and rewrite it until both of you would give the same result on the same input.
'''),
('Effort estimation, unit economics, and support capacity', '''
### Estimate by work package
Break the work into discovery, data preparation, implementation, evaluation, deployment, review, training, and handover. Give each a low, expected, and high effort estimate with the source of uncertainty. “Build app: 40 hours” hides which assumption can change the schedule. A dependency on an unknown document format should appear as a risk or investigation task, not an invisible buffer.

### Separate cost, price, and value
Cost is what delivery consumes. Price is the commercial amount agreed. Value is the outcome the buyer cares about. These quantities are related but not interchangeable. For an illustrative 44-hour pilot at 50 fictional units per hour, direct labor cost is 2,200 units; a 20% effort allowance gives 52.8 hours, or 2,640 units. Hosting, provider usage, and support are separate. These are teaching assumptions, not recommended market rates.

### Model recurring usage from accepted work
Count requests, calls per request, retries, input/output tokens, and failed jobs. Divide total cost by accepted outputs rather than only successful API calls. If 100 attempts produce 70 accepted handouts, your unit denominator is 70. Include a review cost and maintenance reserve. A model that is cheap per call can be expensive per accepted result if it generates more corrections.

### Price a boundary you can explain
Fixed-scope pricing needs clear acceptance and change rules. Time-based work needs reporting and a budget control. Ongoing support needs a coverage window, supported versions, and severity definitions. Do not make a fixed promise against an unbounded input set. Choose a model for the simulated engagement and explain which risks each party retains.

### Check your own capacity
Suppose three supported clients each generate four incidents per month, with 45 minutes of investigation and 30 minutes of follow-up per incident. That is 15 support hours before planned maintenance. Add sales and administration when evaluating how much delivery work you can take on. Revenue alone does not establish a sustainable service.

### Estimation exercise
Produce one-time and recurring sheets, three usage scenarios, a change example, and a support-capacity calculation. Label every input as observed, quoted, or assumed. Change volume and acceptance rate together, then explain which assumption deserves validation before making a commercial commitment.
'''),
('Data inventory and least-privilege delivery', '''
### Map data by movement
Inventory the fields needed for each step, where they originate, which component reads them, whether a provider receives them, where outputs are stored, and when they are removed. Include logs, caches, backups, and exports. “We delete the uploaded file” is incomplete if its content remains in traces or generated drafts. Begin with synthetic notes so you can test the data flow without real client information.

### Separate account ownership from implementer access
The client should be able to operate the service after your access is removed. Use client-owned service accounts and narrowly scoped implementer roles for the exercise. Record who can rotate keys, change billing, approve users, and recover backups. Do not put actual keys in a handover document or a screenshot. Document variable names and storage locations instead.

### Apply least privilege to behavior
A drafting service needs read access to approved notes and write access to draft storage. It does not need permission to send email or change the source curriculum. Separate reviewer approval from generation. Log who approved which revision and invalidate approval when the material changes. A model’s instruction cannot substitute for an application permission check.

### Build retention into the design
For each data class, specify purpose, access, retention trigger, and deletion method. Test deletion in primary storage and explain how backup retention affects complete removal. If jurisdiction-specific obligations matter, investigate them before a real engagement; this lesson provides a technical inventory, not a universal legal rule.

### Trace one record
Follow synthetic note N03 through ingestion, draft generation, review, export, logging, and backup. At each boundary, list the minimum fields. Replace full source text in operational logs with IDs and status where possible. Confirm that error messages do not echo credentials or confidential payloads.

### Access exercise
Create an operator, reviewer, administrator, and implementer role. Write an allow/deny matrix and test one allowed and one denied action per role. Remove implementer access and verify routine operation still works. The evidence should describe the actual denial or success, not merely a checkbox saying security was considered.
'''),
('Prototype, pilot, and production evidence', '''
### Match the build to the question
A prototype can test whether users understand a review screen using fake data. A pilot tests a bounded workflow with representative inputs and real operating constraints. Production serves ongoing work with assigned ownership and recovery. Label the stage clearly. A polished interface does not turn a prototype into production, and a local demo does not establish reliable multi-user operation.

### Build one vertical slice
For the handout service, implement source input → draft creation → instructor review → saved approved revision → export. A collection of disconnected screens cannot test the end-to-end handoff. Keep the slice small: one input template, one reviewer role, one output format. Preserve the manual fallback so the team can finish work if the pilot stops.

### Show uncertainty in the interface
Missing source information should appear as unresolved, not a confident completion. Display draft status, source revision, review state, and provider failure separately. A disabled export with a clear reason is more useful than silently producing an incomplete file. The interface should help a reviewer understand what requires judgment.

### Define what each evidence type proves
A screenshot proves appearance at a moment. An API response proves one request returned a value. A reload check can show persistence. A second-user denial shows one access boundary. A restore rehearsal demonstrates a recovery procedure in the tested environment. Combine evidence to support the claim you actually make; do not use a screenshot to claim database isolation.

### Add a stop rule
Choose a condition that pauses expansion: missing source ownership, unacceptable false acceptance, review time above the baseline, or no one available to operate the service. Agree on the rule before looking at favorable outputs. A failed pilot can still be a useful engagement when it prevents an expensive unsupported rollout.

### Pilot exercise
Write the decision question, smallest complete flow, representative cases, success measure, guardrail, fallback, and expansion gate. Implement the slice with synthetic data. Ask a reviewer to handle one unseen normal case and one failure without coaching. Record where the design failed to communicate its limits.
'''),
('Feedback triage and bounded iteration', '''
### Treat feedback as evidence about a layer
Separate a source defect, model error, interface confusion, missing capability, and changed business objective. Each has a different owner and remedy. “The draft is wrong” might come from contradictory approved notes; a prompt tweak could hide the problem. Ask for the input, observed output, expected behavior, and consequence before choosing a fix.

### Use a triage record
Store ID, case revision, reporter role, observation, expected behavior, severity, owning layer, proposed action, and closure evidence. Link the record to an acceptance scenario if one exists. If the requested behavior falls outside the agreed scope, record it as a change candidate rather than silently absorbing it into defect work.

### Prioritize using consequence and reproducibility
A reproducible source-citation failure can block the pilot even if it appears rarely. A cosmetic request may be frequent but have little effect on acceptance. Use severity, exposure, and reversibility, and keep uncertainty visible. Avoid multiplying arbitrary scores into a false impression of precision.

### Close the learning loop
For each accepted fix, add a regression case, update the owning rule or component, and define when to recheck it. A fix is not closed merely because the developer changed something. The original reporter or an authorized reviewer should be able to repeat the case and observe the intended behavior.

### Retire stale controls
If a workaround no longer applies after a source or product change, give someone responsibility for removing it. Accumulated prompt instructions can conflict and become impossible to audit. Keep a reason and review date for temporary controls. Prefer a small testable rule over an ever-growing prompt warning.

### Feedback exercise
Create five feedback records covering source error, unclear review label, unsupported scan, duplicate job, and a new email feature. Classify defect versus change, assign an owner, and write the evidence needed for closure. Implement one simulated correction and rerun its failing case plus the existing representative set.
'''),
('Client-readable evaluation and decision reports', '''
### Start with the decision
A useful report tells the buyer what was tested, what happened, and what decision the evidence supports. Put the scope and recommendation before tool names. A result such as “18 of 20 drafts preserved every required objective on dataset v2” is interpretable. “The AI scored 90%” lacks a denominator, a rubric, and consequences.

### Separate quality dimensions
For handouts, measure objective coverage, unsupported claims, source traceability, false acceptance, reviewer effort, and turnaround. A fluent output may still invent a requirement. An answer can cite an existing source ID while misrepresenting its text. Keep mechanical reference validation separate from factual entailment review.

### Classify results honestly
Report passed, failed, deferred, and not tested. Include raw counts and the most consequential failure. A small synthetic sample does not demonstrate performance on real client data, unseen languages, or scans. State those limits near the result, not only in an appendix. Label all fictional or role-play results as simulated.

### Explain the trade-off
Suppose version A accepts 9 of 10 drafts and includes one unsupported objective; version B accepts 7 and sends 3 to review with no unsupported accepted draft in the sample. The buyer must weigh review capacity against the cost of a wrong accepted output. Present both measures and recommend the next test, rather than declaring the version with a larger acceptance percentage the winner.

### Make the report reproducible
Include dataset revision, input selection rule, rubric, configuration revision, environment, and observed outputs. Preserve a small audit trail from claim to case record. Do not paste secret-bearing logs. A future maintainer should be able to rerun the evaluation and explain a changed score.

### Reporting exercise
Write a one-page decision memo and an evidence appendix. Include one accepted case, one rejection, one ambiguous case, a before/after comparison, and a recommendation with a condition that would reverse it. Ask a peer to identify what you did not test; revise any claim that overstates the evidence.
'''),
('Milestones, dependency risk, and delivery forecasting', '''
### Make milestones observable
A milestone is a decision supported by an artifact: source readiness approved, vertical slice observed, evaluation reviewed, or handover rehearsed. “Backend complete” is difficult for a buyer to interpret. Connect each milestone to inputs, owner, acceptance evidence, and the next decision it unlocks.

### Plan around dependencies
Create a dependency graph for representative data, reviewer availability, access approval, implementation, evaluation, and acceptance. Work that depends on unknown source formats should not start with a promise of final quality. Schedule a short feasibility task first. Parallelize only work that can genuinely proceed without those answers.

### Maintain a risk register
For each risk record cause, possible event, consequence, likelihood evidence, mitigation, owner, trigger, and contingency. “AI may fail” is too vague. “Scanned notes may lose objective numbering; run a five-scan feasibility test before offering OCR support” gives you an action and a decision date. Track assumptions separately from problems already observed.

### Use ranges and update them
An estimate is a forecast based on current knowledge. Keep original and revised assumptions visible. When access is delayed, explain which milestone moves and what can still proceed. Do not silently reduce evaluation time to preserve a calendar date; that transfers risk into the deliverable without an explicit decision.

### Report progress through evidence
A useful status note contains completed evidence, current uncertainty, next decision, and help needed from the client. It should not be a list of hours spent. If the prototype works only on known good cases, say so. A blocker with a proposed smaller alternative is more actionable than a generic red status.

### Planning exercise
Build four milestones with owners and evidence, a dependency map, and five risks. Simulate a two-day delay in approved data and a reviewer absence. Reforecast the plan, identify a safe parallel task, and write a concise update that explains the impact without promising untested work.
'''),
('Change control and commercial conversations', '''
### Identify a change by behavior
A request is a change when it alters supported inputs, roles, effects, scale, quality criteria, operating duties, or agreed outputs. “Just send the handout automatically” introduces recipient selection, authorization, duplicate-send prevention, audit history, and recovery. Its size cannot be judged by the number of interface fields.

### Write an impact assessment
Record requested outcome, current boundary, proposed behavior, affected data, permissions, tests, dependencies, effort range, operating cost, and schedule impact. Offer at least one smaller alternative. For automated distribution, an export-ready draft with explicit manual send may meet the immediate need while avoiding a new external-action surface.

### Separate defect from changed expectation
If the app fails an agreed supported case, investigate a defect. If the buyer introduces a new format that was excluded, assess a change. If the original document was ambiguous, acknowledge and resolve the ambiguity rather than using scope as an excuse. Preserve the evidence and update the shared specification once a decision is made.

### Make the decision traceable
Use approved, rejected, deferred, or needs investigation. Record the authorized decision maker and the revision of scope, estimate, and acceptance affected by an approved change. Do not implement new consequential actions on informal enthusiasm alone. In this course, prepare local simulated decisions; no message or contract is sent.

### Protect the relationship through clarity
Explain the goal you share, the new work it entails, the alternatives, and the decision needed. Avoid defensive phrases or unexplained surcharges. The aim is for both sides to understand cost, time, and risk before work starts. A precise smaller option is often more useful than a binary yes or no.

### Change exercise
Assess a new input format, a reviewer-role change, and automatic email. For each identify five affected tests or operating duties, provide an estimate range, and propose an alternative. Update your simulated delivery plan for one accepted change and rerun its acceptance scenarios.
'''),
('Operational ownership, rollout, and recovery', '''
### Transfer capability, not just files
Handover succeeds when the client can run, administer, pay for, and recover the service without your private accounts. Create an ownership matrix for hosting, domain, provider account, database, backups, user administration, and incident decisions. Include a named fallback owner where possible.

### Rehearse the deployment path
Record configuration names, supported runtime, migration command, health check, and a simple smoke case. Keep secret values in the agreed secret store. Deploy into an isolated environment first and record the version actually running. “Works on my laptop” does not prove the client environment has its dependencies or network access.

### Roll out in stages
Use a limited group or shadow output before wider use. Choose promotion and rollback criteria in advance: quality, review burden, latency, error rate, and cost. Shadow generation must not create external effects. A rollback needs a known previous version and compatible data, not merely an old container image.

### Restore data as a test
A backup file is not evidence of recoverability. Restore into a separate database, verify a known record and access boundaries, and record time and errors. Understand which data would be lost between backups and how long restoration takes. Those observations inform recovery objectives; they do not guarantee every future incident will match the rehearsal.

### Remove implementer access
Use a simulated implementer role and revoke it after handover. Verify the client administrator and routine operator still work. Rotate shared development credentials where necessary. Check deployment automation does not depend on your personal token.

### Handover exercise
Create the ownership matrix, deploy the pilot locally, save a record, restart, restore into isolation, and remove implementer access. Have a peer follow the runbook without coaching. Record any undocumented assumption and repair the instructions before acceptance.
'''),
('Training design and user acceptance rehearsal', '''
### Teach decisions before clicks
Users need to know what is a draft, how to inspect source evidence, what makes an output unacceptable, and when to escalate. A click tour on a perfect example does not teach those decisions. Design training around a normal case, an incomplete source, a contradiction, an unavailable provider, and a stale edit.

### Define role-specific tasks
An operator creates a draft; a reviewer accepts or rejects a revision; an administrator manages access. Teach each role its own responsibility and boundary. Do not imply that a green generation status means approval. Give the reviewer a short rubric and show how corrections affect the saved artifact.

### Observe teach-back
Ask the trainee to complete an unseen case and explain why they accepted or rejected it. Avoid taking over the mouse or supplying the answer at every hesitation. Record confusion, source lookups, mistakes, and time. Those observations evaluate both the guide and the interface.

### Run acceptance separately from training
Acceptance belongs to the authorized owner using agreed scenarios and evidence. Attending training is not acceptance. Keep passed, failed, deferred, and not tested distinct. A failed recovery scenario cannot be hidden behind a successful generation demo. Update the acceptance record when a defect is repaired and retested.

### Build a usable quick-start guide
Include purpose, supported inputs, normal steps, review rubric, common failure symptoms, fallback procedure, and escalation owner. Use synthetic examples. Include version and review date so a changed interface does not leave users following stale instructions.

### Training exercise
Write a five-case rehearsal. Have another person or a clearly labeled role-play operator use your guide. Capture the observed result and one improvement per failure. End with an acceptance record that identifies unresolved conditions and who can decide whether they block handover.
'''),
('Support design and incident learning', '''
### Specify the supported service
Name the environment, versions, features, reporting route, coverage window, and excluded changes. Distinguish response target from resolution guarantee. An incident caused by a third-party outage may be outside your repair control while still requiring diagnosis and a fallback. Use illustrative assumptions in this course rather than making real service commitments.

### Classify incidents by consequence
Define examples: unavailable drafting, unauthorized access, unsupported accepted content, slow response, and cosmetic defects. A low error count does not make an authorization failure low severity. Record affected users, exposure period, workaround, and the decision owner. Avoid including private content in broadly shared incident notes.

### Contain, recover, then investigate
Pause external effects or promotion when needed. Preserve enough evidence to understand the incident without copying secrets. Restore a safe operating path, including manual operation if appropriate. After recovery, reconstruct the timeline, contributing conditions, detection gap, and corrective actions.

### Treat model and source changes as releases
A prompt, model, retrieval setting, or policy revision can change behavior without a frontend code change. Keep their revisions and rerun representative evaluations before promotion. Maintain a rollback or source-deactivation path. A restart does not fix a stale policy index.

### Close actions with evidence
Assign each corrective action an owner, due condition, and verification case. “Be more careful” is not a control. “The index activation step rejects a source revision without a completed evaluation record” is testable. Review whether temporary controls should be retired after the underlying fix.

### Incident exercise
Simulate a source-policy update that makes an accepted handout stale. Identify affected outputs, disable the stale revision, prepare a local reviewer note, restore the correct source, and add a regression case. Write a short incident review with facts separated from hypotheses.
'''),
('Portfolio claims and evidence-backed case studies', '''
### Make one claim per evidence trail
A case study should connect context, constraint, decision, implementation, measured result, and limitation. For each result, identify the dataset, baseline, metric, sample size, and artifact. “Built an AI assistant” is a capability description. “Saved drafts persisted after restart on the local test stack” is a scoped technical observation.

### Label simulated work accurately
A self-directed project can demonstrate useful engineering. Call the training provider fictional and the engagement simulated. Do not turn role-play feedback into a testimonial or say a paying client used the service. Accuracy about provenance makes the technical evidence easier to trust.

### Show a consequential failure
Include an example that changed your design: a missing objective produced invented text, a stale edit overwrote approval, or an export included an unreviewed draft. Explain how you reproduced the failure, what changed, and which test now catches it. A polished screenshot without this reasoning does not show how you handle delivery risk.

### Separate local results from general claims
A ten-document synthetic evaluation can support a statement about those cases and settings. It cannot establish performance on every client document or predict business savings. Show the remaining uncertainty and the next validation step. Avoid a percentage without a denominator or a comparison without a common rubric.

### Protect others' information
Use synthetic artifacts or explicit permission for names, data, quotes, and logos. Redact credentials, internal URLs, and private records from logs and images. A public repository is not automatically a suitable place for a client's operational details.

### Case-study exercise
Write a one-page narrative and a claim-to-evidence table. Include one architecture sketch, a workflow example, a before/after comparison, an important failure, and an operational limitation. Ask a peer to challenge your strongest claim and narrow it until every word is supported.
'''),
('Qualification and problem-specific outreach preparation', '''
### Research a plausible workflow, then ask
Published information can suggest an operating context; it rarely proves an internal problem. A business running many courses may prepare handouts, but you cannot infer that its current process is broken. Write the public fact, your inference, and the question you would ask in separate fields.

### Qualify fit before proposing delivery
Check problem relevance, owner authority, access feasibility, review capacity, timing, and the ability to measure an outcome. A buyer who wants fully autonomous publication but cannot assign a reviewer may not fit your current service. A respectful decline or a diagnostic is preferable to an unsupported promise.

### Draft a concise introduction
Use a relevant public observation, a specific workflow hypothesis, one accurately labeled piece of evidence, and an invitation to discuss the current process. Do not invent urgency, savings, or a relationship. For the exercise, use fictional organizations and keep messages as local drafts.

### Prepare useful follow-up questions
Ask for a recent example, the current completion rule, what causes rework, who reviews results, and which data can be used in a pilot. Avoid requesting confidential files before access is agreed. If someone declines, record the outcome and do not turn follow-up into pressure.

### Evaluate your own readiness
Before offering a capability, confirm you can demonstrate its normal behavior, a failure, evidence of persistence, the review boundary, and a recovery path. A demo built on hand-picked examples may be suitable for learning but insufficient for a real engagement. Qualify yourself as carefully as the prospect.

### Qualification exercise
Create three fictional prospect records, separate observations from assumptions, draft an introduction, and write five discovery questions. Define three decline conditions. Have a peer role-play an enthusiastic but unsuitable buyer and explain a bounded alternative without promising results you have not observed.
'''),
('Engagement synthesis and repeatable delivery', '''
### Audit consistency across the package
Trace each promise in the service offer through scope, implementation, evaluation, acceptance, and handover. If the offer promises editable drafts, a screenshot of generated text is insufficient; demonstrate editing, saving, and reopening a revision. If a supported format was never tested, either test it or revise the promise before closing the engagement.

### Create a delivery index
List artifact, purpose, revision, owner, acceptance state, and location in the simulated project. Include the discovery dossier, baseline, offer, scope, estimate, data map, pilot, evaluation, change log, runbook, training guide, and acceptance record. A directory full of files is less useful than an index explaining how they support the delivery decision.

### Rehearse three perspectives
As a buyer, ask what outcome was demonstrated and what costs recur. As an operator, complete a normal task and handle a failure. As a maintainer, restore a record, change a configuration, and locate the relevant evaluation. Record where the handover depends on the implementer supplying undocumented knowledge.

### Keep unresolved work explicit
For each limitation, record consequence, owner, next evidence, and whether it blocks acceptance. A backlog entry does not automatically make a material failure acceptable. The authorized reviewer must make that decision. In the course, label that decision as simulated.

### Improve the process from observed friction
Choose one discovery question, one acceptance scenario, one technical control, and one handover instruction to improve based on the engagement. Explain the event that motivated each change. Keep reusable templates small enough to understand, and remove fields that no one used to make a decision.

### Final practicum
Run the complete source-to-approved-export journey on unseen synthetic cases, including one failure and recovery. Audit the evidence and present a defensible recommendation: expand, revise, pause, or stop. The program outcome is the ability to deliver and explain a bounded service responsibly, supported by your actual work.
'''),
]
