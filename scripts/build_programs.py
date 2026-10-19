"""Build the authored academy programs. No model or network calls."""
import sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'programs'))
from common import PROGRAMS, ROOT
import bootcamp, workshops, freelancing
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
