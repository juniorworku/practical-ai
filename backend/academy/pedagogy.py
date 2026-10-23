"""Academy-wide engineering teaching contracts. No network or model calls."""
PRINCIPLES = {
 'version':'engineering-principles-v2',
 'software_first':'Build interfaces, asynchronous services, API adapters and recoverable data flows before studying algorithm derivations. Use mathematics to explain a measured engineering decision.',
 'production_over_playground':'A notebook or chat demo is an early prototype. Graduation builds toward operational evidence: deployment/readiness, bounded work, rate limits, error recovery and persisted state. Early checkpoints assess only boundaries already taught; future deployment controls are planned rather than claimed complete. The 10% framing is a teaching heuristic, not a measured universal percentage.',
 'pillars':['Latency vs. Cost vs. Quality','Deterministic Evaluation','Context Management'],
 'evaluation_note':'Automate repeatable checks with fixed inputs and versioned expectations. Model judges, faithfulness scores and semantic reviews can be stochastic; record judge/configuration versions and disagreement rather than calling them deterministic truth.',
}
# scenario, performance decision, automated evidence, context policy, production failure
CONTRACTS = {
 'foundation':('A read-only assistant over three synthetic policies', 'Compare a fixed workflow and a bounded agent on identical labeled cases. Count failed attempts and review time in cost per accepted result; retain p50/p95 and a quality floor.', 'Version a case set containing supported, ambiguous, missing-source and unauthorized inputs. Schema, permissions and stop conditions are executable assertions; label semantic support separately.', 'Record instruction, tool-schema, history, evidence and output allocations. Preserve source IDs and exceptions; label estimates separately from provider usage.', 'Reject oversized input, preserve it on provider failure, and cap attempts, elapsed time and concurrent work.'),
 'adapter':('A provider adapter shared by simultaneous learners', 'Measure time to first output and total completion separately. Compare retry cost and accepted-output rate under a fixed overall deadline.', 'Fake 429, 503, permission failure, malformed JSON, cancellation and a partial stream. Assert bounded retry and no false saved/success status.', 'Track actual input/output usage when supplied; include retry usage. Key caches by owner, model, prompt and source revisions; never cache partial streams as complete answers.', 'Honor Retry-After within the total budget, stop sibling tasks on disconnect, and separate safe draft retries from uncertain external writes.'),
 'retrieval':('A tenant-scoped source-grounded knowledge base', 'Compare lexical, dense, hybrid and reranked retrieval on the same labeled queries. Report retrieval latency, reranking spend and answer quality separately.', 'Assert document scope and revision before retrieval. Measure recall@k/MRR on versioned relevance labels, including no-answer and conflicting-source cases.', 'Use token-aware chunks retaining page/time provenance and exceptions. Version embedding dimensions/indexes and invalidate retrieval/answer caches on source or permission changes.', 'Quarantine failed parsing, bound upload size and worker queues, activate revisions only after indexing checks, and preserve a working previous revision.'),
 'actions':('A workspace agent that proposes drafts and calendar changes', 'Compare a fixed plan, bounded graph and delegated tasks. Include all tool/model calls, handoff delays and human review in the useful-output denominator.', 'Replay duplicate events, stale approvals, denied scopes, graph resumes and lost responses. Assert one authorized state transition; separately reconcile remote effects.', 'Persist bounded state outside the prompt. Select tenant-scoped memory, budget tool results and invalidate approval/cache when effect fields or source revisions change.', 'Verify connector scopes and actor identity outside model output, bind approval to the exact payload and destination, and handle timeout outcomes as uncertain.'),
 'evaluation':('A release candidate tested against normal and edge-case inputs', 'Report latency distributions, total spend, acceptance and critical failures by category. A cheap/fast candidate cannot trade away a mandatory safety or factual-support gate.', 'Freeze dataset, prompt, model, parser and judge versions. Fail CI on schema/permission regressions; run model-based quality judgments with recorded rubrics and reviewed disagreements.', 'Compare context sizes and cache policies using the same dataset. Log counts, hit/miss and revision IDs without copying private prompts into traces.', 'Trace retries, timeouts and queue wait as separate spans. Redact logs, retain unavailable runs in denominators and rehearse promotion/rollback.'),
 'deployment':('A multi-user AI service deployed from containers', 'Load-test offered vs. completed work, p95 and cost per accepted result at stated concurrency. Autoscaling settings are hypotheses until observed against downstream/GPU limits.', 'Test readiness against the actual database, restart/readback, isolated restore, denied owner access, overload rejection and a dependency outage on the deployed revision.', 'Budget resident model memory/KV cache and per-request context separately. Keep tenant/revision-aware application caches; never assume a process-local cache is shared across replicas.', 'Separate request concurrency, worker capacity and model/GPU capacity. Add admission control, shared quotas, bounded queues, maximum instances and a documented fallback/stop budget.'),
 'business':('A fictional training provider buying a reviewed handout workflow', 'Present generation latency, reviewer time, recurring usage and accepted-output quality together. Count preparation, exceptions and maintenance; distinguish assumptions from observations.', 'Translate each promise into Given/When/Then with dataset/release IDs and case-level evidence. Automate mechanical checks; keep authorized factual review and acceptance decisions explicit.', 'Inventory approved notes, sensitive fields, source revisions, token allowances and cache retention. Price source cleanup and cache invalidation rather than assuming unlimited context or free reuse.', 'Assign rate/budget caps, failure/manual fallback, hosting ownership, review duties, restore evidence and escalation before expanding the service.'),
 'terminal':('A reproducible workspace operated without private developer state', 'Compare manual setup and scripted checks by elapsed time, failures and maintenance effort; do not confuse a shorter command with a more reliable setup.', 'Use a fresh directory/environment and assert paths, exit status, expected files and denied unsafe operations. Keep command transcripts with synthetic fixtures.', 'Select only relevant files for an assistant context, exclude secrets/large binaries, record a byte/token estimate and invalidate cached guidance after file changes.', 'Check exit codes, fail on missing configuration, keep secrets out of shell history/logs, and distinguish the academy simulation from a real terminal.'),
}

