"""Build reviewed in-app books and exact executable references for 113 imported lessons.
Original source remains immutable in imported_curriculum.json; only targeted paths receive books.
"""
import hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
from imported_teaching.specs import SPECS
from imported_teaching.checkpoints import CHECKS
from imported_teaching import tutor,labs,refinements  # register and refine reviewed specimens
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from academy.pedagogy import module_contract
CONTENT=ROOT/'backend/academy/content'

def fence(kind,text): return '```'+kind+'\n'+text.strip()+'\n```'
def run(code):
    with tempfile.TemporaryDirectory(prefix='reviewed-course-') as folder:
        file=Path(folder)/'solution.py';file.write_text(code+'\n')
        result=subprocess.run([sys.executable,'-I',str(file)],cwd=folder,capture_output=True,text=True,timeout=20)
        if result.returncode: raise RuntimeError(result.stderr)
        return result.stdout.strip()
def chapter(id,title,body,kind='Concept teaching'):return dict(id=id,title=title,body=body,kind=kind)
def file_book(folder,names):
    return '\n\n'.join('### '+name+'\n\n'+fence('python' if name.endswith('.py') else 'text',(folder/name).read_text()) for name in names)
def supplement(key):
    if key in {'terminal-01','terminal-02'}:
        commands='''learning_dir="$(mktemp -d "${TMPDIR:-/tmp}/practical-tutor.XXXXXX")"
cd "$learning_dir"
pwd
mkdir exercises
printf '%s\\n' 'synthetic learning workspace' > exercises/README.txt
ls exercises
cat exercises/README.txt
command -v python3
python3 --version
if python3 -c 'raise SystemExit(2)'; then
  printf '%s\\n' 'Unexpected success'
else
  result=$?
  printf 'Observed exit status: %s\\n' "$result"
fi'''
        body='A real shell has a working directory, variables, exit status and persistent files. The academy command box is a stateless tutorial and does not create this workspace. Read each command, then run it in your own terminal.\n\n'+fence('bash',commands)+'\n\nExpected: pwd prints a newly created temporary learning folder; ls lists README.txt; cat prints synthetic learning workspace; Python prints its installed version; the deliberate failure reports exit status 2. mktemp creates a new directory each run. Quoting keeps spaces from splitting paths. The > operator writes inside this fresh folder. The if statement captures failure without claiming success. No application folder or account data is accessed. If python3 is missing, stop at environment setup; do not pretend the remaining commands ran.\n\nSave the complete Python specimen from this lesson in that workspace and run it as taught. No external coding agent or installation is required.'
        return chapter('real-shell','Real terminal: paths, files and exit codes',body,'Guided terminal practice')
    if key in {f'lesson-{i:02}' for i in range(23,30)}|{'lesson-51','lesson-52','lesson-55','lesson-57','lab-05','lab-06','lab-13','lab-14'}:
        folder=CONTENT/'accelerator_stack'
        files=['requirements.txt','Dockerfile','compose.yaml','database.py','api.py','tasks.py','alembic.ini','migrations/env.py','migrations/versions/001_documents.py','migrations/versions/002_parser_version.py','check.py']
        introduction,practice=(folder/'README.md').read_text().split('## Run the complete example',1)
        return chapter('complete-stack','Complete API, PostgreSQL and queue-worker case study',introduction+'\n\n## Every file used by this lab\n\n'+file_book(folder,files)+'\n\n## Run the complete example'+practice,'Complete integration and recovery')
    advanced=CONTENT/'starter/advanced';starter=CONTENT/'starter'
    if key in {'lesson-02','lesson-12','lesson-21','lesson-22','lab-01','lab-03'}:
        return chapter('complete-api','Complete FastAPI starter: files and run sequence',
        'This is the complete included lexical/fake API, not an omitted import or a production service. Create these files in a new folder, or use workspace/ from the program download. Python 3.12 is required. The exercise in the preceding chapter is independent and standard-library-only. This integration uses the starter dependency lock. It has no authentication or persistence: keep it local with synthetic data.\n\n'+
        file_book(starter,['pyproject.toml','app/__init__.py','app/main.py','app/schemas.py','app/service.py','app/retrieval.py','app/providers.py','data/policies.json','tests/test_baseline.py','evals/run_baseline.py','evals/baseline.jsonl'])+
        '\n\n### Run, then inspect real responses\n\nFrom the extracted workspace directory containing pyproject.toml and uv.lock, run:\n\n'+fence('bash','uv sync --locked --extra dev\nuv run pytest\nuv run python -m evals.run_baseline\nuv run uvicorn app.main:app --host 127.0.0.1 --port 8010')+
        '\n\nThe server remains in the foreground. In a second terminal, request http://127.0.0.1:8010/docs and try /health and the request shape shown in app/schemas.py. Compare the response with service.py and the tests. Stop this learner process with Ctrl-C. A health response proves this process responds; it does not establish production readiness. This API is independent of the academy on 8080 and Workshop on 8000. The lexical baseline may retrieve common-word matches: retain that defect in your retrieval report.\n\n### Read the code in order\n\n1. app/schemas.py bounds the transport input.\n2. app/main.py owns HTTP adaptation and injects the service.\n3. app/service.py orchestrates evidence and generation.\n4. app/retrieval.py performs lexical matching; providers.py contains an explicit fake.\n5. tests/test_baseline.py exercises the actual boundaries. The evaluation JSONL supplies separate labeled cases.\n\nExpected: pytest reports its actual passing count; the baseline report can expose known retrieval weaknesses. Do not rewrite expected labels to conceal them. A locked installation failure belongs to environment diagnosis, not model quality.', 'Complete integration')
    if key in {'lesson-61','lesson-62','lesson-63','lesson-64','lesson-65','lesson-66','lab-15'}:
        return chapter('sdk-integration','Complete reusable agent harness',
        'The complete agent below is a scripted, read-only baseline. Put both files in the same new folder. Use `python3 agent.py` for this multi-file example so its sibling policies.py is importable; reserve -I for the independent single-file specimens. No network or provider call occurs.\n\n'+file_book(advanced,['policies.py','agent.py'])+
        '\n\nExpected: status completed, citation policy-1 and a trace containing search then finish. Run with an unsupported topic and inspect the abstained status. Then try max_steps=1: the result is step_budget, with no completed answer. Search-before-finish, allowlisting and source membership are enforced by run, not by the adapter prompt. This synthetic corpus uses a 30-day policy; the separate 14-day specimens above intentionally use different fixtures.', 'Complete integration')
    if key in {'lesson-68','lesson-69','lesson-72','lab-16','lab-17'}:
        return chapter('sdk-integration','Complete LangGraph workflow and checkpoint example',
        'These are complete files, with explicit dependencies. Use the downloaded starter/advanced folder or recreate the files below in a new directory. The SDK versions are the pinned course snapshot; this is not a claim about newest releases.\n\n'+file_book(advanced,['requirements.txt','policies.py','graph.py'])+
        '\n\n'+fence('bash','python3.12 -m venv .venv\n. .venv/bin/activate\npython -m pip install -r requirements.txt\npython graph.py')+
        '\n\nRead the data path: initial creates empty evidence and attempts=0; retrieve attaches source results; draft intentionally emits a bad first answer; verify compares against the exact fixture; repair clears the bad-draft flag; the second draft is accepted. Expected attempts=2, verdict=accepted, and one repair in trace. Change the question to unicorn vacation: the empty evidence path must abstain. get_state inspects the same thread in the same process. InMemorySaver does not survive process restart; use the earlier file-checkpoint exercise to learn durable serialization. It is not a shared multi-worker store. The pure routing specimen distinguishes retry exhaustion from acceptance even though both can end graph execution.', 'Complete SDK integration')
    if key in {f'lesson-{i:02}' for i in range(79,85)}|{'lab-19','lab-20'}:
        return chapter('sdk-integration','Complete MCP server, client and observed checks',
        'Study the application contract first, then these complete SDK files. They run a real local subprocess and require no model account. Use a fresh directory with Python 3.12. The dependency snapshot is pinned, and network access is needed to install its packages. These SDK examples are separate from the pure Python dispatch specimens above.\n\n'+file_book(advanced,['requirements.txt','policies.py','mcp_server.py','mcp_client.py'])+
        '\n\n'+fence('bash','python3.12 -m venv .venv\n. .venv/bin/activate\npython -m pip install -r requirements.txt\npython mcp_client.py')+
        '\n\n### Follow the actual protocol sequence\n\n1. StdioServerParameters points to the local Python interpreter and server file.\n2. The async Client context launches and initializes the child.\n3. list_tools verifies the exposed read-only capability before call_tool.\n4. The successful call must contain policy-1 and its 30-day text; the resource read checks the same fixture.\n5. An empty query must return isError; error content must not become evidence.\n6. The context closes the server process. The printed negotiated version is an observation from your installed snapshot.\n\nExpected messages include Policy call: PASS; resource read: PASS; invalid query: rejected and Server subprocess closed. If discovery fails, inspect SDK versions and stderr before changing the tool contract. The client has a 20-second total exercise deadline. This does not test remote HTTP authentication, every cancellation race, or malicious model behavior. The read-only synthetic server has no user database or secret access.', 'Complete SDK integration')
    return None

