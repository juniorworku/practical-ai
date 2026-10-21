"""Build the authored academy programs. No model or network calls."""
import sys, json, hashlib, runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'programs'))
from common import PROGRAMS, ROOT
import bootcamp, workshops, freelancing
sys.path.insert(0,str(Path(__file__).parent/'activities'))
from bank import BANK
for name in ['bootcamp','workshops','freelancing']:
    runpy.run_path(str(Path(__file__).parent/'activities'/f'{name}.py'))
assert len(BANK)==60
# Keep compact fingerprints of generated releases so later deployments can
# upgrade their own text and activities without replacing instructor edits.
history_path=ROOT/'backend/academy/course_book_history.json'
history=json.loads(history_path.read_text()) if history_path.exists() else {}
for old_course in json.loads((ROOT/'backend/academy/starter_curriculum.json').read_text()):
    for old in old_course['lessons']:
        if old['resources'].get('revision','').startswith('academy-course-books-v'):
            fingerprints=history.setdefault(old['source_id'],{'content':[],'learning':[]})
            for field,value in [('content',old['content_hash']),('learning',old['resources']['learning']['revision'])]:
                if value not in fingerprints[field]:fingerprints[field].append(value)
history_path.write_text(json.dumps(history,indent=2)+'\n')
previous=ROOT/'backend/academy/previous_practical_curriculum.json'
if not previous.exists(): previous.write_text((ROOT/'backend/academy/starter_curriculum.json').read_text())
for course,prefix in zip(PROGRAMS,['B','W','F']):
    for index,item in enumerate(course['lessons'],1):
        activity=BANK[f'{prefix}{index:02}']
        cards=[{'id':f'card-{i+1}','front':front,'back':back} for i,(front,back) in enumerate(activity['cards'])]
        question,answer,wrong1,wrong2,why=activity['scenario']
        def quiz(qid,prompt,options,explanation,shift):
            tagged=[(i==0,text) for i,text in enumerate(options)]
            tagged=tagged[shift:]+tagged[:shift]
            choices=[{'id':chr(97+i),'text':text} for i,(_,text) in enumerate(tagged)]
            return {'id':qid,'prompt':prompt,'options':choices,'correct':next(chr(97+i) for i,(right,_) in enumerate(tagged) if right),'explanation':explanation}
        quizzes=[quiz('scenario',question,[answer,wrong1,wrong2],why,index%3),quiz('concept',f"Which statement describes {cards[0]['front'].lower()} in this lesson?",[c['back'] for c in cards],cards[0]['back']+' Keep this distinct from the other two concepts in this session.',(index+1)%3)]
        learning={'concepts':[{'term':c['front'],'definition':c['back']} for c in cards], 'questions':[{'id':'reflection','prompt':activity['reflection']}], 'quiz':quizzes,'flashcards':cards,'exercise':{'steps':item['task'].split('\n'),'hint':why},'task':{'title':item['title']+' — practical submission','deliverable':item['resources']['artifact'],'criteria':item['resources']['checks']}}
        learning['revision']=hashlib.sha256(json.dumps(learning,sort_keys=True).encode()).hexdigest()
        item['resources']['learning']=learning

from course_books.build import enrich
enrich(PROGRAMS)
from engineering.build import build as build_engineering
PROGRAMS.append(build_engineering())
from engineering.principles import apply
apply(PROGRAMS)
from progression import apply as apply_progression
apply_progression(PROGRAMS)
from capstone_books import apply as apply_capstones
apply_capstones(PROGRAMS)

archive=ROOT/'backend/academy/legacy_starter_curriculum.json'
target=ROOT/'backend/academy/starter_curriculum.json'
if not archive.exists():
    archive.write_text(target.read_text())
for p in PROGRAMS:
    p.pop('_capstone')
    folder=ROOT/'backend/academy/program_content'/p['slug']
    folder.mkdir(parents=True,exist_ok=True)
    for l in p['lessons']:
        (folder/f"{l['order']+1:02}.md").write_text(l['content'])
target.write_text(json.dumps(PROGRAMS,indent=2,ensure_ascii=False)+'\n')
for p in PROGRAMS:
    words=sum(len(l['content'].split()) for l in p['lessons'])
    print(f"{p['title']}: {len(p['lessons'])} sessions, {sum(l['minutes'] for l in p['lessons'])/60:g} practice hours, {words} words")

# Keep the optional offline archive in step with the in-app books.
runpy.run_path(str(ROOT/'scripts/package_learning_kit.py'))