def family(slug,module):
    text=(slug+' '+module).lower()
    if slug=='python-for-ai':
        return {'01':'adapter','02':'adapter','03':'adapter','04':'retrieval','05':'evaluation','06':'deployment'}.get(module[:2],'foundation')
    if 'freelancing' in slug:return 'business'
    if 'terminal' in slug:return 'terminal'
    if slug=='genai-accelerator' and module.startswith('Lab '):
        try:number=int(module.split()[-1])
        except ValueError:return 'foundation'
        if number==2:return 'adapter'
        if number in {4,7,8,9}:return 'retrieval'
        if number in {10,11,12}:return 'evaluation'
        if number in {5,6,13,14}:return 'deployment'
        if number>=15:return 'actions'
        return 'foundation'
    if 'ai-workshops'==slug:
        if 'studio 03' in text:return 'retrieval'
        if 'studio 01' in text:return 'adapter'
        if 'studio 02' in text:return 'actions'
        if any(x in text for x in ['studio 04','studio 05']):return 'actions'
        return 'deployment'
    if any(x in text for x in ['retrieval','rag','grounding','ingestion','vector','chunk']):return 'retrieval'
    if any(x in text for x in ['llmops','monitor','evaluation','observability','quality','06 ·','09 ·']):return 'evaluation'
    if any(x in text for x in ['deploy','container','scaling','hosting','infrastructure','07 ·','08 ·','capstone','production']):return 'deployment'
    if any(x in text for x in ['agentic','agent loops','tools','protocol','mcp','graph','multi-agent','04 ·','05 ·','approval']):return 'actions'
    if any(x in text for x in ['api','modern ai stack','stream','02 ·','context','sdk']):return 'adapter'
    if '03 ·' in text:return 'retrieval'
    return 'foundation'

