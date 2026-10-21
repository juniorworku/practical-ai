"""Execute exactly the code a learner sees, including complete exercise variations."""
import ast,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
programs=json.loads((ROOT/'backend/academy/content/reviewed_workshop.json').read_text())
rows=[]
for program in programs:
    for lesson in program['lessons']:
        learning=lesson['resources']['learning'];key=lesson['source_id']
        ids=[c['id'] for c in learning['chapters']]
        assert ids.index('concept-tutorial')<ids.index('worked-implementation')<ids.index('case-study'),key
        baseline=next(c for c in learning['chapters'] if c['id']=='worked-implementation')['body']
        for kind,material in [('baseline',baseline),('reference',learning['exercise']['solution'])]:
            code=re.findall(r'```python\n(.*?)```',material,re.S)
            expected=re.findall(r'```text\n(.*?)```',material,re.S)
            assert len(code)==len(expected)==1,(key,kind)
            tree=ast.parse(code[0]);assert any(isinstance(node,ast.Assert) for node in ast.walk(tree))
            assert 'assert True' not in code[0] and '...' not in code[0],key
            with tempfile.TemporaryDirectory(prefix='student-exact-example-') as folder:
                path=Path(folder)/'lesson.py';path.write_text(code[0])
                result=subprocess.run([sys.executable,'-I',str(path)],cwd=folder,text=True,capture_output=True,timeout=20)
                assert result.returncode==0,(key,kind,result.stderr)
                assert result.stdout.strip()==expected[0].strip(),(key,kind,result.stdout,expected)
            if kind=='reference':assert code[0]==(ROOT/'backend/academy/content/reviewed_examples'/f'{key}.py').read_text(),key
        assert lesson['task'] in learning['exercise']['material'],key
        assert len(learning['exercise']['hints'])==3 and all(q.get('guidance') for q in learning['questions'])
        assert all(set(q['option_feedback'])=={o['id'] for o in q['options']} for q in learning['quiz'])
        assert all('](https://github.com/' not in chapter['body'] for chapter in learning['chapters'])
        rows.append({'id':key,'examples_executed':2,'chapters':len(ids),'quiz_choices_checked':sum(len(q['options']) for q in learning['quiz'])})
assert len(rows)==113
report={'student_lessons':113,'exact_examples_executed':226,'chapters':sum(r['chapters'] for r in rows),'lesson_checks':rows}
(ROOT/'docs/imported-teaching-audit.json').write_text(json.dumps(report,indent=2))
print(f'PASS: {len(rows)} lessons, 226 exact published example/reference executions, {report["chapters"]} teaching chapters; aligned tasks, staged hints, reflection guidance and per-choice feedback.')
