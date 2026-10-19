"""Execute what the student sees, not a hidden reference implementation.
Run with Python 3.12; reads active generated books, creates isolated scratch dirs.
"""
import ast, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def check(data):
    executed=[]
    for prefix,program in zip('BWF',data):
        for index,lesson in enumerate(program['lessons'],1):
            key=f'{prefix}{index:02}'
            learning=lesson['resources']['learning']
            body=lesson['content']; material=learning['exercise']['material']
            assert 'downloadable' not in body and 'code/main.py' not in body, key
            assert 'the related topic' not in body and '](https://github.com' not in body, key
            assert '## Before you begin' in body, key
            assert all(c in material for c in lesson['resources']['checks']), key
            assert all(s in material for s in learning['exercise']['steps']), key
            assert all(c['definition'] in body for c in learning['concepts']), key
            assert len(learning['questions'])==3 and len(learning['quiz'])==3, key
            for question in learning['quiz']:
                assert question['correct'] in {o['id'] for o in question['options']}, key
                assert len({o['text'] for o in question['options']})==len(question['options']), key
            for code in re.findall(r'^```python\n(.*?)^```',body,re.M|re.S):
                ast.parse(code,filename=key)
                assert 'NotImplementedError' not in code and '>>>' not in code, key
            if prefix=='F':
                assert any(c['kind']=='Complete worked artifact' for c in learning['chapters']), key
                continue
            chapter=next(c for c in learning['chapters'] if c['id']=='worked-implementation')
            if key=='B19':
                assert all('### '+name in chapter['body'] for name in ['compose.yaml','backend/app.py','frontend/index.html']),key
                continue # Its full multi-file Docker experiment has a separate observed test.
            codes=re.findall(r'^```python\n(.*?)^```',chapter['body'],re.M|re.S)
            assert len(codes)==1,key
            expected=re.search(r'## Expected observation\s+```text\n(.*?)\n```',chapter['body'],re.S)[1]
            with tempfile.TemporaryDirectory(prefix='student-audit-') as scratch:
                file=Path(scratch)/'example.py';file.write_text(codes[0])
                run=subprocess.run([sys.executable,'-I',str(file)],cwd=scratch,capture_output=True,text=True,timeout=10)
                assert run.returncode==0, (key,run.stderr)
                assert run.stdout.strip()==expected.strip(), (key,run.stdout,expected)
            executed.append(key)
    assert len(executed)==41
    # Recalculate the published fictional client's assumptions, including the
    # adverse case that flips the recommendation and the support-capacity load.
    f=data[2]['lessons']
    scenarios=[(10,.20,90),(14,.30,-130),(8,.10,230)]
    for review,exceptions,expected in scenarios:
        observed=40*(20-4-review-exceptions*15)-30
        assert observed==expected
        assert str(expected) in f[2]['content'].replace('−','-')
    assert 44*1.2==52.8 and 3*4*(45+30)/60==15
    assert '52.8' in f[5]['content'] and '15 support hours' in f[5]['content']
    print(f'PASS: all 60 lessons aligned; 41 exact published Python examples executed; Docker lab has separate verification; client arithmetic reconciled.')

if __name__=='__main__': check(json.loads((ROOT/'backend/academy/starter_curriculum.json').read_text()))