def module_contract(slug,module):
    kind=family(slug,module)
    scenario,performance,evaluation,context,operations=CONTRACTS[kind]
    # Workshop studios retain their own use cases rather than becoming agent/RAG lessons.
    if slug=='ai-workshops':
        scenarios={'01':'purchase-request extraction','02':'meeting commitments and corrections','03':'a claim-and-citation research notebook','04':'support topic/urgency routing','05':'factual content review and local publication','06':'one integrated studio app'}
        match=next((v for k,v in scenarios.items() if 'Studio '+k in module),None)
        if match:scenario=match
    focus=MODULE_FOCUS.get(slug,{}).get(module)
    if focus:
        scenario,performance,evaluation,context=focus[:4]
        if len(focus)>4: operations=focus[4]
    return {'version':PRINCIPLES['version'],'module':module,'family':kind,'scenario':scenario,
            'software_first':PRINCIPLES['software_first'],'production_over_playground':PRINCIPLES['production_over_playground'],
            'pillars':[{'name':name,'application':value} for name,value in zip(PRINCIPLES['pillars'],[performance,evaluation,context])],
            'operations':operations,'evaluation_note':PRINCIPLES['evaluation_note'],
            'deliverable':'module-engineering-evidence.json: dataset/release IDs; latency/cost/quality comparison; automated checks and critical failures; context and cache policy; deployment/failure observations. Mark unmeasured fields as not tested.',
            'release_gates':['Record latency, cost and quality for the boundary taught so far; mark unmeasured provider or deployment values unknown.', 'Retain the taught positive and negative checks with unchanged expectations; keep semantic review separate.', 'Explain the current source/context allowance and owner boundary; later cache or distributed controls are not assumed implemented.', 'Exercise the failure path taught in this stage. Future hosting, overload and distributed recovery experiments become mandatory only in their own deployment stage.']}

ENGINEERING_PROGRAMS = frozenset({'ai-agent-bootcamp','ai-workshops','ai-engineering-12-week','genai-accelerator','python-for-ai'})

def displayed_contract(slug, module):
    """The engineering brief belongs to engineering paths, not every catalog record."""
    return module_contract(slug,module) if slug in ENGINEERING_PROGRAMS else None

def program_contract(slug,modules):
    if slug not in ENGINEERING_PROGRAMS:
        return None
    return {**PRINCIPLES,'modules':[module_contract(slug,m) for m in dict.fromkeys(modules)]}

def chapter(contract):
    parts=['## Software-first practice\n\n'+contract['software_first'], '## Production evidence\n\n'+contract['production_over_playground'], '## Apply the three pillars to '+contract['scenario']]
    for pillar in contract['pillars']:parts.append('### '+pillar['name']+'\n\n'+pillar['application'])
    parts.extend(['## Failure and deployment work\n\n'+contract['operations'],'## Evaluation precision\n\n'+contract['evaluation_note'],'## Module evidence to retain\n\n'+contract['deliverable'],'\n'.join('- '+x for x in contract['release_gates'])])
    return '\n\n'.join(parts)

# Each original module applies the pillars to its own deliverable and data.
MODULE_FOCUS={
 'freelancing-masterclass':{
 '01 · Opportunity and customer discovery':('a discovery interview and opportunity scorecard','Estimate response time, reviewer effort and cost of the current workflow; mark interview assumptions separately from observations. Compare at least two opportunities against a minimum accepted-output standard.','Turn interview claims into falsifiable workflow checks: input availability, reviewer authority and a repeated task. Reject an opportunity without usable evidence.','Inventory which approved source notes the workflow actually needs; exclude unrelated personal/client data and record source ownership.'),
 '02 · Offer and scope':('a fixed-scope statement of work','Specify latency/quality limits and an explicit usage allowance in the offer. Price review, retries and maintenance, not just a successful generation.','Write Given/When/Then acceptance examples and critical exclusions into the scope. Link each promise to an observable test and a named decision owner.','Define allowed sources, revisions, retention and context allowance; a source expansion or new tenant changes scope and cache handling.'),
 '03 · Data and prototype':('a permissioned client-data inventory and prototype','Compare a manual baseline with the prototype on identical synthetic inputs, reporting elapsed/review time, total attempts and accepted outputs.','Use a reviewed acceptance set with missing data and unsupported-claim cases; no polished demo substitutes for the failure report.','Build a source/permission manifest with digest/revision, token estimate, omitted fields and cache invalidation rules before any provider request.'),
 '04 · Quality and delivery':('a client acceptance report and change request','Report per-accepted-output spend, p95 and reviewer corrections for the exact delivery candidate; keep failed and unavailable attempts visible.','Automate structural checks and attach authorized claim-level review. Block delivery when a mandatory gate fails even if averages improve.','Freeze source/prompt/model/context versions with the delivery manifest. Reevaluate after a change instead of silently expanding context.'),
 '05 · Handover and operations':('an operator runbook and incident drill','Include routine usage, alert response, fallback and restore labor in the ongoing service budget. Compare capacity assumptions with actual drill observations.','Have a fresh operator restart, read back, deny wrong-owner access and restore isolated synthetic records; attach transcripts and unresolved failures.','Define who can refresh data, revoke access, invalidate caches and prune logs. A handover needs lifecycle ownership, not a folder of prompts.'),
 '06 · Credibility and repeatability':('an evidence-backed case study and reusable service package','Publish only observed latency, costs and accepted outcomes with workload caveats; do not turn a one-client result into a universal ROI promise.','Link each public claim to dataset/release and acceptance evidence. Test the reusable package with a different synthetic client and retain failures.','Remove client data from reusable templates, reset owner/source IDs and test cross-client isolation and stale-cache rejection.'),
 }
}

