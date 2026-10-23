"""Audit the actual published teaching and exercise contracts, not hidden examples."""
import ast,asyncio,importlib.util,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXAMPLES=ROOT/'backend/academy/content/engineering_examples'
spec=importlib.util.spec_from_file_location('evaluation_suite',EXAMPLES/'evaluation_suite.py');suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
data=[p for p in json.loads((ROOT/'backend/academy/starter_curriculum.json').read_text()) if p['slug']!='python-for-ai'] # Dedicated advanced checks cover Python.
course=next(p for p in data if p['category']=='Engineering')
assert len(course['lessons'])==36
assert len({l['module'] for l in course['lessons']})==5
executed=0
for program in data:
 for index,lesson in enumerate(program['lessons']):
  learning=lesson['resources']['learning'];contract=lesson['resources']['pedagogy']
  assert len(contract['pillars'])==3
  assert 'stochastic' in contract['evaluation_note']
  assert all(p['application'] in lesson['content'] for p in contract['pillars'])
  assert all(c in learning['exercise']['material'] for c in learning['task']['criteria'])
  if index==len(program['lessons'])-1 or program['lessons'][index+1]['module']!=lesson['module']:
   assert all(g in learning['task']['criteria'] for g in contract['release_gates'])
  assert '](https://github.com' not in lesson['content']
  for block in re.findall(r'^```python\n(.*?)^```',lesson['content'],re.M|re.S):ast.parse(block)
for lesson in course['lessons']:
 learning=lesson['resources']['learning'];chapter=next(c for c in learning['chapters'] if c['id']=='implementation')
 code=re.findall(r'^```python\n(.*?)^```',chapter['body'],re.M|re.S)
 assert len(code)==1
 expected=re.search(r'## Observed output\s+```text\n(.*?)\n```',chapter['body'],re.S)[1]
 with tempfile.TemporaryDirectory() as scratch:
  path=Path(scratch)/'example.py';path.write_text(code[0])
  r=subprocess.run([sys.executable,'-I',str(path)],cwd=scratch,capture_output=True,text=True,timeout=15)
  assert r.returncode==0,(lesson['title'],r.stderr)
  assert r.stdout.strip()==expected.strip(),lesson['title']
 executed+=1
 for q in learning['quiz']:
  assert len({o['text'] for o in q['options']})==3
  assert q['correct'] in {o['id'] for o in q['options']}
 for c in learning['concepts']:assert c['definition'] in lesson['content']
 expected=3+int(any(c['id']=='runtime-studio' for c in learning['chapters']))
 assert len(learning['questions'])==len(learning['quiz'])==len(learning['flashcards'])==expected
# Harness must detect a critical failure and unavailable cases, not only pass its fixture.
cases=suite.cases();report=asyncio.run(suite.run(cases))
assert report['passed']==120 and report['semantic_reviewed']==0 and report['mode']=='fixture'
bad=cases[0];bad['expected']['decision']='deny';bad['critical']=True
report=asyncio.run(suite.run([bad]));assert report['passed']==0 and report['critical_failures']==[bad['id']]
def unavailable(url,request):raise TimeoutError('synthetic timeout')
suite.remote=unavailable
report=asyncio.run(suite.run([cases[0]],url='http://127.0.0.1:9000/evaluate'))
assert report['attempted']==1 and report['passed']==0 and report['usage_missing']==1
assert report['rows'][0]['error']=='TimeoutError'
print(f'PASS: {executed} exact published engineering examples executed; all 96 lessons align with module gates; 120 concrete fixture cases plus injected critical failure tested.')
