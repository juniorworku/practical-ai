"""Authored learning dependencies, artifact continuity and taught-to-capstone maps.
Numbers identify stable source sessions, never mutable display positions.
"""
import hashlib
import json

ENTRY = {
 'ai-agent-bootcamp': 'Read and edit Python functions, lists and dictionaries; run a file and understand a failing assertion. No agent, retrieval or model SDK experience is assumed. Start with sessions 1–3 to establish scope, a workspace and labeled cases.',
 'ai-workshops': 'Read small Python functions and dictionary records, run a script and inspect assertions. No previous AI course is required. Studios 1–5 each teach a complete workflow; Studio 6 integrates one chosen workflow, rather than requiring five production applications.',
 'freelancing-masterclass': 'Describe a business workflow and read a table of inputs, outputs and costs. Python specimens are inspectable decision models: explain the values and expected result before running them. No client, paid model account or prior academy program is required. Coding syntax must be learned before modifying the optional code; business deliverables remain required.',
 'ai-engineering-12-week': 'Write Python functions, use lists/dictionaries and exceptions, run scripts and read assertions. Basic HTTP/JSON, SQL, Git and command-line familiarity are expected. Async, streaming, retrieval, agents and deployment are taught here. A model account and cloud spending are optional extensions, not prerequisites for the local learning route.',
 'genai-accelerator': 'Read Python functions, lists/dictionaries, imports, exceptions and assertions; run a script in a terminal. Start at the product brief and reproducible project, then follow the interleaved labs. Frameworks and infrastructure are introduced in sequence. This is an independent program; completing AI Engineering or Bootcamp is not required.',
 'terminal-tutor': 'No agent, protocol or other academy program is required. You need a terminal, a text editor and Python 3.12 to execute the examples. The first guide teaches the small Python vocabulary used here; pause there until you can explain its assertions. The academy command box is a simulation; use your own scratch folder for real execution.',
}
# Stage ranges are stable, one-based source numbers. Each checkpoint is a
# concrete integration of earlier teaching, not another arbitrary code variation.
STAGES = {
 'ai-agent-bootcamp': [(1,3,'a bounded support brief and labeled case table'),(4,6,'a validated adapter contract with failure and context limits'),(7,9,'versioned evidence and citation/abstention checks'),(10,12,'a bounded dispatcher with approval and replay controls'),(13,15,'an API/data boundary and reviewable status states'),(16,18,'regression, injection and latency/cost evidence'),(19,21,'a container, recovery transcript and orchestration decision'),(22,24,'the support-agent release packet')],
 'ai-workshops': [(1,3,'validated extraction records and a review queue'),(4,6,'a confirmed action register and omission checks'),(7,9,'a claim/citation notebook and benchmark memo'),(10,12,'a taxonomy, confusion matrix and review queue'),(13,15,'a bounded brief, revision rubric and publishing approval'),(16,18,'one integrated workflow with persistence and a portfolio evidence index')],
 'freelancing-masterclass': [(1,3,'a buyer/workflow brief with a measured baseline'),(4,6,'an offer, statement of work and estimate'),(7,9,'a data map, thin pilot and scoped feedback log'),(10,12,'an evaluation report, milestone plan and change ledger'),(13,15,'a recovery runbook, acceptance record and support agreement'),(16,18,'a consent-aware case study and consistent final client packet')],
 'ai-engineering-12-week': [(1,6,'a local voice-session acceptance report'),(7,15,'a source-grounded knowledge-base evidence pack'),(16,24,'a permissioned workspace-agent trace'),(25,30,'a repeatable evaluation and release report'),(31,36,'a deployed or explicitly local graduation packet')],
 'genai-accelerator': [(1,10,'a product brief, baseline and reliable provider boundary'),(11,20,'typed service states, scope and context contracts'),(21,29,'an API, persisted ingestion and worker recovery transcript'),(31,40,'versioned chunks and retrieval/grounding comparisons'),(41,50,'security cases, traces and an automated release gate'),(51,60,'a deployment/recovery evidence pack'),(61,66,'a bounded agent trace and validated decision adapter'),(67,72,'a resumable approval-aware graph'),(73,78,'a measured worker-team comparison'),(79,84,'an MCP discovery/call/error transcript')],
 'terminal-tutor': [(1,2,'a scratch workspace and observed process-exit transcript'),(3,5,'a prediction, changed example and retained counterexample'),(6,8,'a bounded tool decision and resumable evidence note')],
}
# (checkpoint source number, [(required capability, prior teaching numbers)], integration steps)
CAPS = {
 'ai-agent-bootcamp': [(22,[('scope and labeled cases',[1,3]),('contract, timeout and bounded evidence',[4,5,6]),('authorized retrieval and grounded abstention',[7,8,9]),('allowlisted loop, approval and replay protection',[10,11,12]),('HTTP and persistent ownership boundary',[13,14]),('regression, injection and measured trace',[16,17,18]),('container and recovery evidence',[19,20])], 'Choose the support workflow from session 1. Reuse the case labels from 3 without changing expected answers to fit the candidate. Wire the adapter, retrieval and dispatcher through the API boundary. Record one supported question, one unsupported question, one denied action and one timeout as full request/result traces. Carry unresolved defects into sessions 23–24; a fixture-only run stays labeled local.'),
 (24,[('vertical slice and findings',[22,23]),('packaging and recovery',[19,20])], 'Package the exact candidate evaluated in 22–23. Verify the file manifest, repeat setup in a fresh workspace and retain the recovery transcript. A missing or unresolved critical finding blocks the release decision.')],
 'ai-workshops': [(16,[('extraction with review',[1,2,3]),('meeting action confirmation',[4,5,6]),('grounded research and benchmark',[7,8,9]),('triage routing and review',[10,11,12]),('content approval and revision',[13,14,15])], 'Select ONE of the five taught studios. Write its input record, transformation, uncertainty/review state and expected output. Reuse that studio’s positive and negative cases. This is the scope/design checkpoint: persistence is introduced in session 17, so do not claim an implemented durable application yet.'),
 (18,[('selected studio specification',[16]),('integration, persistence and tests',[17]),('review and evaluation patterns',[3,6,9,12,15])], 'Implement the one workflow selected in 16 with the persistence pattern taught in 17. Run its cases through the whole path, reopen stored state, and test the review route. Index actual evidence files from all completed studios, distinguishing practice artifacts from the single integrated app. Missing or empty evidence is incomplete; do not invent five deployed apps.')],
 'freelancing-masterclass': [(18,[('buyer, discovery and baseline',[1,2,3]),('bounded offer, acceptance and estimate',[4,5,6]),('data, pilot and feedback',[7,8,9]),('evaluation, risk and change control',[10,11,12]),('recovery, acceptance and support',[13,14,15]),('evidence claims and outreach boundaries',[16,17])], 'Use one simulated client throughout the final packet. Compare the offer, statement of work, acceptance report, handover and client email field by field. Every promised outcome needs the matching observed test or an explicit untested label. Apply the change ledger to extra requests. Submit the recovery and support decision with the case study; a convincing email cannot override failed acceptance. No real outreach or client purchase is required.')],
 'ai-engineering-12-week': [(6,[('adapter and session/token state',[1,2]),('concurrency and cancellation',[3]),('backpressure and interruption',[4,5])], 'Combine the taught local session events into a voice trace. Include normal output, no-audio, interruption and deadline cases. Measure first-output latency and quality separately; fast silence fails. This checkpoint is local/session-level. Containers, distributed quotas and cloud scaling are taught in Module 5 and are not required here.'),
 (15,[('provenance and chunking',[7,8]),('versioned index, filtering and retrieval',[9,10,11]),('rerank budget, citations and stream failure',[12,13,14])], 'Trace one source from intake to chunk, index, selected context and cited answer. Run a multi-passage gold question and a no-source question; report passage recall separately from answer judgment. Reuse token accounting from Module 1. Compare the local baseline with the optional configured service integration without claiming a hosted release.'),
 (24,[('permissioned tools and state',[16,17]),('approval binding and scoped memory',[18,19]),('orchestration and MCP boundaries',[20,21]),('replay/reconciliation and event intake',[22,23])], 'Replay a synthetic workspace event through retrieval, draft, approval and effect ledger. Attempt a stale-payload approval, duplicate event and missing-evidence request. Retain state/effect counts and a trace. Live Slack/calendar accounts and cloud hosting are optional extensions; local fixtures must not be described as external delivery.'),
 (30,[('rubrics and labeled case harness',[25,26]),('CI release gate and redacted traces',[27,28]),('useful-output economics',[29])], 'Freeze the dataset and candidate versions. Run the taught 120-case harness, retain individual failures, incomplete review and critical populations. Compare latency and cost per accepted output. Enforce the predeclared quality floor and block missing/unknown results. Do not relabel fixtures as a real concurrent cloud load test.'),
 (36,[('prior integrated agent and release evidence',[24,30]),('containers and concurrency',[31,32]),('local-model capacity and distributed budgets',[33,34]),('hybrid routing and load experiment',[35])], 'Reuse the candidate and regression cases, then add the taught hybrid routing, quota and load experiment. Rehearse fresh-operator setup and recovery. Each release field is passed, failed or untested; only observed passed checks may support a release claim. A local run is an honest local graduation path; cloud scale requires the actual deployment/load evidence, not configuration alone.')],
 'terminal-tutor': [(8,[('workspace and exit evidence',[1,2]),('prediction, execution and counterexamples',[3,4,5]),('tool permission and instruction inspection',[6,7])], 'Resume the scratch exercise from guides 1–5. Write the workspace path, exact command, observed exit code, passed/failed assertions, permitted tool and next action in the bounded note. Reopen the file and rerun the named check. Change the source fixture: stale evidence must be marked for rerun rather than reused as current proof.')],
}
LAB_AFTER={1:5,2:10,3:15,4:20,5:25,6:29,7:33,8:37,9:40,10:44,11:48,12:50,13:59,14:60,15:66,16:68,17:72,18:78,19:81,20:84}
LAB_SOURCES={1:[1,2,5],2:[6,9,10],3:[11,12,13,14,15],4:[16,17,18,19,20],5:[21,22,23,24,25],6:[25,26,27,28,29],7:[31,32,33],8:[34,35,36,37],9:[38,39,40],10:[41,42,43,44],11:[45,46,47,48],12:[49,50],13:[51,52,53,54,55,56,57,58,59],14:[49,50,55,57,58,59,60],15:[61,62,63,64,65,66,85],16:[67,68],17:[69,70,71,72],18:[73,74,75,76,77,78],19:[79,30,80,81],20:[79,80,81,82,83,84]}