# Explicit Python stages avoid number-based heuristics selecting unrelated agent/RAG work.
MODULE_FOCUS['python-for-ai'] = {
 '01 · Contracts and streaming':('typed request boundaries and bounded UTF-8 records',
  'Compare parsing the same byte stream at different chunk boundaries. Measure allocations/record limits before optimizing; no model bill or semantic-quality improvement is implied.',
  'Reject unknown fields/types and truncated or oversized frames. Verify every byte split of the UTF-8 fixture yields identical records; keep the original expected values.',
  'Separate transport bytes, decoded characters and actual provider tokens. Preserve complete framed evidence; a final record is not automatically a completed model answer.',
  'Fail before provider work, cap record and total byte/count allowances, and retain the synthetic input plus failure category for diagnosis.'),
 '02 · Concurrency and recovery':('a cancellable, bounded async work queue',
  'Compare one worker and three on identical inputs. Record queue pressure, peak active work and whole-operation latency; do not infer throughput from sleep(0).',
  'Force out-of-order completion, a failing consumer, parent cancellation and a total deadline. Assert ordered outputs and zero surviving owned tasks.',
  'Bound input batches and queue entries as well as active calls. Do not create one task per unbounded input or use an in-memory prompt as durable state.',
  'TaskGroup must clean up blocked producers and sibling workers. Propagate cancellation; document that an already-running thread or committed write may survive cancellation.'),
 '03 · Providers and evidence':('a validated provider boundary and safe-read retry budget',
  'Count every attempted call, backoff delay and unavailable result under one deadline. Preserve unknown usage; compare connection lifecycle overhead separately.',
  'Use an HTTPX mock transport for status, JSON shape, completion, output bytes and usage. Test exhaustion and denied permission without any model download.',
  'Bound serialized evidence and response bytes before parsing, label byte guards separately from tokenizer counts, and reject partial/incomplete answers before caching.',
  'Classify bad caller input separately from upstream failure. Retry only taught transient reads within budget; a timed-out external write requires reconciliation.'),
 '04 · Context and persistence':('owner-scoped context and a recoverable versioned cache',
  'Compare cold and warm authorized reads with the same source/prompt/model/schema identity. Include SQL work and contention; cache hits do not certify model quality.',
  'Assert wrong-owner exclusion, stable ties, aggregate context allowance, independent revision misses, rollback and readback from a restored SQLite snapshot.',
  'Filter ownership before ranking. Reserve query/instruction/output allowances and key caches by every dependency; do not hide a conflicting policy through arbitrary truncation.',
  'Close connections in finally, commit short transactions, bound lock waits, and test backup/restore separately from connection reopening. In-process single-flight is not distributed locking.'),
 '05 · Evaluation and service boundaries':('a measured HTTP release candidate',
  'Run the versioned case set cold and warm, retain failed attempts in latency observations, and report p50/p95 plus unknown monetary cost explicitly.',
  'Block the contract gate on any failed case, especially owner isolation. Probe 400/401/413/415/429/502/503/504 and a healthy database with an unchecked provider.',
  'Keep credentials outside request/model fields, exclude private prompt bodies from logs, and bind observed answers and cache behavior to exact source/configuration revisions.',
  'Validate the full batch before starting workers. Enforce request body, owner quota, process capacity and batch deadline independently; do not claim global limits across replicas.'),
 '06 · Integrated delivery':('the complete bounded knowledge service and recovery runbook',
  'Save actual fixed-case evaluation output, cold/warm latency and provider-call counts. Separate fixture contract acceptance, real-model review and untested production capacity.',
  'Run the published unit/HTTP/adapter/evaluation tests from the student files alone. Recreate the container with its state volume, rerun owner probes, and test a restored snapshot.',
  'Change model, source and prompt revisions independently and prove stale results miss. Keep byte budgets and measured token usage labeled with their actual units.',
  'Demonstrate provider outage/timeout, no partial answer cached, slot recovery and input preservation at the client. Public hosting additionally needs a production server, TLS, shared admission and measured capacity.')
}

