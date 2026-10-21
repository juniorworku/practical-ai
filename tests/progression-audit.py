"""Check published paths for forward prerequisites and orphan capstone requirements."""
import hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
programs=json.loads((ROOT/'backend/academy/starter_curriculum.json').read_text())+json.loads((ROOT/'backend/academy/content/reviewed_workshop.json').read_text())
report=[]
for program in programs:
    rows=program['lessons'];positions={r['source_id']:i for i,r in enumerate(rows)};checkpoints=[]
    assert len(positions)==len(rows)
    for i,row in enumerate(rows):
        learning=row['resources']['learning'];path=learning['progression']
        assert path['position']==i+1
        assert learning['chapters'][0]['id']=='progression'
        assert path['entry'] and path['stage_artifact']
        for prerequisite in path['prerequisites']:
            assert positions[prerequisite['source_id']]<i,(program['slug'],row['title'],prerequisite)
        for requirement in path['coverage']:
            assert requirement['requirement'] and requirement['sources']
            for source in requirement['sources']:
                assert source in positions and positions[source]<i,(row['source_id'],source)
                prior=rows[positions[source]]['resources']['learning']
                assert prior['exercise']['solution'] and prior['concepts']
        if path['coverage']:
            assert any('Project evidence traces' in criterion for criterion in learning['task']['criteria'])
            assert 'Integrated project requirement' in learning['exercise']['material']
            checkpoints.append({'source_id':row['source_id'],'title':row['title'],'coverage':path['coverage']})
        fingerprint=hashlib.sha256(json.dumps({k:v for k,v in learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()
        assert learning['revision']==fingerprint
    report.append({'program':program['slug'],'sessions':len(rows),'checkpoints':checkpoints})
accelerator=next(p for p in programs if p['slug']=='genai-accelerator')
sequence=[l['source_id'] for l in accelerator['lessons']]
assert sequence.index('lesson-05')<sequence.index('lab-01')<sequence.index('lesson-06')
assert sequence.index('lesson-66')<sequence.index('lesson-85')<sequence.index('lab-15')<sequence.index('lesson-67')
assert sequence.index('lesson-79')<sequence.index('lesson-30')<sequence.index('lesson-80')
assert sequence.index('lesson-84')<sequence.index('lab-20')
# Outline groups must not undo the sequence by pulling later content forward.
groups=list(dict.fromkeys(l['module'] for l in accelerator['lessons']))
assert [l['source_id'] for module in groups for l in accelerator['lessons'] if l['module']==module]==sequence
terminal=next(p for p in programs if p['slug']=='terminal-tutor')['lessons'][0]
bootstrap=next(c for c in terminal['resources']['learning']['chapters'] if c['id']=='python-onramp')
code=re.search(r'```python\n(.*?)```',bootstrap['body'],re.S)[1]
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'basics.py';path.write_text(code)
    completed=subprocess.run([sys.executable,'-I',str(path)],text=True,capture_output=True,check=True)
    assert completed.stdout.strip()=='p1; two sources; assertions passed'
    path.write_text(code.replace('assert len(ids) == 2','assert len(ids) == 3'))
    failed=subprocess.run([sys.executable,'-I',str(path)],capture_output=True,text=True)
    assert failed.returncode!=0 and 'AssertionError' in failed.stderr
(ROOT/'docs/progression-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(programs)} independent paths, {sum(len(p["lessons"]) for p in programs)} sessions, {sum(len(r["checkpoints"]) for r in report)} mapped checkpoints; no forward dependencies, interleaved labs match outline order, bootstrap positive and negative runs verified.')
