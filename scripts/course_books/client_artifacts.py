"""Completed artifacts for one explicitly fictional training-provider engagement.
All numbers are teaching assumptions, not observations of an actual customer.
"""
ARTIFACTS = [
('A workflow selection memo', '''| Candidate | Frequency assumption | Permission/access | Consequence of error | Decision |
|---|---|---|---|---|
| Handout preparation | 40/month, unverified | Approved text notes only | Instructor catches a false teaching claim | Investigate |
| Automatic assessment grading | 200/month, unverified | Learner records not authorized | Incorrect learner outcome | Exclude from first pilot |
| Course announcement drafting | 4/month, unverified | Public fact sheet | Incorrect dates or promises | Possible alternative |

**Selected hypothesis:** the operations lead may value a source-linked handout draft for one course template. The course assistant operates it, the instructor approves teaching facts, and the operations lead owns the pilot decision. Budget authority is unresolved; instructor availability is also unverified.

**Decision:** conduct discovery before offering a saving. The first candidate has enough possible volume to investigate, not enough evidence to sell a fixed outcome. If instructors cannot review outputs, stop or choose a different workflow.''', 'Change handout volume to two per month and review capacity to zero. Re-score all three candidates, explain the trade-off, and identify a different buyer question rather than forcing the original offer.'),
('A discovery evidence ledger', '''| ID | Evidence type | Record | Interpretation | Next action |
|---|---|---|---|---|
| D1 | Role-play statement | “We do handouts daily.” | Volume may be high | Define what counts as one handout |
| D2 | Simulated observed sample | Two handouts in last month’s sample folder | Sample may be incomplete | Ask for the full count, with permission |
| D3 | Role-play walkthrough | 12 min preparing, 8 min reviewing one note | Review is 40% of this example | Time four more examples |
| D4 | Assumption | Faster drafting reduces review | Could be false | Compare correction time in pilot |

**Follow-up:** “Which steps and documents did you include when you said daily? Were those two files representative or just the available sample?” This asks for definitions without accusing the participant of being wrong.

**Finding:** frequency remains unknown. Do not average “daily” and “two” or describe this role-play as a customer interview. A recent example gives a testable workflow, not proof of demand.''', 'Write eight non-leading questions and role-play a recent exception. Produce separate observation, interpretation and assumption columns; include one answer that would make you decline.'),
('An editable benefit model with a stop decision', '''All inputs below are illustrative monthly assumptions.

| Item | Calculation | Minutes |
|---|---|---:|
| Manual workflow | 40 × (12 preparation + 8 review) | 800 |
| Assisted routine work | 40 × (4 preparation + 10 review) | 560 |
| Additional exception work | 40 × 0.20 × 15 | 120 |
| Maintenance | fixed monthly allowance | 30 |
| Net benefit | 800 − 560 − 120 − 30 | **90** |

Exception time here is **incremental** beyond routine review. If your measured exception duration already includes normal review, subtract the overlap rather than count it twice. Ninety minutes is capacity released, not automatically cash saved.

Conservative case: review 14 minutes and exception rate 0.30 gives 800 − 720 − 180 − 30 = **−130 minutes**. Optimistic case: review 8 minutes and exceptions 0.10 gives 800 − 480 − 60 − 30 = **230 minutes**. The range crosses zero; measure review and exceptions before committing. A simulated stop rule is nonpositive net benefit after the agreed observation window.''', 'Rebuild the table in an editable sheet with formulas. Collect five timed synthetic runs, record every review and exception, then replace assumptions with observed inputs while keeping sample size visible.'),
('A bounded pilot offer card', '''**Decision to support:** can instructors prepare source-linked handout drafts for one approved text-note template with manageable review?

**Inputs:** up to 20 synthetic English UTF-8 notes, one template, one instructor reviewer. **Output:** editable draft with source references, missing-objective flags and local reviewed export. **Deliverables:** runnable prototype, case-level evaluation, cost assumptions and handover guide.

**Excluded:** scanned PDF/OCR, new curriculum invention, automatic email, public publication, learner records, multilingual output. **Client duties in the simulation:** supply template and reviewer time; name an acceptance owner. **Fallback:** existing manual preparation remains available.

**Gate:** diagnostic first establishes fields and baseline; pilot tests the agreed cases; expansion is a new decision based on results. The offer does not guarantee time savings, income or autonomous accuracy. A teach-back that interprets “export” as “send to students” means the offer needs revision before agreement.''', 'Create diagnostic and expansion cards with different decision questions. Have a peer teach back the pilot deliverables and exclusions; record and correct any misunderstanding.'),
('An acceptance register linked to scope', '''| ID | Given / when | Then | Evidence | Decision owner |
|---|---|---|---|---|
| A1 | N01-v1 complete; create draft | Required sections and source ID present | saved D01-r1 and review sheet | instructor |
| A2 | N03-v1 missing objective; create draft | Objective stays unknown; review flag visible | D03-r1 plus screenshot | instructor |
| A3 | N04-v1 contradictory sections | Conflict retained; no invented reconciliation | conflict annotation | instructor |
| A4 | Another account requests D01 | Inaccessible; no content disclosed | scoped request/response | operations lead |
| A5 | Fake provider times out | Input retained, failure explicit, no approved export | failure trace and readback | operations lead |

**Milestone condition:** A1–A5 are blocking; a skipped test is not a pass. Add three more cases for malformed input, duplicate submission and stale edit. Pin the fixture and release revisions in the completed record.

If a new scan is supplied at review, the original UTF-8 boundary remains until a change is accepted. This is a project-planning specimen, not a jurisdiction-specific contract.''', 'Complete eight scenarios and assign a reviewer and evidence path to each. Rewrite one ambiguous “good quality” criterion until two peers agree how to judge the same output.'),
('An effort and capacity estimate', '''| Work package | Expected hours | High-case driver |
|---|---:|---|
| Discovery and data | 8 | incomplete template definitions |
| Build | 16 | revision and review conflicts |
| Evaluation | 10 | source contradictions require labels |
| Review | 6 | reviewer feedback turnaround |
| Handover | 4 | fresh setup defects |
| Total | **44** | estimate, not a time log |

A 20% effort allowance gives **52.8 hours**. At **50 fictional units/hour**, planned labor cost is **2,640 units**. This is an illustrative internal cost model, not a market rate or recommended price. Hosting and provider usage are separate; price and the buyer’s value are different quantities.

Recurring example: 100 attempts costing 14 units with 70 accepted drafts gives 0.20 usage units per accepted draft, before review and maintenance. Three clients × four incidents × (45 investigation + 30 follow-up) minutes gives **15 support hours/month**. Do not sell those hours twice as implementation capacity.''', 'Add low/high estimates by package and three usage scenarios. Show which assumption drives the range. Define support coverage and out-of-scope handling separately from a one-time pilot price.'),
('A field-level data-flow register', '''| Data | Destination | Role with access | Retention assumption | Removal test |
|---|---|---|---|---|
| Approved note text | local store | instructor | pilot plus 30 days, to agree | delete then read returns absent |
| Draft + source ID | local store/export | assigned instructor | same draft policy | delete draft and inspect export copy |
| Stage/outcome IDs | logs | operator | seven days, to agree | rotate and inspect sample |
| Backups | isolated client-owned store | administrator | two copies, to agree | expire old copy and verify |
| Learner names | none | none | excluded | synthetic canary rejected at intake |

The offline fake provider receives no real client data. A later hosted model adds a destination and must trigger a new data-flow decision. The retention values are planning assumptions, not default policy or compliance claims.

Deleting an input does not delete an already exported handout or every backup. Record those separate lifecycles and the owner responsible for each. A hidden sheet in a supplied workbook must be inspected before intake, not discovered after upload.''', 'Add an access-provision/revoke checklist and a provider boundary row for a hypothetical integration. Follow a synthetic canary through logs, drafts, exports and backups; report exactly which copies remain.'),
('A pilot demonstration record with honest boundaries', '''| Stage | Implementation | Observed synthetic result | Limitation |
|---|---|---|---|
| Read N01 | real local file | text loaded and source ID recorded | text only |
| Generate outline | fake adapter | required headings returned | no model-quality evidence |
| Check objective | deterministic check + manual fact review | N03 marked missing | semantic adequacy needs instructor |
| Save/reload | real local store | D01-r1 read after restart | hosting recovery not yet tested |
| Export | local file after human review | approved revision exported | no email or public publishing |

**Go/no-go question:** is the review workflow understandable enough to evaluate the agreed scope? A fake generator can test failure recovery and orchestration but cannot establish factual quality of a future model.

**Failure demonstration:** the adapter raises a timeout; the original note is still available and no export is labeled approved. Record whether each result was actually observed in your implementation; this specimen is illustrative.''', 'Build the normal, missing-objective and timeout paths. Keep all three raw observations. Have the reviewer identify every fake/manual component without coaching.'),
('A feedback triage and disposition log', '''| ID | Feedback and revision | Classification | Decision | Verification |
|---|---|---|---|---|
| FB1 | D01-r2 export loses approved objective | Defect against A1 | Fix serialization | exported objective matches saved revision |
| FB2 | D01-r2 “tone too formal” | Preference | Test against instructor audience rubric | paired reviewer task |
| FB3 | “Translate into three languages” | New requirement | Prepare separate change; do not include now | new datasets/tests if accepted |
| FB4 | “Assistants should approve for instructors” | Permission change | Hold pending authority decision | allowed/denied-role cases |

Fixing FB1 restores the current promise; accepting FB3 changes it. FB2 needs a task-based reason rather than implementer taste. FB4 affects authority even if implemented as a dropdown.

For conflicting requests, quote the prior requirement and show alternatives, effort and acceptance impact. Keep a local decision note for this exercise; preparing a recommendation is not authorization to send a proposal.''', 'Classify ten role-play items, reproduce two defects, and write a change request for one expansion. Record a deferred item with owner and a condition for revisiting it.'),
('A client-readable result and recommendation', '''**Candidate:** demo-r3; dataset: synthetic-notes-v2; 20 cases, all retained. This is an illustrative report, not a measured client result.

| Primary outcome | Count | Interpretation |
|---|---:|---|
| Required sections present; no flagged issue in review | 16 | Passed these rubric checks |
| Source clarification required | 3 | Not ready for unattended distribution |
| Unsupported teaching statement | 1 | Blocking factual defect |
| Total | **20** | No cases excluded |

“16/20 complete without a flagged issue” describes this sample. It does not mean 95% accurate, nor does it establish that every sentence is correct. Report factual review and format completeness as separate dimensions when collecting real results. Include individual correction times; a synthetic average is not observed saving.

**Recommendation:** continue only as a reviewed pilot; block unattended release. Inspect the unsupported statement, identify its source/version, fix the cause, rerun affected cases and obtain fresh review before expansion. Three clarification outcomes may be correct system behavior but still consume reviewer capacity.''', 'Replace the specimen with actual per-case results and review minutes from your pilot. Write a scoped recommendation and one condition that would change it; preserve the strongest counterexample.'),
('A milestone and risk decision sheet', '''| Milestone | Artifact and acceptance | Dependency | Owner |
|---|---|---|---|
| M1 | labeled notes-v1 + agreed A1–A8 | template and instructor review | instructor |
| M2 | normal + timeout draft saved/reloaded | M1 fields stable | implementer |
| M3 | case-level evaluation + handover rehearsal | reviewer availability and M2 | operations lead |

| Risk | Trigger | Action | Consequence |
|---|---|---|---|
| Reviewer unavailable | no slot before M3 | request new date or named alternate | acceptance pending, not passed |
| Real notes delayed | agreed intake date missed | continue synthetic implementation | real-data claims deferred |
| Source contradiction | two active objectives disagree | preserve conflict, request owner decision | draft review blocked |

A dependency delay may leave useful implementation work possible without making acceptance possible. Separate elapsed calendar time from effort. A risk owner must have an action they can take; “monitor closely” alone does not change the plan.''', 'Add two risks and simulate the instructor being absent for the last week. Revise milestone dates, labels and remaining claims without silently removing the factual-review gate.'),
('A change request for automatic email', '''**CR-03, proposed only:** send approved handouts to participants. **Reason:** reduce manual distribution work. **Current scope:** local reviewed export; no external sends.

**New requirements:** client-owned sending account, approved recipient source, sender permission, exact content/recipient approval, durable idempotency key, send-outcome ledger, retry/reconciliation behavior, opt-in test environment and incident owner. A lost send response is uncertain; repeating with a new key can duplicate delivery.

**Acceptance additions:** stale approval blocked; unauthorized sender denied; duplicate submission produces one fake effect; timeout after fake acceptance reconciled; wrong recipient never silently repaired. **Data-flow impact:** recipient addresses and provider logs become new data destinations.

**Alternatives:** retain reviewed local export; or create a local dispatch manifest for a human sender. **Estimate:** investigate provider and test environment before quoting effort. **Decision:** defer CR-03 in the simulated pilot and finish A1–A8. No email is sent by this exercise.''', 'Prepare one cosmetic and one permission change in the same format. For an accepted hypothetical change, update milestones, estimate, data register and tests; demonstrate all four affected artifacts agree.'),
('An ownership and recovery handover matrix', '''| Asset | Accountable owner | Implementer access | Handover observation |
|---|---|---|---|
| Hosting/service | client administrator | temporary limited role | client restarts service after revoke |
| Database and backups | client administrator | scoped deployment role | isolated restore content checked |
| Content review | instructor | no approval authority by default | instructor reviews fresh draft |
| Provider account, if added | client billing owner | restricted runtime credential | revoke implementer without stopping service |
| Recurring charges | operations lead | read-only cost visibility if agreed | cost owner identified |

The runbook lists configuration **names**, never secret values. State how the administrator finds the agreed secret store and rotates access. Record exact release and backup IDs, observed restore content and limitations. A checked box without an observation is not a handover test.

For the local simulation, use distinct roles and synthetic records. Revoking an implementer role must not remove the application’s separate service identity or the client administrator’s recovery access.''', 'Perform local restart/readback and an isolated restore. Give a peer the runbook, remove your simulated operator role and record what they can still operate without your credentials.'),
('An acceptance and training observation log', '''| Scenario | Trainee observation | Status | Follow-up |
|---|---|---|---|
| Complete note | draft reviewed and exported | passed in role-play | save output revision |
| Missing objective | trainee assumed “draft complete” meant approved | failed | change state label and teach review duty |
| Contradictory source | no authorized instructor available | not tested | schedule named reviewer |
| Optional PDF scan | outside text scope | deferred by scope decision | separate expansion, not a pass |

**Guide revision:** replace “draft complete” with “Draft needs instructor review”; show the source excerpt and block approved export until the exact revision is confirmed. Repeat with a new missing-objective note, then ask the trainee to explain why it cannot be distributed yet.

Attendance at a demo proves attendance. Passing acceptance requires the authorized reviewer to observe the named behavior. Keep the failed first attempt: it explains why the correction was necessary. This specimen’s role-play statuses must be replaced by your actual observations.''', 'Prepare five fresh tasks including two failures. Observe a peer without intervening; record assistance separately. Revise one instruction and rerun with a new input rather than coaching the original case to success.'),
('An incident tabletop with concrete corrective checks', '''**Scenario:** yesterday’s handout cites returns-v1 after returns-v2 became active. **Impact in simulation:** three drafts may contain stale teaching conditions; no automatic distribution exists.

**Timeline:** 09:00 instructor detects mismatch; 09:05 operator pauses affected exports; 09:15 source owner confirms effective revision; 09:30 affected drafts identified by source ID; 10:00 corrected drafts await review. These times are fictional tabletop events, not an actual incident.

**Contributing conditions:** active pointer changed without evaluation; drafts did not show source age. **Recovery:** preserve original drafts, record supersession, regenerate against confirmed v2 and obtain new review. Restarting the API alone does not change source selection.

**Corrective checks:** current query uses v2; historical-date query still retrieves v1 when appropriate; edited draft invalidates approval; source revision is visible in the review screen. Assign one owner and due date to each. A support response target is time to acknowledge/triage, not a guarantee of resolution.''', 'Write coverage, severity and escalation assumptions for a small service. Run a provider-format-change tabletop and record retained data, manual fallback, recovery checks and one prevention test.'),
('A case-study claim audit', '''| Draft claim | Supporting evidence required | Defensible wording |
|---|---|---|
| “Saved a client hours” | actual client baseline and comparable timed work | “Simulated engagement; ten synthetic notes” until measured |
| “Review fell from 8 to 6 minutes” | same task definition, case-level times and sample | “In a ten-note synthetic comparison, mean review was 8 versus 6 minutes” if actually observed |
| “Secure app” | much broader evidence than this pilot | “Cross-account read denied in the recorded ownership cases” |
| “Production-ready” | operations, load, recovery and organizational acceptance | “Offline reviewed prototype with stated limits” |

If the two-minute difference is observed over ten notes, that is 20 minutes on that sample, not proof of future monthly savings. Include differences in errors or reviewer workload. Describe one failed attempt, its cause and the test that motivated the correction.

No customer quote, logo or simulated buyer is presented as a real endorsement. Specific evidence preserves the value of a self-directed project without inventing a commercial history.''', 'Audit five statements in your own case study. Link each to a real evidence file or narrow/remove it. Include a failure and clearly label every simulated result.'),
('A local outreach draft and qualification decision', '''**Fictional prospect fact:** the training provider’s public-style profile lists four live cohorts. **Hypothesis:** instructors may spend time preparing handouts; this has not been observed.

**Unsent draft:** “Your course profile lists several live cohorts. I built a synthetic handout-review prototype that may be relevant to preparation work. If this is a current priority, would a short discussion of your existing process be useful? The example is a reviewed draft workflow, not automatic teaching or distribution.”

**Qualification agenda:** who owns the workflow and budget; recent concrete example; volume and correction work; authority to use samples; reviewer availability; timing; acceptable fallback. Ask for access only after its scope is agreed.

**Decline/rescope conditions:** no reviewer for factual teaching, no permission to use the input, or demand for guaranteed unsupported outcomes. A polite response or interest in AI is not a qualified buying decision. This exercise prepares local drafts only and sends nothing.''', 'Create three fictional profiles with facts and hypotheses separate. Prepare one introduction and one disconfirming question for each. Role-play a request for confidential autonomous processing and record your scope response.'),
('A cross-document consistency and handover audit', '''| Promise | Implementation evidence | Acceptance record | Handover | Disposition |
|---|---|---|---|---|
| English text notes | fixture notes-v2 and supported parser | A1/A2 | input-format section | retain within tested scope |
| Missing objectives flagged | N03 saved draft + source review | A2 | failure guide | retain after observed rerun |
| Automatic email | no implementation or authorization | none | none | remove from offer; CR-03 deferred |
| Recoverable drafts | restart and isolated restore log | operational gate | runbook | pending until actual test |

An index entry proves a file is named, not that its promise was fulfilled. Open each artifact, compare its revision, and ask the reviewer to operate a fresh normal case and a failure. If the offer says PDF but only text was tested, implement and evaluate PDF or narrow the offer; changing only a result label is insufficient.

**Final package:** discovery, bounded offer, A1–A8, editable estimate, prototype, case-level evaluation, acceptance statuses, data register, ownership/runbook, limitations and retrospective. Pending items stay visible and have owners.''', 'Run the complete simulated handover with a fresh reviewer. Audit every offer promise against evidence and disposition; fix one mismatch and rerun its acceptance scenario before calling the package complete.'),
]