MODULE_FOCUS['ai-agent-bootcamp'] = {
 '05 · Application and data':('the support API, owner-scoped records and reviewable interface',
 'Measure HTTP and storage overhead on the same support cases; report accepted responses and database failures separately from model latency.',
 'Probe request shape, wrong-owner reads, transaction rollback, saved/readback state and honest unavailable responses through the API.',
 'Persist source IDs and decisions outside the prompt; return only the authenticated owner’s records and invalidate cached answers after source changes.',
 'Validate inputs before provider work, keep transactions short, and surface storage/provider failures without claiming a successful save.')
}
MODULE_FOCUS['ai-workshops'] = {
 'Studio 01 · Document extraction':('purchase-request extraction',
 'Compare extracted-field acceptance and reviewer corrections on the same purchase requests; include failed parses and usage in time/cost per accepted record.',
 'Assert required fields, types, missing values and rejected malformed records against fixed purchase-request fixtures.',
 'Select only approved document fields, preserve source/page references and mark missing data instead of filling gaps from unrelated context.',
 'Keep the input fixture on parse/provider failure, bound document/output sizes and route invalid records for correction rather than silent publication.'),
 'Studio 02 · Meeting actions':('meeting commitments and corrections',
 'Measure time plus reviewer corrections per accepted action list; do not count an unreviewed generated commitment as a completed action.',
 'Check owners, dates, missing assignees and corrections against labeled transcript spans; distinguish proposed actions from approved ones.',
 'Retain the supporting transcript span and revision for each commitment; a corrected transcript invalidates the previous draft.',
 'Preserve the draft on dependency failure and require human review before sending commitments or changing an external system.'),
 'Studio 03 · Grounded research':('a claim-and-citation research notebook',
 'Compare citation coverage, unresolved claims, review time and retrieval latency on the same research questions.',
 'Assert citation IDs exist and belong to the selected research set; review claim support separately from mechanical citation validity.',
 'Keep bounded excerpts and provenance; conflicting or missing sources must remain visible instead of being summarized away.',
 'Bound source fetching and extraction, record unavailable sources, and keep an honest incomplete research result for review.'),
 'Studio 04 · Support triage':('support topic and urgency routing',
 'Compare routing errors and reviewer effort on the same labeled tickets; a cheap classification cannot trade away the critical urgency rule.',
 'Replay ambiguous, unknown-topic and high-urgency fixtures. Assert allowed labels and fail-closed escalation before delivery.',
 'Select relevant ticket/policy fields and exclude unrelated customer data; preserve ticket identity and policy revision.',
 'Keep unclassified tickets recoverable when the dependency fails and bound retries; do not convert an exception into a low-priority label.'),
 'Studio 05 · Content operations':('factual content review and local publication',
 'Include drafting, fact review and corrections in accepted-output cost/time; compare on the same brief and source revision.',
 'Check required sections and source references mechanically, then require an authorized claim review before publication.',
 'Use the approved brief and source notes only, retain exceptions and invalidate drafts when the facts change.',
 'Keep a reviewable draft on failure, stage publication locally and preserve the last accepted version for rollback.'),
 'Studio 06 · App sprint':('one integrated studio application',
 'Measure one studio workflow end to end, with failed attempts, reviewer time and declared deployment conditions.',
 'Run its existing acceptance fixtures through the complete input→workflow→saved result path, plus restart and wrong-owner checks where taught.',
 'Carry the chosen studio’s source IDs, input limits, revisions and ownership into the integrated app; avoid a second unrelated agent project.',
 'Deploy the chosen workflow with bounded input/work, visible failures and a reproduction/recovery runbook; mark any untested hosting claim explicitly.')
}
