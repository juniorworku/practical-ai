"""Apply a versioned teaching contract without touching imported originals."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from academy.pedagogy import module_contract,chapter

def apply(programs):
    for course in programs:
        for index,lesson in enumerate(course['lessons']):
            learning=lesson['resources']['learning']
            contract=module_contract(course['slug'],lesson['module'])
            learning['chapters'].append({'id':'engineering-principles','title':'Apply the three engineering pillars','kind':'Production practice','body':chapter(contract)})
            last=index==len(course['lessons'])-1 or course['lessons'][index+1]['module']!=lesson['module']
            if last:
                learning['task']['criteria'].extend(contract['release_gates'])
                learning['exercise']['steps'].append('Complete '+contract['deliverable'])
                lesson['task']+='\nComplete '+contract['deliverable']
                learning['exercise']['material']+='\n\n## Module release checks\n\n'+'\n'.join('- '+g for g in contract['release_gates'])+'\n\nComplete '+contract['deliverable']
            lesson['resources']['pedagogy']=contract
            lesson['resources']['checks']=learning['task']['criteria']
            lesson['resources']['revision']='academy-course-books-v6'
            learning['revision']=hashlib.sha256(json.dumps({k:v for k,v in learning.items() if k!='revision'},sort_keys=True).encode()).hexdigest()
            lesson['content']='# '+lesson['title']+'\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['body'] for c in learning['chapters'])
            lesson['content_hash']=hashlib.sha256(lesson['content'].encode()).hexdigest()
    manifest=[{'program':p['slug'],'lesson':l['order']+1,'title':l['title'],'chapters':len(l['resources']['learning']['chapters']),'words':len(l['content'].split()),'concepts':len(l['resources']['learning']['concepts']),'quiz':len(l['resources']['learning']['quiz']),'cards':len(l['resources']['learning']['flashcards'])} for p in programs for l in p['lessons']]
    (ROOT/'docs/course-book-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
