"""Publish complete student-built projects inside their own courses."""
import hashlib
from pathlib import Path
from progression import refresh
BASE=Path(__file__).resolve().parents[1]/'backend/academy/content/capstones'
PLANS={
 'ai-agent-bootcamp':('19','22'), 'ai-workshops':('17','18'),
 'freelancing-masterclass':('15','18'), 'ai-engineering-12-week':('35','36'),
 'genai-accelerator':('lesson-80','lab-20'), 'terminal-tutor':('terminal-07','terminal-08')}
def files(slug):
 return sorted(p for p in (BASE/slug).rglob('*') if p.is_file() and not any(part in {'.venv','__pycache__'} for part in p.parts) and not p.name.startswith('observed') and not p.name.endswith('-observed.json') and p.name!='.dockerignore' and (p.suffix in {'.py','.json','.csv','.md','.yaml','.txt','.ini','.html'} or p.name=='Dockerfile'))
def apply(programs):
 from student_depth import prepare_capstones
 prepare_capstones()
 for program in programs:
  slug=program['slug']
  if slug not in PLANS:continue
  bridge,final=PLANS[slug];folder=BASE/slug
  for row in program['lessons']:
   key=row['source_id'].rsplit(':',1)[-1]
   if key not in {bridge,final}:continue
   learning=row['resources']['learning'];readme=(folder/'README.md').read_text()
   if key==bridge:
    intro=readme.split('## Build from a fresh folder',1)[0] if '## Build from a fresh folder' in readme else readme
    chapter={'id':'capstone-assembly','title':'Connect the taught pieces before the capstone','kind':'Step-by-step integration teaching','body':intro+'\n\nThe final project chapter in this program provides every file, exact commands and the failure checks. Explain the storage, ownership and observed-result boundaries above before proceeding. No code from another program is required.'}
   else:
    public=files(slug)
    body=readme+'\n\n## Complete project files — no omitted application imports\n\n'
    for path in public:
     if path.name=='README.md':continue
     language='python' if path.suffix=='.py' else 'json' if path.suffix=='.json' else 'yaml' if path.suffix=='.yaml' else 'html' if path.suffix=='.html' else 'text'
     body+='### '+str(path.relative_to(folder))+'\n\n```'+language+'\n'+path.read_text().strip()+'\n```\n\n'
    body+='## Final student acceptance\n\nBuild in a fresh directory using only the files above. Run the documented check and retain its real output. Deliberately exercise one negative case, record its failure, repair it and rerun without deleting the failed evidence. Where this project uses Docker, prove readback after container replacement and compare a restored database. Keep untested live-model, human acceptance or cloud claims explicit. The bounded lesson variation remains a separate practice check; this integrated build is the final project.'
    chapter={'id':'capstone-build','title':'Build the complete final project from these files','kind':'Complete student capstone','body':body}
    learning['capstone']={'program':slug,'files':{str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in public},'independent':True,'runbook':'README.md'}
    learning['exercise']['steps'].append('Build and check the complete final project in the capstone chapter; retain the actual reports and one failed/corrected case.')
    criterion='The complete independent capstone runs from the published files; actual checks, negative cases and required restart/restore evidence are retained, with untested claims labeled.'
    learning['task']['criteria'].append(criterion)
    learning['exercise']['material']+='\n\n## Complete working capstone\n\n'+criterion+' Read the complete project chapter and run its documented acceptance procedure. A passing single-file lesson variation alone is insufficient.'
   chapters=learning['chapters'];index=next((i for i,c in enumerate(chapters) if c['id'] in {'case-study','project'}),len(chapters))
   chapters.insert(index,chapter);refresh(row)
