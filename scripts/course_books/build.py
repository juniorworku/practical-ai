"""Build student-reviewed, aligned teaching. Never concatenate raw source chapters.
The pinned source remains reference material, not an exercise dependency.
"""
import hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path
from .business import CHAPTERS
from .cases import CASES
from .client_artifacts import ARTIFACTS
from .student_labs import LABS
from .container_lab import FILES, RESTORE_SCRIPT
from .audit_findings import FINDINGS
from .diagnostics import QUESTIONS
from .teaching import strengthen
ROOT=Path(__file__).resolve().parents[2]
LICENSE=(ROOT/'backend/academy/content/LICENSE.source').read_text()
REVISION=json.loads((ROOT/'backend/academy/content/provenance.json').read_text())['revision']
RELEASE='academy-course-books-v5'

def clean(text):
    text=re.sub(r'!\[[^\]]*\]\([^)]*\)','',text)
    text=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',text)
    return text.strip()

def fence(kind,text): return '```'+kind+'\n'+text.strip()+'\n```'

def docker_instructions():
    return '''### Run the isolated container experiment

Prerequisite: Docker Engine with Compose available. This is an optional local build; it uses no model key. Save the seven files above under a new `container-lab` folder with exactly the shown paths. Never run this unauthenticated experiment on a public interface or put real content in it. Its static page isolates networking and persistence; keep React for your own capstone.

```sh
cd container-lab
export LAB_DB_PASSWORD=synthetic-local-lab-password
export LAB_DJANGO_SECRET=synthetic-local-lab-secret-for-testing-only
export LAB_PORT=8091
docker compose -p academy-student-lab up -d --build
curl --fail http://127.0.0.1:8091/api/health/
curl --fail -H 'Content-Type: application/json' -d '{"body":"restart-proof-draft"}' http://127.0.0.1:8091/api/drafts/
docker compose -p academy-student-lab up -d --force-recreate backend
curl --fail http://127.0.0.1:8091/api/drafts/
```

Wait for the health request to succeed before the POST; startup ordering alone does not establish HTTP readiness. Open `http://127.0.0.1:8091/` and use the form, then reload. The same saved record must return from the API. Stop only the lab database with `docker compose -p academy-student-lab stop db`; a health request must return HTTP 503. Restart it with `docker compose -p academy-student-lab start db` and repeat readiness/readback. A process can be running while its dependency is unavailable.

Clean up using `docker compose -p academy-student-lab down`. This preserves the named volume. Add `--volumes` only when you deliberately want to delete this lab's synthetic records. Do not substitute your capstone or academy Compose project name.
'''

def run_lab(key):
    lab=LABS[key]
    with tempfile.TemporaryDirectory(prefix='academy-published-example-') as folder:
        path=Path(folder)/'example.py'; path.write_text(lab['code'])
        result=subprocess.run([sys.executable,'-I',str(path)],cwd=folder,capture_output=True,text=True,timeout=15)
        if result.returncode: raise RuntimeError(key+'\n'+result.stderr)
        return result.stdout.strip()

def prerequisite(course,index):
    slug=course['slug']
    if slug=='freelancing-masterclass':
        return ('Start with one working draft/review workflow. Use the fictional training-provider engagement; no real client or outreach is required.' if index==1 else
                f'Bring your artifacts from sessions 1–{index-1} of this program. Continue the same fictional training-provider engagement and keep assumption labels and revision IDs intact.')
    if slug=='ai-agent-bootcamp':
        return ('You need basic Python: functions, dictionaries, lists, exceptions and assertions. Read the scope first; session 2 covers the isolated workspace. No model key is required.' if index==1 else
                f'Complete sessions 1–{index-1} in this bootcamp. Keep your policy fixtures and evaluation labels in your own workspace. The example below runs independently so a prior missing file cannot block understanding.')
    studio=(index-1)//3+1; start=(studio-1)*3+1
    return (f'This is studio {studio}. '+
            ('Begin with basic Python functions, dictionaries and assertions; the specimen below supplies all its data.' if index==start else f'Bring the labeled inputs and artifacts from workshop session {start}. Continue the same studio dataset rather than changing inputs between comparisons.')+
            ' No other academy program or paid model account is required.')

