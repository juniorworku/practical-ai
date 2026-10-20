"""Publish the independent twelve-week engineering course as native learning content."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from .curriculum import MODULES,ROWS
from .labs import LABS
from .diagnostics import CHECKS
from .student_guides import GUIDES
from .feedback import MISTAKES,BOUNDARY_MISTAKES
ROOT=Path(__file__).resolve().parents[2]
EXAMPLES=ROOT/'backend/academy/content/engineering_examples'
def fence(code,kind='python'):return '```'+kind+'\n'+code.strip()+'\n```'
WRONGS=[
 ('Let provider-specific SDK objects leak into every route.','Mark every returned string as a saved final answer.'),
 ('Reuse a cache key containing only the user question.','Count only the visible reply as total input usage.'),
 ('Launch every provider call immediately and gather later.','Keep the semaphore permit after a timed-out child exits.'),
 ('Send WebM bytes while declaring raw PCM16.','Keep every captured frame until the provider catches up.'),
 ('Stop only future generation and let scheduled playback finish.','Replay every old frame after reconnecting.'),
 ('Divide successful-request spend by every attempted request.','Report first audio time as completed-task latency.'),
 ('Activate an upload revision before parsing/indexing succeeds.','Deduplicate across tenants using a global digest alone.'),
 ('Split before every exception to reduce chunk size.','Call a word count exact provider token usage.'),
 ('Pad vectors from a new model to fit the old index.','Compare vectors from different model versions directly.'),
 ('Retrieve globally and hide unauthorized citations afterward.','Rely on a query string naming the tenant as authorization.'),
 ('Add raw lexical and cosine scores without calibration.','Let one duplicate candidate occupy multiple final slots.'),
 ('Use returned indexes as new source IDs.','Accept a reranker result outside the supplied candidate list.'),
 ('Treat any valid citation ID as proof of entailment.','Replace factual review with fluent writing quality.'),
 ('Persist the partial draft as a complete response after disconnect.','Retry by appending new tokens to an unrelated partial generation.'),
 ('Include no-answer queries as ordinary positive relevance labels.','Compute recall using only the queries the retriever answered.'),
 ('Trust the model to choose its tenant and scopes.','Retry every tool invocation including uncertain writes.'),
 ('Keep the checkpoint in a worker global and call it durable.','Resume an old checkpoint without checking its state version.'),
 ('Approve a label and permit later destination changes.','Use a previous actor\'s approval after expiry.'),
 ('Retain revoked facts because they appeared in a summary.','Use owner-free cache keys for shorter prompts.'),
 ('Add a second role because agreement proves independent verification.','Compare only the fastest branch and ignore duplicate spend.'),
 ('Treat tool discovery metadata as permission to call it.','Expose all host files because the server is local.'),
 ('Create a new operation key whenever a response times out.','Mark every timed-out write as definitely not committed.'),
 ('Acknowledge before persisting and discard repeated delivery IDs.','Process repeated events with new proposal IDs each time.'),
 ('Allow scheduling whenever a draft sounds confident.','Use a model response as the sole authority to send a message.'),
 ('Use citation membership as the entire faithfulness metric.','Assume a low-temperature model judge is a deterministic oracle.'),
 ('Count generated case IDs as 120 tested prompts.','Send expected labels to the application so it can choose correctly.'),
 ('Promote because the average score increased despite a critical failure.','Change the prompt without changing the release manifest.'),
 ('Sum parallel span durations and label the result wall time.','Export full confidential prompts for every successful request.'),
 ('Remove failed requests from spend calculations.','Claim the cheapest model wins regardless of acceptance rate.'),
 ('Call all 120 attempts semantically evaluated after reviewing 100.','Drop unavailable requests before computing completion rate.'),
 ('Let browser code connect directly to the Docker database hostname.','Treat a running process as proof its database is ready.'),
 ('Set a high concurrency limit and assume hardware scales with it.','Keep quota counters in a single instance\'s memory.'),
 ('Advertise arithmetic GPU slots as measured throughput.','Treat OpenAI-compatible transport as identical model behavior.'),
 ('Run a separate tenant quota counter inside each replica.','Switch provider without reevaluating data residency or output quality.'),
 ('Send locally restricted documents to a premium fallback silently.','Compare routes on different easier workloads.'),
 ('Publish a thousands-of-users claim from configuration alone.','Hide the missing load report behind a completion checkbox.'),
]

def appendix(number):
    names={6:['live_requirements.txt','voice_gateway.py','voice.html'],7:['media_ingest.py'],
      9:['embedding_adapter.py','vector_lab.sql'],12:['provider_adapters.py'],17:['langgraph_review.py'],
      21:['mcp_policy.py','mcp_client.py'],22:['workspace_state.py'],24:['workspace_connectors.py'],
      26:['evaluation_suite.py'],33:['provider_adapters.py']}.get(number,[])
    if not names:return None
    setup='''## Save and run the complete integration files

These files are part of this lesson, not a download assignment. Save each under the shown name in an isolated workspace. Use Python 3.12 and `python3 -m venv .venv`, then activate that environment. Only install packages for the integration you are running. Record resolved dependency versions with `python -m pip freeze > tested-dependencies.txt`; a version range is not a tested lock file. The standard-library experiment in the previous chapter needs none of these dependencies. Use synthetic data and your own authorized test accounts. Provider calls may incur charges; free academy enrollment does not include provider credits.

'''
    commands={
      6:'''Install the packages listed in live_requirements.txt. Set `VOICE_LAB_TOKEN` to a new local secret, then run `python -m uvicorn voice_gateway:app --host 127.0.0.1 --port 8092`. Open http://127.0.0.1:8092/ and enter that token. In the default echo mode, connect and capture microphone audio; hearing the echo establishes PCM transport only. Inspect bounded playback and Stop behavior. Reject a wrong token and disallowed origin.

For an opt-in real assistant, set server-side `VOICE_MODE=gemini`, `GOOGLE_API_KEY` and `GEMINI_LIVE_MODEL` to a supported Live audio model before starting the server. No API key goes in HTML. The browser captures 16kHz PCM16; provider output is played at 24kHz. Record end-of-speech→first-audible-output, total task latency, interruptions, completed tasks and actual usage. Disconnect mid-turn and verify cancellation. The loopback token is a transport-lab credential, not a production identity system. Before public hosting, add authenticated per-user session grants, shared admission/quota enforcement and a tested reconnect policy. A health response reports gateway readiness and never certifies the upstream provider.''',
      7:'''Install `pypdf` and `python-docx` for local files, `httpx` for approved website retrieval. Run `python media_ingest.py sample.pdf sample.docx sample.vtt > parsed.jsonl`. The program includes page/paragraph/time locators and rejects unsupported/empty extraction. Supply synthetic fixtures you can inspect; a scan requires an explicit OCR path, not invented text. The async approved-origin function is available for your ingestion worker; its operator allowlist must never come from a user's uploaded URL. Add a bounded worker timeout and controlled network egress before accepting untrusted files/sites.''',
      9:'''First install httpx and select an installed local embedding model in Ollama. Set LOCAL_EMBEDDING_MODEL and EXPECTED_EMBEDDING_DIMENSIONS for its documented index contract, then run `python embedding_adapter.py`. The complete adapter sends bounded batches to /api/embed with truncation disabled, validates model/batch/dimension/finite vectors and preserves input order. A model-name mismatch is a deliberate hard error requiring operator inspection rather than silent index mixing. This opt-in run can download/use local model resources; no request is made by importing the file.

Use an isolated pgvector PostgreSQL database. Run `psql "$VECTOR_LAB_DSN" -v ON_ERROR_STOP=1 -f vector_lab.sql` after setting the DSN for that disposable database. This schema deliberately uses three-dimensional synthetic vectors to expose owner filtering and score order; it is not a real semantic embedding. Inspect exact-search output before the HNSW index. Replace it with a documented embedding adapter and a matching parallel index before evaluating semantic retrieval. Parameterize application queries and derive owner from authenticated identity, never from model output.''',
      12:'''Install `httpx` and `cohere`. Import `cohere_rerank` from provider_adapters.py and pass your bounded authorized candidate list and query. Configure `COHERE_API_KEY` and `COHERE_RERANK_MODEL` for a supported model. Keep the candidate IDs before calling; returned indexes map into that exact list. Run labeled retrieval cases with reranking both enabled and disabled, recording real additional latency/cost. The offline index-mapping example proves neither relevance nor quality.''',
      17:'''Install `langgraph`, save langgraph_review.py and run `python langgraph_review.py`. The first invocation stops at an interrupt; the resume applies the supplied review decision. The example deliberately uses an in-memory saver: a new process loses it. Implement a durable checkpointer with an owner-bound thread ID before claiming restart recovery. Test replaying the approval and modifying its payload; neither should create a new remote effect.''',
      21:'''Install `mcp`; save both files together. Run `python mcp_client.py`. The real stdio client initializes the session, discovers the single read-only tool and calls it. The server's policy fixture is fixed and synthetic. Extend it with a denied unknown-policy case and argument validation. Do not register this toy server as a broad filesystem or connector capability: discovery describes what exists; the host and dispatcher still enforce authorization.''',
      22:'''Run `python workspace_state.py`. It creates a temporary SQLite database, closes/reopens it and checks duplicates, owner denial and one locally committed fake effect. This is durable local state, not a distributed exactly-once guarantee. Wire real connectors only behind the same current-payload approval and scoped operation key. For a lost remote acknowledgement, retain uncertain state, query the original destination and reconcile before replay. A local database rollback cannot undo a remote message.''',
      24:'''Install httpx. Import Connectors without executing writes. First run history() against an allowlisted test channel and freebusy() against your own selected calendar with authorized OAuth grants. The same adapter also demonstrates Gmail metadata retrieval and reviewed draft creation: it creates a draft only, never sends. Grant the minimum required OAuth scope, store the trusted review and handle uncertain draft creation without blind retry. Store and deduplicate verified event IDs using the durable inbox from session 22; page history with the returned cursor rather than silently claiming complete monitoring. The signature helper authenticates the exact raw webhook body and rejects old timestamps; persist the verified inbox before acknowledging. Draft a source-grounded answer locally, then construct an exact event proposal with timezone-aware start/end and inspect conflicts. Do not let the model select channel/calendar ownership. create_reviewed_event() requires a trusted stored approval, uses a stable scoped destination ID and returns uncertain instead of blindly retrying. Reconcile uncertain/409 outcomes against the approved canonical fields before updating your state machine. Rate-limit responses require bounded scheduled retries for reads; do not apply read retries to writes. OAuth refresh, distributed workers and actual semantic quality remain integration tasks you must test. No connector is invoked automatically by this lesson.''',
      26:'''Run `python evaluation_suite.py --output fixture-report.json`. This executes 120 concrete inputs across twelve behavior families and ten fictional organization scopes. Review the generated cases with `from evaluation_suite import cases`; each has an actual prompt, initial state, expected decision and source IDs. All ten organization variants stay in the same split as their family; they are isolation variants, not 120 independent task families.

The default deterministic rule fixture tests the harness and mechanical contracts, not AI quality. For your application's adapter, implement POST accepting only the request object (`prompt`, `context`) and returning `decision`, `source_ids`, `tenant`, `revision`, `text`, `cost_usd` and `effect_committed`. Configure `EVAL_TARGET_TOKEN` and run `python evaluation_suite.py --target http://127.0.0.1:9000/evaluate --output candidate-report.json`. Labels are never sent. Keep every failure and timeout in the denominator. The report deliberately leaves semantic_reviewed at zero: add a separately versioned claim-level review table before claiming faithfulness or answer quality. Critical schema/permission/effect failures block release even if the mean improves.''',
      33:'''Install Ollama separately and explicitly select/download a model you are authorized to run; record its version/quantization and hardware. Install `httpx`, set `LOCAL_MODEL` and run `python provider_adapters.py` against the local Ollama endpoint. The adapter parses NDJSON deltas and requires a final done record before completion. For vLLM, separately configure its supported chat endpoint, served model name, authentication and GPU limits; transport compatibility does not imply the same streaming fields, tokenization or quality. Compare identical labeled workloads and include warm-up, input/output length, concurrency, p95, error rate, memory and accepted-output quality. Never infer GPU throughput from the synthetic memory arithmetic alone.''',
    }
    body=setup+commands[number]+'\n\n'+'\n\n'.join('### '+name+'\n\n'+fence((EXAMPLES/name).read_text(),'html' if name.endswith('.html') else 'sql' if name.endswith('.sql') else 'text' if name.endswith('.txt') else 'python') for name in names)
    return {'id':'integration','title':'Complete integration: implementation and test boundaries','kind':'Integration lab','body':body}

def build():
    course=dict(slug='ai-engineering-12-week',title='AI Engineering',category='Engineering',
      description='A 12-week software-first engineering program: streaming voice, mixed-media RAG, workspace agents, repeatable evaluation and measured production deployment. Build five connected capstones with concrete failure and release gates.',
      audience='Developers comfortable with Python functions, exceptions, HTTP and basic SQL. No prior model training or calculus required.',
      outcome='A scoped hybrid-model SaaS release with authenticated data boundaries, automated contracts, reviewed answer quality, cost/latency reports, recovery evidence and a fresh-operator handover.',
      duration='12 weeks · 36 build sessions',level='Prerequisites: Python, HTTP/JSON, basic SQL and Git. Budget roughly 12–18 hours/week; provider/GPU experiments are optional and separately billed.',order=4,lessons=[],_capstone='An evidence-backed hybrid AI SaaS release')
    for number,(title,terms,case,decision) in enumerate(ROWS,1):
        module,weeks,start,end,outcome,body=next(m for m in MODULES if m[2]<=number<=m[3])
        lab=LABS[number];guide=GUIDES[number]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'example.py';p.write_text(lab['code'])
            result=subprocess.run([sys.executable,'-I',str(p)],cwd=d,capture_output=True,text=True,timeout=15,check=True)
            solution_code=lab['code']+'\n# Guided practice reference implementation\n'+guide['extension']
            p.write_text(solution_code)
            solved=subprocess.run([sys.executable,'-I',str(p)],cwd=d,capture_output=True,text=True,timeout=15,check=True)
        concepts=[{'term':term,'definition':definition} for term,definition in terms]
        chapters=[]
        if number==start:chapters.append({'id':'module-foundation','title':module+' · system design','kind':'Module concepts','body':body+'\n\n## Module capstone\n\n'+outcome+'\n\n'+weeks+'. Keep one versioned dataset and baseline through these sessions; do not change inputs while claiming an improvement.'})
        chapters.append({'id':'decision','title':title+' · concepts and decision','kind':'Teaching & prerequisites',
          'body':f'## Before you begin\n\n'+guide['prerequisite']+' Use Python3.12 with assertions enabled. All core practice runs offline with the standard library; provider accounts are only for separately labeled integration work.'+'\n\n## The case\n\n'+case+'\n\n## Reason through the decision\n\n'+decision+'\n\n'+lab['reason']+'\n\n## Vocabulary used in this session\n\n'+'\n\n'.join('### '+a+'\n\n'+b for a,b in terms)})
        chapters.append({'id':'concept-tutorial','title':'Learn each concept step by step','kind':'Guided concept teaching','body':'Read these three explanations before running the specimen. Each connects a definition to the decision it controls.\n\n'+'\n\n'.join('## Step '+str(i+1)+' · '+term+'\n\n'+explanation for i,((term,_),explanation) in enumerate(zip(terms,guide['explanations'])))})
        chapters.append({'id':'implementation','title':'Read, run and explain the complete implementation','kind':'Worked implementation',
          'body':'## Walk through the data and state\n\n'+'\n\n'.join(str(i+1)+'. '+t for i,t in enumerate(guide['trace']))+'\n\n## Predict before execution\n\nSave this entire block as example.py in an empty directory. Run `python3 -I example.py` with assertions enabled. It uses only the Python standard library, includes its synthetic data and performs no provider calls. Explain each assertion before running.\n\n'+fence(lab['code'])+'\n\n## Observed output\n\n'+fence(result.stdout,'text')+'\n\n## Transfer beyond the fixture\n\n'+lab['reason']+'\n\n'+lab['change']})
        extra=appendix(number)
        if extra:chapters.append(extra)
        if number==27:
            chapters.append({'id':'evaluation-ci','title':'Continuous evaluation: complete CI workflow and release boundaries','kind':'Integration lab','body':(EXAMPLES/'evaluation_ci.md').read_text()})
        if number==32:
            chapters.append({'id':'cloud-release','title':'Cloud Run release experiment and ECS comparison','kind':'Deployment runbook','body':(EXAMPLES/'cloud_runbook.md').read_text()})
        if number==31:
            from course_books.container_lab import FILES,RESTORE_SCRIPT
            from course_books.build import docker_instructions
            chapters.append({'id':'container-project','title':'Complete container network and recovery project','kind':'Integration lab',
              'body':'This deliberately small DRF/PostgreSQL experiment isolates deployment boundaries. Its HTTP form is a network fixture; keep React in your integrated SaaS.\n\n'+'\n\n'.join('### '+name+'\n\n'+fence(text,'python' if name.endswith('.py') else 'html' if name.endswith('.html') else 'yaml' if name.endswith('.yaml') else 'text') for name,text in FILES.items())+'\n\n'+docker_instructions()+'\n\n### Isolated restore drill\n\nSave this complete shell script as restore-drill.sh and run `sh restore-drill.sh` from that lab directory while its stack is healthy. It restores synthetic records into a separate named test database, verifies readback without modifying the source database. The script retains the isolated restore database and backup for inspection; remove only those named lab artifacts when finished.\n\n'+fence(RESTORE_SCRIPT,'sh')})
        steps=['Read the concept tutorial, trace the complete baseline and predict its assertions before running.',guide['task'],'Run your change against the named normal and failure cases. Compare actual output with the reference only after making your own attempt.']
        criteria=['The baseline ran and each supplied assertion/state change is explained using the step-by-step trace.',guide['task'],'The submitted implementation includes both positive and negative assertions and records actual output; its limitations are labeled.']
        if number==end:steps.append('Then complete the module integration capstone: '+outcome+' Keep actual reports for the four module release gates; state whether each result is simulated or observed against a deployed system.')
        solution='## Complete guided-practice reference\n\nSave the entire following block as solution.py and run `python3 -I solution.py` in a new scratch directory. No prior files or provider account are needed. This is one reference implementation of the bounded practice, not a completed live capstone.\n\n'+fence(solution_code)+'\n\n## Expected reference observation\n\n'+fence(solved.stdout,'text')+'\n\n## If your result differs\n\n'+guide['diagnosis']+'\n\n## Explain before continuing\n\nCompare the changed code with the baseline: which new input or state transition is protected, and which integration behavior remains untested?'
        material='## 1. Inspect the input and predict the outcome\n\n'+'\n\n'.join(str(i+1)+'. '+t for i,t in enumerate(guide['trace']))+'\n\n'+fence(lab['code'])+'\n\n## Expected baseline observation\n\n'+fence(result.stdout,'text')+'\n\n## 2. Make the targeted change\n\n'+guide['task']+'\n\n## What to submit and check\n\n'+'\n'.join('- '+c for c in criteria)+'\n\n'+'\n'.join(steps)
        chapters.append({'id':'project','title':'Practice first, then integrate','kind':'Practice and acceptance',
          'body':'## Your practical task\n\n'+'\n\n'.join(f'{i+1}. {step}' for i,step in enumerate(steps))+'\n\n## Acceptance rubric\n\n'+'\n'.join('- '+c for c in criteria)+'\n\n## Next: integration work\n\n'+lab['change']+'\n\nComplete the bounded task first. Carry its invariant and tests into this larger project. Earlier sessions and the inline integration files supply the building blocks; optional live providers must be tested separately. A successful local reference is not evidence of cloud scale, speech quality or real connector effects.\n\n## Review before marking complete\n\nThe exercise includes staged hints, a full reference solution and diagnostic feedback. Compare after your own attempt. Practical submission is your own evidence report, not automated code inspection or certification.'})
        quizzes=[]
        def quiz(qid,prompt,right,wrongs,explanation):
            values=[right,*wrongs];shift=number%3;values=values[shift:]+values[:shift]
            return {'id':qid,'prompt':prompt,'options':[{'id':chr(97+i),'text':v} for i,v in enumerate(values)],'correct':chr(97+values.index(right)),'explanation':explanation}
        quizzes.append(quiz('case',case+' What is the defensible next decision?',decision,WRONGS[number-1],lab['reason']))
        quizzes.append(quiz('concept','Which definition describes '+terms[0][0]+'?',terms[0][1],[terms[1][1],terms[2][1]],'Keep '+terms[0][0]+' distinct from '+terms[1][0]+' and '+terms[2][0]+'. '+terms[0][1]))
        diagnostic,right,wrong1,wrong2=CHECKS[number-1]
        quizzes.append(quiz('boundary',diagnostic,right,[wrong1,wrong2],right+' '+lab['change']))
        for q in quizzes:
            if q['id']=='case':
                reasons={WRONGS[number-1][i]:reason for i,reason in enumerate(MISTAKES[number-1])}
                q['option_feedback']={o['id']:('This decision preserves the required boundary. '+decision if o['id']==q['correct'] else 'Why this choice fails: '+reasons[o['text']])+ '\n\nNext check: '+guide['trace'][0]+' Revisit the concept tutorial before retrying.' for o in q['options']}
            elif q['id']=='concept':
                q['option_feedback']={o['id']:('Correct: '+terms[0][1] if o['id']==q['correct'] else 'This describes '+next(t for t,d in terms if d==o['text'])+', rather than '+terms[0][0]+'.')+' '+guide['explanations'][0] for o in q['options']}
            else:
                boundary_reasons={CHECKS[number-1][i+2]:reason for i,reason in enumerate(BOUNDARY_MISTAKES[number-1])}
                q['option_feedback']={o['id']:('Correct: '+right if o['id']==q['correct'] else 'Why this choice fails: '+boundary_reasons[o['text']])+'\n\nReview: '+right+' Then compare your practice with the reference and inspect its assertions.' for o in q['options']}
        learning={'concepts':concepts,'questions':[
          {'id':'mechanism','prompt':'Trace the baseline from input through state changes to its assertions. Explain why each observation occurs.','guidance':'A strong explanation follows this causal sequence: '+' '.join(guide['trace'])+' It should name the checked variables, not just say the code passed.'},
          {'id':'transfer','prompt':guide['task'],'guidance':'Compare the complete practice reference after your attempt. '+guide['diagnosis']},
          {'id':'decision','prompt':case+' Explain your decision, evidence and remaining uncertainty.','guidance':decision+' '+guide['explanations'][2]}],
          'quiz':quizzes,'flashcards':[{'id':f'card-{i+1}','front':t,'back':d} for i,(t,d) in enumerate(terms)],'chapters':chapters,
          'exercise':{'steps':steps,'hint':guide['hints'][0],'hints':guide['hints'],'solution':solution,'material':material},
          'task':{'title':title+' — practical submission','deliverable':f'engineering-{number:02}-evidence.json plus implementation/test files','criteria':criteria}}
        learning['attribution']={'notice':(ROOT/'backend/academy/content/LICENSE.source').read_text(),'credit':'Academy-authored engineering curriculum and runnable examples. AI Engineering from Scratch informed topic coverage; its source notice is retained without requiring an external repository.','revision':'engineering-2026-10'}
        learning['revision']=hashlib.sha256(json.dumps(learning,sort_keys=True).encode()).hexdigest()
        content='# '+title+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in chapters)
        course['lessons'].append(dict(title=title,module=module,order=number-1,minutes=300 if number==end else 240,content=content,task='\n'.join(steps),source_id=f'academy-v2:ai-engineering-12-week:{number:02}',source_url='',content_hash=hashlib.sha256(content.encode()).hexdigest(),resources={'revision':'academy-course-books-v6','artifact':learning['task']['deliverable'],'checks':criteria,'capstone':outcome,'references':[],'learning':learning}))
    return course
