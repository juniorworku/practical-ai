"""Copy only public course artifacts. Never imports accounts, databases, env, or skills as instructions."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path, help='Resume Studio root')
args = parser.parse_args()
source = args.source / 'studio'
target = Path(__file__).resolve().parents[1] / 'backend/academy/content'
target.mkdir(parents=True, exist_ok=True)
rows = []
catalog = json.loads((source / 'curriculum/catalog.json').read_text())
for phase in catalog['phases']:
    lessons = []
    for i, item in enumerate(phase['lessons']):
        text = item['text']
        digest = hashlib.sha256(text.encode()).hexdigest()
        # Preserve original source identity and artifacts without interpreting any instructions.
        lessons.append(dict(title=item['title'], module=phase['title'], order=i, minutes=45,
            content=text, task='Work through the practice in this source chapter. Record what you tried and what remains unverified.',
            source_id=item['id'], source_url=f"{catalog['repository']}/blob/{catalog['revision']}/{item['path']}/docs/en.md",
            content_hash=digest, resources={k:item[k] for k in ['quiz','code','languages','default_language'] if k in item}))
    rows.append(dict(slug=f"library-phase-{phase['number']:02}",title=phase['title'],category='Library',description=f"Full source readings from phase {phase['number']:02} of AI Engineering from Scratch.",audience='Self-paced learners building AI engineering foundations.',outcome='Complete source readings, code references, and practical exercises.',duration=f"{len(lessons)} chapters",level='Self-paced',order=10+phase['number'],lessons=lessons))
acc = json.loads((source / 'accelerator_content/catalog.json').read_text())
modules = {m['number']:m['title'] for m in acc['modules']}
lessons = []
for i,item in enumerate(acc['lessons'] + acc['labs']):
    text = (source/'accelerator_content'/item['path']).read_text()
    digest = hashlib.sha256(text.encode()).hexdigest()
    if digest != item['sha256']: raise ValueError(f"Content hash mismatch: {item['id']}")
    lessons.append(dict(title=item['title'],module=modules[item['module']] if 'module' in item else f"Lab {item['day']:02}",order=i,minutes=item['minutes'],content=text,task='\n'.join(item.get('checks',[])),source_url=item.get('source_url',acc['source_repository']),source_id=item['id'],content_hash=digest,resources={'artifact':item.get('artifact',''),'checks':item.get('checks',[])}))
rows.append(dict(slug='genai-accelerator',title='GenAI Accelerator',category='Accelerator',description='The original capstone learning path: foundations, RAG, evaluation, deployment, agents, graphs, and MCP.',audience='Builders ready to implement and evaluate a document assistant.',outcome='A policy-document assistant capstone with tests and evaluation evidence.',duration=f"{len(acc['lessons'])} lessons · {len(acc['labs'])} labs",level='Core + advanced',order=3,lessons=lessons))
terminal = json.loads((source/'terminal_content/catalog.json').read_text())
lessons=[]
for i,item in enumerate(terminal):
    text=(source/'terminal_content'/f"{item['number']:02}.md").read_text()
    lessons.append(dict(title=item['title'],module='Terminal Tutor guide',order=i,minutes=20,content=text,task='Try the guide in a separate local learning workspace. This academy does not execute code.',source_id=f"terminal-{item['number']:02}",source_url='',content_hash=hashlib.sha256(text.encode()).hexdigest(),resources={}))
rows.append(dict(slug='terminal-tutor',title='Terminal Tutor',category='Tutor',description='Your original eight-part guide to learning with a coding tutor in a separate workspace.',audience='Learners who want guided local coding practice.',outcome='A repeatable learn, code, run, and review loop.',duration='8 guides',level='Beginner friendly',order=4,lessons=lessons))
(target/'imported_curriculum.json').write_text(json.dumps(rows,ensure_ascii=False))
for folder,license_name,dest in [('curriculum','LICENSE','LICENSE.source'),('accelerator_content','LICENSE.upstream','LICENSE.accelerator')]:
    shutil.copyfile(source/folder/license_name,target/dest)
shutil.copytree(source/'accelerator_content/starter',target/'starter',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.venv','.env','*.pyc','.pytest_cache'))
manifest={'source_repository':catalog['repository'],'revision':catalog['revision'],'chapters':sum(len(p['lessons']) for p in catalog['phases']),'accelerator_lessons':len(acc['lessons']),'accelerator_labs':len(acc['labs']),'terminal_guides':len(terminal),'note':'Imported course documents are reference content. No accounts, credentials, progress, or app runtime were copied.'}
(target/'provenance.json').write_text(json.dumps(manifest,indent=2))
import subprocess, sys
subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'package_learning_kit.py')],check=True)
print(json.dumps(manifest,indent=2))