BOOTSTRAP = '''## The Python vocabulary used in these guides

Run this complete small example first, before the filesystem specimen. Save it as basics.py in your scratch directory and use `python3 -I basics.py`.

```python
# = binds a name; strings hold text; lists keep ordered items.
ids = ['p1', 'p2']
# A dictionary binds named fields to values.
record = {'source': ids[0], 'text': '14 days'}
# def defines a function. Indented lines form its body; return supplies its result.
def first_source(items):
    return items[0]
assert first_source(ids) == record['source']
assert len(ids) == 2
print('p1; two sources; assertions passed')
```

Expected output: `p1; two sources; assertions passed`. Change the expected length to 3 and rerun: AssertionError means the expectation failed; restore 2 before continuing. `==` compares rather than assigning. `import` makes a named library available: pathlib provides Path objects and tempfile creates disposable workspaces. `with` enters a resource context and closes/cleans it when the indented block ends, including on an error. `root / 'exercises'` joins a Path with a child name; it is not numeric division. A method such as `.write_text(...)` performs the named operation on that object. In the next specimen, trace each of these operations before running. You are not expected to know an agent SDK to learn file ownership.
'''

def key_number(row): return int(row['source_id'].rsplit(':',1)[-1]) if row['source_id'].startswith('academy-') else int(row['source_id'].rsplit('-',1)[-1])
def refresh(row):
    learning=row['resources']['learning']
    learning['revision']=hashlib.sha256(json.dumps({k:v for k,v in learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()
    row['content']='# '+row['title']+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in learning['chapters'])
    row['content_hash']=hashlib.sha256(row['content'].encode()).hexdigest()

def apply(programs):
    for program in programs:
        slug=program['slug']
        if slug not in ENTRY: continue
        rows=program['lessons'];by_number={key_number(r):r for r in rows if not r['source_id'].startswith('lab-')}
        if slug=='genai-accelerator':
            labs={key_number(r):r for r in rows if r['source_id'].startswith('lab-')};ordered=[]
            for n in range(1,85):
                if n==30:continue  # narrow MCP preview follows protocol foundations
                row=by_number[n];ordered.append(row)
                if n==66:ordered.append(by_number[85])
                if n==79:
                    by_number[30]['module']=row['module'];ordered.append(by_number[30])
                for lab,after in LAB_AFTER.items():
                    if after==n:
                        labs[lab]['module']=row['module'];ordered.append(labs[lab])
            rows=program['lessons']=ordered
        checkpoints={n:(coverage,steps) for n,coverage,steps in CAPS.get(slug,[])}
        for position,row in enumerate(rows):
            learning=row['resources']['learning'];n=key_number(row);is_lab=row['source_id'].startswith('lab-')
            stage=next((s for s in STAGES[slug] if s[0]<=n<=s[1]),STAGES[slug][-1])
            if slug=='genai-accelerator' and n==85 and not is_lab:stage=STAGES[slug][6]
            if slug=='genai-accelerator' and n==30 and not is_lab:stage=STAGES[slug][-1]
            if slug=='genai-accelerator' and is_lab:
                sources=LAB_SOURCES[n];stage=next((s for s in STAGES[slug] if s[0]<=LAB_AFTER[n]<=s[1]),STAGES[slug][-1])
                coverage=[('Integrate the mechanisms and preserve their negative checks',sources)]
                steps='Reopen the listed lesson specimens and their observed results. Use the complete lab baseline to combine those boundaries, then attempt the bounded variation. Retain each earlier counterexample. Explain any changed interface or fixture instead of assuming the examples share a database or identical policy period. A passing lab specimen is local evidence; perform the separately taught service integration only when its setup prerequisites are met.'
            else:coverage,steps=checkpoints.get(n,([],''))
            prerequisites=[{'source_id':by_number[i]['source_id'],'title':by_number[i]['title']} for _,nums in coverage for i in nums]
            previous=rows[position-1] if position else None
            if previous and not prerequisites:prerequisites=[{'source_id':previous['source_id'],'title':previous['title']}]
            progression={'entry':ENTRY[slug],'position':position+1,'stage_artifact':stage[2],'prerequisites':list({r['source_id']:r for r in prerequisites}.values()),'coverage':[{'requirement':name,'sources':[by_number[i]['source_id'] for i in nums]} for name,nums in coverage]}
            learning['progression']=progression
            if slug=='genai-accelerator' and not is_lab and n==85:
                progression['stage_artifact']='a bounded agent trace and validated decision adapter'
            body=('## Before this session\n\n'+(ENTRY[slug] if position==0 else 'Bring your notes and observed output from **'+previous['title']+'**. Earlier completion clicks are not evidence of understanding: explain the input, output and failing case before adding this boundary.')+'\n\n')
            if progression['prerequisites']:
                body+='### Specific preparation\n\n'+'\n'.join('- '+r['title']+' (`'+r['source_id']+'`)' for r in progression['prerequisites'])+'\n\nIf you cannot explain one of these mechanisms, return to that session’s trace and counterexample, rerun its reference, then retry your own version. The stable IDs identify lessons inside this program; no external enrollment is required.\n\n'
            if previous:
                prior=previous['resources']['learning']
                concept=prior['concepts'][0]
                body+='## Readiness check from the previous session\n\nExplain **'+concept['term']+'** before continuing. Compare your explanation with this recap: '+concept['definition']+'\n\nReproduce the earlier positive case and its counterexample from your saved implementation. If you can only recall a passing output, reopen its walkthrough and explain why the counterexample must fail. Then identify what this session adds to that contract.\n\n'
            body+='## Carry work forward\n\nBuild toward **'+stage[2]+'**. Keep one evidence folder for this stage: source input, implementation, unchanged expected labels, observed output and unresolved failures. Compare this lesson’s new boundary with the previous result. The complete examples are independent fixtures: deliberately map their field names and source revisions before reusing code; do not concatenate scripts and assume their data agrees.\n\n'
            if slug=='ai-workshops':body+='At a studio boundary, open a new fixture for the new use case, but carry forward the validation, review-state and evaluation habits. The final sprint selects one studio for end-to-end integration.\n\n'
            if coverage:
                body+='## Taught-to-project evidence map\n\n'+ '\n'.join('- **'+name+'** — taught in '+', '.join(by_number[i]['title'] for i in nums)+'. Evidence: retain those lessons’ successful case and negative check in the project report.' for name,nums in coverage)+'\n\n## Assemble, then test\n\n'+steps+'\n\n## Feedback when integration fails\n\nFind the first boundary whose actual output differs from its contract. Rerun that lesson’s isolated positive and negative checks. If they pass, inspect the connecting field names, owner/source IDs, units and state transitions; do not weaken the gold labels or bypass a denied path. Record the failing input and unresolved result. Passing a single variation does not establish the whole project.\n\n'
                criterion='Project evidence traces each mapped capability to its taught lesson, retains its negative check, and records the combined path with unresolved or untested boundaries explicitly labeled.'
                learning['task']['criteria'].append(criterion)
                learning['exercise']['steps'].append('Complete the integration sequence and evidence map in the learning progression chapter; keep the bounded specimen variation as a separate check.')
                learning['exercise']['material']+='\n\n## Integrated project requirement\n\n'+steps+'\n\n'+criterion
            if position+1<len(rows):body+='## Next checkpoint\n\nNext: **'+rows[position+1]['title']+'**. Save your current inputs, actual output and one unresolved question so the next session can extend a known baseline.'
            else:body+='## Completion boundary\n\nReopen the evidence packet in a fresh session. A complete program records both successful checks and remaining limits. Choose further study by the missing capability; another academy program is optional, not a hidden graduation prerequisite.'
            chapters=[c for c in learning['chapters'] if c['id']!='progression']
            # Replace the old circular prerequisite claim in the imported orientation.
            for c in chapters:
                if c['id']=='orientation':c['body']='This session teaches **'+row['title']+'**.\n\n'+ENTRY[slug]+'\n\nRead the progression and concept chapters before the complete specimen and exercise. Compare feedback only after predicting and attempting the task.'
            chapters.insert(0,dict(id='progression',title='Learning progression and project preparation',kind='Learning path',body=body))
            if slug=='terminal-tutor' and position==0:chapters.insert(1,dict(id='python-onramp',title='Python vocabulary before filesystem practice',kind='Concept teaching',body=BOOTSTRAP))
            for c in chapters:
                if c['id'] in {'complete-stack','complete-api','sdk-integration'}:
                    c['body']='**Integration timing:** This is a complete worked integration to revisit after the relevant setup lessons. The core exercise remains the self-contained specimen. '+('Run the full database/worker stack after lessons 21–29 and Lab 6; earlier appearances are a preview, not an unexplained Docker prerequisite.' if c['id']=='complete-stack' else 'Install framework dependencies only after reading this chapter’s setup; environment failure is not an exercise result.')+'\n\n'+c['body']
            learning['chapters']=chapters
            if slug=='genai-accelerator':row['order']=position
            refresh(row)
    return programs