def build():
    originals=json.loads((CONTENT/'imported_curriculum.json').read_text());reviewed=[];report=[]
    expected={l['source_id'] for p in originals[-2:] for l in p['lessons']}
    assert expected==set(SPECS),(expected-set(SPECS),set(SPECS)-expected)
    assert expected==set(CHECKS),expected-set(CHECKS)
    output=CONTENT/'reviewed_examples';output.mkdir(exist_ok=True)
    for program in originals[-2:]:
        result={k:v for k,v in program.items() if k!='lessons'};result['lessons']=[]
        for original in program['lessons']:
            row=json.loads(json.dumps(original));key=row['source_id'];s=SPECS[key]
            if 'title' in s: row['title']=s['title']
            contract=module_contract(program['slug'],row['module'])
            code=s['code']+'\n';solution=code+'\n# Bounded exercise variation\n'+s['patch']+'\nprint("Exercise variation: PASS")\n'
            try: baseline_output=run(code);solution_output=run(solution)
            except Exception as error: raise RuntimeError(key+' '+str(error)) from error
            (output/(key+'.py')).write_text(solution)
            first=s['explanation'].split('. ',1)[0]+'.'
            boundary=s['diagnosis'].split('. ',1)[0]+'.'
            concepts=[{'term':s['term'],'definition':first},{'term':'Verification boundary','definition':boundary}]
            original_intro=''
            if key.startswith('lesson-') and int(key[-2:])<=60:
                parts=original['content'].split('## What you will learn',1)
                if len(parts)==2:original_intro=parts[1].split('In our capstone,',1)[0].strip()
            tutorial='## Step 1 · '+s['term']+'\n\n'+s['explanation']+('\n\n### Capstone application\n\n'+original_intro if original_intro else '')+'\n\n## Step 2 · Trace the mechanism\n\n'+s['trace']+'\n\n## Step 3 · Verification boundary\n\n'+s['diagnosis']
            pillars='## Apply all three engineering pillars\n\n'+'\n\n'.join('### '+p['name']+'\n\n'+p['application'] for p in contract['pillars'])+'\n\n### Production boundary\n\n'+contract['operations']+'\n\n'+contract['evaluation_note']+'\n\nFor this lesson specifically: '+s['diagnosis']
            setup='Use Python 3.12. Create a new scratch folder and save the entire block as `lesson.py`. Run `python3 -I lesson.py` with assertions enabled. All imports and fixtures are included; no model key is required. The code uses only the standard library. Examples create temporary resources and close them. The academy records your self-reported work; it does not execute this file for you.'
            worked=setup+'\n\n## Predict before running\n\n'+s['trace']+'\n\n'+fence('python',code)+'\n\n## Expected output\n\n'+fence('text',baseline_output)+'\n\n## Interpret the result\n\n'+s['diagnosis']
            criteria=[s['task'],'The original positive and negative assertions remain enabled and pass; actual output is recorded.','The report distinguishes observed local behavior from untested provider, protocol or production claims.','The three-pillar note records latency/cost/quality, an automated invariant and a scoped context/cache decision; unmeasured values are labeled unknown.']
            task='## Your bounded exercise\n\n'+s['task']+'\n\nStart from the complete lesson.py above. Change or extend it in your own copy before revealing the reference. Keep the baseline assertions; add a positive and counterexample check for the variation.\n\n## Acceptance\n\n'+'\n'.join('- '+c for c in criteria)+'\n\n## Explain before moving on\n\nWhich boundary does the changed test protect? What output did you observe? Which larger claim would still require a different integration test?\n\n'+s['diagnosis']
            reference=setup.replace('lesson.py','solution.py')+'\n\n'+fence('python',solution)+'\n\n## Expected output from this exact reference\n\n'+fence('text',solution_output)+'\n\n## Diagnose a difference\n\n'+s['diagnosis']
            chapters=[chapter('orientation','Goal, prerequisites and study sequence','This session teaches **'+s['term']+'** in '+program['title']+'.\n\nPrerequisites: Python variables, functions, lists and dictionaries. Imports are explained by their purpose in the walkthrough; framework code, where present, has a separate setup chapter. If syntax is unfamiliar, use Terminal Tutor guides 3–5 first.\n\nRead the concept tutorial, predict and run the complete specimen, study the three-pillar boundary, then attempt the bounded exercise. Quiz explanations and reference solutions follow your attempt. Marking a lesson complete does not certify a deployed system.\n\nThe specimen is synthetic. Preserve its stated assumptions and compare them with your own artifact before making claims.'),chapter('concept-tutorial','Learn each concept step by step',tutorial),chapter('worked-implementation','Complete example: predict, run, interpret',worked,'Worked implementation'),chapter('engineering-principles','Trade-offs, evaluation and context',pillars)]
            extra=supplement(key)
            if extra:chapters.append(extra)
            chapters.append(chapter('case-study','Practice the taught boundary',task,'Aligned practice'))
            quiz=[]
            applied=CHECKS[key]
            prompts=[('mechanism',applied[0],applied[1]),('boundary','Which limitation must remain in your interpretation of this lesson?',[(s['diagnosis'],'Correct. '+s['diagnosis']),('Passing this specimen proves all related failures are handled in production.','A bounded fixture cannot establish every deployed behavior. '+s['diagnosis']),('A successful example makes its counterexample and failure checks unnecessary.','Counterexamples expose the boundary the lesson protects. '+s['trace']+' '+s['diagnosis'])])]
            for index,(id,prompt,choices) in enumerate(prompts):
                shift=int(hashlib.sha256((key+id).encode()).hexdigest()[:4],16)%3
                rotated=list(enumerate(choices));rotated=rotated[shift:]+rotated[:shift]
                options=[];feedback={};correct=None
                for label,(original_index,(text,reason)) in zip('abc',rotated):
                    options.append(dict(id=label,text=text));feedback[label]=reason
                    if original_index==0:correct=label
                quiz.append(dict(id=id,prompt=prompt,options=options,correct=correct,explanation=feedback[correct],option_feedback=feedback))
            learning=dict(chapters=chapters,concepts=concepts,
              questions=[dict(id='trace',prompt='Predict and explain the mechanism before running it: '+s['term']+'. What changes and what remains protected?',guidance=s['trace']),dict(id='diagnosis',prompt=s['task'],guidance=s['diagnosis']+' Compare with the exact runnable reference after your own attempt.'),dict(id='transfer',prompt='Apply the three pillars to this lesson. Which measured comparison, invariant and context/cache boundary would you record?',guidance=' '.join(p['application'] for p in contract['pillars']))],
              flashcards=[dict(id='mechanism',front=s['term']+' — explain the mechanism before revealing.',back=s['explanation']),dict(id='failure',front='Which evidence boundary does this example leave unverified?',back=s['diagnosis']),dict(id='practice',front='Recall the bounded variation and its acceptance condition.',back=s['task'])],
              quiz=quiz,exercise=dict(steps=['Read the concept tutorial and predict the data path.','Run the complete specimen in a fresh scratch directory and retain its assertions.',s['task'],'Record observed output, inspect counterexamples, then compare the full reference and diagnosis.'],hint='Start with the input and boundary: '+s['trace'],hints=['Trace the original values first: '+s['trace'],'Keep the acceptance invariant while making this change: '+s['task'],'Inspect this specific failure: '+s['diagnosis']],material=task,solution=reference),task=dict(title=row['title'],deliverable=key+'/lesson.py + observed-results.md',criteria=criteria))
            learning['attribution']={'credit':'Academy-authored teaching and reviewed runnable specimens; original imported curriculum retained separately for provenance. Source notices are included in the program kit.','revision':original['content_hash'],'notice':(CONTENT/'LICENSE.accelerator').read_text() if program['slug']=='genai-accelerator' else (CONTENT/'LICENSE.source').read_text()}
            learning['revision']=hashlib.sha256(json.dumps(learning,sort_keys=True).encode()).hexdigest()
            resources={**row['resources'],'learning':learning,'reviewed_source_hash':original['content_hash']}
            row.update(resources=resources,content='# '+row['title']+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in chapters),task=s['task'],minutes=max(row['minutes'],45))
            row['content_hash']=hashlib.sha256(row['content'].encode()).hexdigest()
            result['lessons'].append(row);report.append(dict(id=key,title=row['title'],chapters=len(chapters),reference_executed=True,stdout=solution_output,revision=learning['revision']))
        reviewed.append(result)
    from progression import apply as apply_progression
    apply_progression(reviewed)
    from capstone_books import apply as apply_capstones
    apply_capstones(reviewed)
    for p in reviewed:
        for row in p['lessons']:
            record=next(r for r in report if r['id']==row['source_id'])
            record.update(chapters=len(row['resources']['learning']['chapters']),revision=row['resources']['learning']['revision'])
    history_path=CONTENT/'imported_teaching_history.json'
    history=json.loads(history_path.read_text()) if history_path.exists() else {}
    for p in reviewed:
        for row in p['lessons']:
            known=history.setdefault(row['source_id'],dict(content=[],learning=[],fields={}))
            for field,value in [('content',row['content_hash']),('learning',row['resources']['learning']['revision'])]:
                if value not in known[field]:known[field].append(value)
            for field in ['task','title','module','minutes']:
                values=known['fields'].setdefault(field,[])
                if row[field] not in values:values.append(row[field])
    history_path.write_text(json.dumps(history,indent=2))
    (CONTENT/'reviewed_workshop.json').write_text(json.dumps(reviewed,ensure_ascii=False))
    (ROOT/'docs/imported-student-review.json').write_text(json.dumps(dict(lessons=len(report),chapters=sum(r['chapters'] for r in report),specimens=report),indent=2))
    print(f'Reviewed {len(report)} lessons; {sum(r["chapters"] for r in report)} chapters; {len(report)*2} executed baseline/reference files.')
if __name__=='__main__':build()