def enrich(programs):
    manifest=[]; audit=[]
    for prefix,course in zip(['B','W','F'],programs):
        for index,lesson in enumerate(course['lessons'],1):
            key=f'{prefix}{index:02}'; learning=lesson['resources']['learning']
            original=clean(lesson['content'].split('## Further reading')[0])
            concept=original.split('## The engineering or business decision\n\n',1)[1].split('\n\n## Worked example',1)[0]
            project='## Worked example'+original.split('## Worked example',1)[1]
            glossary='\n\n'.join('### '+t['term']+'\n\n'+t['definition'] for t in learning['concepts'])
            chapters=[{'id':'decision','title':'Understand the decision: '+lesson['title'],'kind':'Teaching & prerequisites',
                       'body':'## Before you begin\n\n'+prerequisite(course,index)+'\n\n## Why this decision matters\n\n'+concept+'\n\n## Vocabulary used in this session\n\n'+glossary}]
            if prefix=='F':
                title,body=CHAPTERS[index-1]
                chapters.append({'id':'business','title':title,'kind':'Client-delivery concepts','body':body.strip()})
                title,body,extension=ARTIFACTS[index-1]
                output=None
                worked='## Completed specimen: '+title+'\n\n'+body+'\n\n## Critique and transfer\n\n'+extension+'\n\nTreat the completed specimen as a model of reasoning, not a result to copy into your own evidence. Your submission must replace its assumptions and statuses with your own observations, or remain explicitly simulated.'
            else:
                lab=LABS[key]; output=run_lab(key); extension=lab['extension']
                if key=='B19':
                    worked='## Follow the network and storage boundaries\n\n'+lab['explanation']+'\n\n'+ '\n\n'.join('### '+name+'\n\n'+fence('python' if name.endswith('.py') else 'html' if name.endswith('.html') else 'yaml' if name.endswith('.yaml') else 'text',text) for name,text in FILES.items())+'\n\n'+docker_instructions()
                else:
                    worked='## Predict before running\n\nRead the assertions and predict the output and rejected cases. Save the **entire** following block as `example.py` in a new scratch folder. Use Python 3.12; every import and synthetic fixture required for this example is included. Run `python3 -I example.py`. Assertions must be enabled; do not use `-O`. No model, network, database service or third-party package is required. SQLite examples create a temporary database and clean it up.\n\n'+fence('python',lab['code'])+'\n\n## Expected observation\n\n'+fence('text',output)+'\n\n## Walk through the mechanism and its limits\n\n'+lab['explanation']
                if key=='B20':
                    worked+='\n\n## Rehearse the PostgreSQL restore in your previous lab\n\nReturn to the isolated `container-lab` from session 19 and start its stack. Save at least one synthetic draft. Keep other writers stopped during this small comparison so source data does not change after the snapshot. Save the entire block below as `verify-restore.sh` and run `sh verify-restore.sh` from that directory. It needs no host PostgreSQL tools: pg_dump, createdb, pg_restore and psql run inside the lab database container. The script stops if its backup file or restore target already exists; inspect those artifacts and choose fresh names for another rehearsal. Never substitute the academy database or a real client project.\n\n'+fence('sh',RESTORE_SCRIPT)+'\n\nThe target database is separate from `lab`. Matching IDs and body text establish that this snapshot can be read after restore, not only that a dump file exists. Save the backup creation time and restore duration. No source writes are replayed after the snapshot; a live service needs a planned consistency and recovery-point strategy. This local synthetic rehearsal does not test encrypted backup custody, retention or disaster recovery. Keep those as explicit operational requirements.\n'
                worked+='\n\n## Extend the example\n\n'+extension+'\n\nThe assertions demonstrate only the named local behavior. They do not execute your capstone, grade factual judgments, or prove that a real provider or external integration works.'
                title='Worked implementation: '+lesson['title']
            chapters.append({'id':'worked-implementation','title':title,'body':worked,'kind':'Complete worked artifact' if prefix=='F' else 'Runnable example & reasoning'})
            chapters.append({'id':'case-study','title':'Build and challenge your own version','body':project,'kind':'Guided project & acceptance'})
            case_title,fixture,expected,why,variation=CASES[course['slug']][index-1]
            # No unrelated upstream exercises, dependency fragments or quizzes.
            material='## '+case_title+'\n\n### 1. Inspect the input and predict the outcome\n\nBefore consulting the worked example, record a predicted decision and the evidence you would need to justify it.\n\n'+fence('json',json.dumps(fixture,indent=2,ensure_ascii=False))+'\n\n### 2. Explain the expected decision\n\n'+why+'\n\n'+fence('json',json.dumps(expected,indent=2,ensure_ascii=False))+'\n\n### 3. Run or complete the lesson example\n\n'+('Read the completed client artifact in the Lesson tab; recreate its analysis with your own assumptions. Label role-play results as simulated.' if prefix=='F' else 'Use the complete worked implementation in the Lesson tab. Predict its output, run it, and explain each assertion. The Docker session supplies its full files and separate procedure.')+'\n\n### 4. Make the targeted change\n\n'+extension+'\n\n### 5. Challenge the boundary\n\n'+variation+'\n\n### 6. Build the session deliverable\n\n'+'\n'.join(f'{i}. {s}' for i,s in enumerate(learning['exercise']['steps'],1))+'\n\n### What to submit and check\n\nSave `'+lesson['resources']['artifact']+'` with fixture/candidate revisions, prediction, actual observation, explanation of any discrepancy and limitations. Keep the original failed result beside the correction.\n\n'+'\n'.join('- '+c for c in learning['task']['criteria'])+'\n\nThe academy stores your written evidence; it does not run your code or certify external work. A copied expected output is not an observed experiment.'
            learning['exercise']['material']=material
            learning['questions'].extend([{'id':'diagnosis','prompt':extension},{'id':'transfer','prompt':variation}])
            prompt,right,wrong1,wrong2,explanation=QUESTIONS[prefix][index-1]
            options=[right,wrong1,wrong2]; shift=index%3; options=options[shift:]+options[:shift]
            learning['quiz'].append({'id':'worked-diagnostic','prompt':prompt,'options':[{'id':chr(97+i),'text':value} for i,value in enumerate(options)],'correct':chr(97+options.index(right)),'explanation':explanation})
            strengthen(key,learning,chapters,why,variation)
            learning['chapters']=chapters
            lesson['task']='\n'.join(learning['exercise']['steps'])
            learning['attribution']={'notice':LICENSE,'credit':'Academy-authored teaching, examples and client artifacts. AI Engineering from Scratch by Rohit Ghumare informed the background curriculum; its MIT notice is retained. No external repository or download is required for this session.','revision':REVISION}
            learning['revision']=hashlib.sha256(json.dumps({k:v for k,v in learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()
            lesson['content']='# '+lesson['title']+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in chapters)
            lesson['content_hash']=hashlib.sha256(lesson['content'].encode()).hexdigest()
            lesson['source_url']=''; lesson['resources']['revision']=RELEASE
            lesson['resources']['references']=[]; lesson['resources']['provenance']=[]
            record={'program':course['slug'],'lesson':index,'title':lesson['title'],'chapters':len(chapters),'words':len(lesson['content'].split()),'concepts':len(learning['concepts']),'quiz':len(learning['quiz']),'cards':len(learning['flashcards']),'example':key if prefix!='F' else None}
            manifest.append(record)
            audit.append({'id':key,'program':course['slug'],'lesson':index,'title':lesson['title'],
                          'prior_defect':FINDINGS[course['slug']][index-1],
                          'replacement':title,'student_extension':extension,
                          'boundary_challenge':variation,'acceptance':learning['task']['criteria'],
                          'verification':('completed specimen reviewed; arithmetic checked separately; no real client work claimed' if prefix=='F' else 'complete isolated Python example executed with assertions; Docker behavior separately tested' if key=='B19' else 'complete published Python example executed with assertions'),
                          'observed_stdout':output})
    (ROOT/'docs/course-book-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'docs/student-content-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
