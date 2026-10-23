"""Student build: execute the published teaching, solutions and self-contained project."""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
course=next(p for p in json.loads((ROOT/'backend/academy/starter_curriculum.json').read_text()) if p['slug']=='python-for-ai')
assert len(course['lessons'])==12
prompts=[]

def run(command,cwd):
    result=subprocess.run([sys.executable,*command],cwd=cwd,text=True,capture_output=True,timeout=90,
                          env={**os.environ,'RUN_LIVE_MODEL':'0','STATE_PATH':'state/cache.sqlite3'})
    assert result.returncode==0,(command,result.stdout[-2000:],result.stderr[-4000:])
    return result

def blocks(body):return re.findall(r'```python\n(.*?)\n```',body,re.S)

with tempfile.TemporaryDirectory() as temporary:
    scratch=Path(temporary)
    for number,lesson in enumerate(course['lessons'],1):
        learning=lesson['resources']['learning']
        assert len(learning['chapters'])>=6 and len(learning['quiz'])==5 and len(learning['flashcards'])==5
        ids=[chapter['id'] for chapter in learning['chapters']]
        assert ids.index('advanced-studio')<ids.index('practice')
        assert 'Required advanced studio evidence' in learning['exercise']['material']
        for q in learning['quiz']:
            assert q['correct'] in {choice['id'] for choice in q['options']}
            assert set(q['option_feedback'])=={choice['id'] for choice in q['options']}
            assert q['review_chapter'] in ids
            prompts.append(q['prompt'])
        publications=[]
        for chapter in learning['chapters']:
            if chapter['id'] in {'worked-implementation','advanced-studio','real-provider'}:
                publications.extend((chapter['id'],code) for code in blocks(chapter['body']))
        publications.extend(('reference',code) for code in blocks(learning['exercise']['solution']))
        for index,(kind,code) in enumerate(publications):
            path=scratch/f'lesson-{number}-{kind}-{index}.py';path.write_text(code)
            run(['-I',str(path)],scratch)
        print(f'PASS session {number}: {len(publications)} published examples/solutions, aligned studio and five question contracts',flush=True)
    assert len(prompts)==len(set(prompts))==60
    chapter=next(c for c in course['lessons'][-1]['resources']['learning']['chapters'] if c['id']=='capstone-build')
    files=re.findall(r'^### ([\w.-]+)\n\n```(?:python|text)\n(.*?)\n```',chapter['body'].split('## Save every project file',1)[1],re.M|re.S)
    expected={'.dockerignore','Dockerfile','pipeline.py','server.py','evaluate.py','probe.py','test_pipeline.py','test_http.py','test_evaluate.py','requirements.txt'}
    assert {name for name,_ in files}==expected
    project=scratch/'student-project';project.mkdir()
    for name,body in files:
        assert body.strip()==(ROOT/'backend/academy/content/capstones/python-for-ai'/name).read_text().strip(),name
        (project/name).write_text(body+'\n')
    readme_examples=blocks(chapter['body'].split('## Save every project file',1)[0])
    assert len(readme_examples)==1
    (project/'restore_check.py').write_text(readme_examples[0])
    run(['restore_check.py'],project)
    result=run(['-m','unittest','discover','-v'],project)
    print(result.stderr,flush=True)
    run(['evaluate.py','--repeats','20','--output','evaluation-observed.json'],project)
    report=json.loads((project/'evaluation-observed.json').read_text())
    assert report['gate_passed'] and report['observations']==120 and not report['critical_failures']
    assert report['cost_per_accepted_result'] is None
    print('PASS complete student project reconstructed from lesson text; 120 actual local fixture observations and all project tests passed',flush=True)
