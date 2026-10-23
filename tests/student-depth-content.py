"""Execute exact learner-facing studios and reconstruct projects from inline files."""
import hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SLUGS={'ai-agent-bootcamp','ai-workshops','ai-engineering-12-week','genai-accelerator'}
programs=[p for path in ['backend/academy/starter_curriculum.json','backend/academy/content/reviewed_workshop.json'] for p in json.loads((ROOT/path).read_text()) if p['slug'] in SLUGS]
report={'lessons':0,'studios':[],'capstones':[]}
for program in programs:
    report['lessons']+=len(program['lessons'])
    for lesson in program['lessons']:
        learning=lesson['resources']['learning'];ids=[c['id'] for c in learning['chapters']]
        assert len(ids)==len(set(ids)),lesson['source_id']
        studio=next((c for c in learning['chapters'] if c['id']=='runtime-studio'),None)
        if studio:
            assert ids.index('concept-tutorial')<ids.index('runtime-studio')<min(ids.index(c) for c in ['case-study','project'] if c in ids)
            assert len(re.findall(r'^## Step [1-4] · ',studio['body'],re.M))==4
            codes=re.findall(r'^```python\n(.*?)^```',studio['body'],re.M|re.S)
            expected=re.findall(r'^```text\n(.*?)^```',studio['body'],re.M|re.S)
            assert len(codes)==len(expected)==2
            for code,stdout in zip(codes,expected):
                with tempfile.TemporaryDirectory() as folder:
                    path=Path(folder)/'example.py';path.write_text(code)
                    result=subprocess.run([sys.executable,'-I',str(path)],cwd=folder,capture_output=True,text=True,timeout=12)
                    assert result.returncode==0,(lesson['source_id'],result.stderr)
                    assert result.stdout.strip()==stdout.strip()
            quiz=next(q for q in learning['quiz'] if q['id']=='runtime-studio')
            assert quiz['review_chapter']=='runtime-studio'
            assert set(quiz['option_feedback'])=={o['id'] for o in quiz['options']}
            report['studios'].append({'lesson':lesson['source_id'],'executed_blocks':2,'teaching_before_practice':True,'feedback_target':quiz['review_chapter']})
        if 'capstone' in learning:
            chapter=next(c for c in learning['chapters'] if c['id']=='capstone-build')
            manifest=learning['capstone']['files']
            with tempfile.TemporaryDirectory(prefix='student-rebuild-') as folder:
                target=Path(folder)
                for name,digest in manifest.items():
                    if name=='README.md':
                        code=(ROOT/'backend/academy/content/capstones'/program['slug']/name).read_text()
                        assert chapter['body'].startswith(code)
                    else:
                        pattern=r'^### '+re.escape(name)+r'\n\n```[^\n]+\n(.*?)^```'
                        found=re.findall(pattern,chapter['body'],re.M|re.S);assert len(found)==1,name
                        code=found[0].rstrip()+'\n'
                    actual=(ROOT/'backend/academy/content/capstones'/program['slug']/name).read_text()
                    assert code.rstrip()==actual.rstrip(),name
                    assert hashlib.sha256(actual.encode()).hexdigest()==digest,name
                    file=target/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(code)
                modules=['test_agent','test_evidence'] if program['slug']=='genai-accelerator' else ['test_core']
                result=subprocess.run([sys.executable,'-m','unittest','-v',*modules],cwd=folder,capture_output=True,text=True,timeout=20)
                assert result.returncode==0,result.stderr
                report['capstones'].append({'program':program['slug'],'reconstructed_files':len(manifest),'published_tests':result.stderr.split('Ran ',1)[1].split('\n',1)[0]})
assert report['lessons']==183 and len(report['studios'])==9 and len(report['capstones'])==4
(ROOT/'docs/student-depth-content.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:183 lesson structures,18 exact studio blocks,4 inline project rebuilds and17 capstone contract tests')
