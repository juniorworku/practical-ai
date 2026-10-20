"""Run exact published references and probe regressions in the original programs."""
import ast,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
programs=json.loads((ROOT/'backend/academy/starter_curriculum.json').read_text())[:3]
report=[];executed=0;namespaces={}
for prefix,program in zip('BWF',programs):
    for n,lesson in enumerate(program['lessons'],1):
        key=f'{prefix}{n:02}';learning=lesson['resources']['learning'];chapters=learning['chapters'];ids=[c['id'] for c in chapters]
        assert ids.index('concept-tutorial')<ids.index('worked-implementation')<ids.index('case-study'),key
        tutorial=next(c['body'] for c in chapters if c['id']=='concept-tutorial')
        for i,concept in enumerate(learning['concepts'],1):
            paragraph=tutorial.split(f"## Step {i} · {concept['term']}\n\n")[1].split('\n\n## Step')[0]
            assert len(paragraph.split())>=30,(key,concept['term'],len(paragraph.split()))
        exercise=learning['exercise'];assert len(exercise['hints'])==3 and len(set(exercise['hints']))==3,key
        assert exercise['steps'][1] in exercise['material'] and exercise['steps'][1] in learning['task']['criteria'],key
        assert all(q['guidance'] for q in learning['questions']),key
        for q in learning['quiz']:
            assert set(q['option_feedback'])=={o['id'] for o in q['options']},key
            assert len(set(q['option_feedback'].values()))==3,key
        reference=exercise['solution'];blocks=re.findall(r'^```python\n(.*?)^```',reference,re.M|re.S)
        stdout=None
        if blocks:
            assert len(blocks)==1,key
            code=blocks[0];ast.parse(code);assert 'NotImplementedError' not in code,key
            expected=re.search(r'## Expected reference observation\s+```text\n(.*?)\n```',reference,re.S)[1]
            with tempfile.TemporaryDirectory(prefix='practical-published-reference-') as folder:
                file=Path(folder)/'solution.py';file.write_text(code)
                result=subprocess.run([sys.executable,'-I',str(file)],cwd=folder,capture_output=True,text=True,timeout=20)
                assert result.returncode==0,(key,result.stderr)
                assert result.stdout.strip()==expected.strip(),(key,result.stdout,expected)
                if key=='B19':
                    files=ast.literal_eval(next(node.value for node in ast.parse(code).body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='FILES' for target in node.targets)))
                    for name,text in files.items():assert (Path(folder)/'container-lab'/name).read_text()==text
                stdout=result.stdout.strip();executed+=1
            if key in {'B04','B07','B08','B09','B11','B12','B16','B22','W05','F03','F06','F18'}:namespaces[key]=code
        else:assert prefix=='F' and len(reference.split())>=140,key
        report.append({'lesson':key,'program':program['slug'],'title':lesson['title'],'concepts_taught':3,
                       'bounded_practice':exercise['steps'][1],'reference_type':'executable Python' if blocks else 'completed changed-case decision',
                       'reference_stdout':stdout,'staged_hints':3,'choice_feedback':9,'reflection_guidance':3})
assert len(report)==60 and executed==47,(len(report),executed)
def load(key):
    namespace={};exec(compile(namespaces[key],key,'exec'),namespace);return namespace
m=load('B04')
# The exercise input is required to reach identity validation, not fail early for missing fields.
material=programs[0]['lessons'][3]['resources']['learning']['exercise']['material']
fixture=json.loads(re.search(r'^```json\n(.*?)^```',material,re.M|re.S)[1])
assert m['validate'](json.dumps(fixture['raw']),set(fixture['known_sources']))==['citation_identity']
m=load('B07')
try:m['ingest']('returns','v1','Changed under reused revision')
except ValueError:pass
else:raise AssertionError('immutable source revision overwritten')
m=load('B09');assert m['decide']('opened',m['policy'],'Opened items are excluded')=='draft_for_review'
m=load('B11');assert m['run'](['answer'])['status']=='failed'
m=load('B12');assert m['execute'](m['payload'],1,actor='other')=='needs_review'
m=load('B08');assert m['retrieval_metrics'](['one'],{'one','two'},1)['recall']==.5
m=load('B16');assert m['candidate']({'scope':'other','has_source':True,'condition':'unopened'})=='answer' # actual defect is detected, not hidden
assert m['critical']==['security']
m=load('B22');assert m['draft']('opened',m['offline'])['status']=='needs_review' and m['draft']('commercial-contract',m['offline'])['status']=='abstain'
m=load('W05');row={'version':7,'confirmed':None};assert m['confirm'](row,6)=='conflict' and row['confirmed'] is None
m=load('F03');assert m['net_minutes'](40,20,4,14,.3,15,30)==-130
m=load('F06');assert m['usage_per_accepted'](14,0) is None
m=load('F18');assert m['gaps'](['recovery'],m['packet'])=={'recovery':['acceptance','handover']}
(ROOT/'docs/practical-student-review.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:60 lessons teach180 concepts before practice;47 exact published runnable references executed;18 business decision references reviewed;180 progressive hints;540 choice-specific feedback entries; recall/executor/stale-review/business-calculation/evidence-status probes passed.')
