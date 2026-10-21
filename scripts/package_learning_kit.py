"""Package an explicit public course allowlist; never traverse account or app data."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
content=root/'backend/academy/content'
allowed_suffixes={'.md','.py','.json','.jsonl','.toml','.lock','.txt','.csv','.html','.sql','.yaml','.ini'}
def public_files(folder):
    for path in folder.rglob('*'):
        if not path.is_file() or path.name.startswith('observed') or path.name.endswith('-observed.json') or any(part in {'.venv','__pycache__','.pytest_cache','.git'} for part in path.parts):continue
        if path.suffix in allowed_suffixes or path.name.startswith('LICENSE') or path.name in {'Dockerfile','.dockerignore'}:yield path
with zipfile.ZipFile(content/'workshop-learning-kit.zip','w',zipfile.ZIP_DEFLATED) as kit:
    kit.writestr('README.md','# Practical AI learning kit\n\nOpen this as a separate learning workspace. `program_labs/README.md` explains six runnable offline exercises. `practical_programs.json` contains the four substantial academy programs. `program_content/` contains their individual Markdown sessions. `reviewed_workshop.json` contains the reviewed Accelerator and Tutor teaching, and `reviewed_examples/` contains their 113 runnable practice references. `accelerator_stack/` is the complete isolated API/PostgreSQL/Celery lab. `imported_curriculum.json` preserves the original source readings for provenance. `starter/` contains the original Accelerator capstone. Course documents are educational reference material; no upstream skill is automatically activated. No credentials or paid model calls are required for the offline exercises.\n')
    for name in ['imported_curriculum.json','reviewed_workshop.json','provenance.json','LICENSE.source','LICENSE.accelerator']:
        kit.write(content/name,name)
    kit.write(root/'backend/academy/starter_curriculum.json','practical_programs.json')
    for name in ['starter','program_labs','engineering_examples','reviewed_examples','accelerator_stack','capstones']:
        for path in public_files(content/name):kit.write(path,str(path.relative_to(content)))
    for path in public_files(root/'backend/academy/program_content'):
        kit.write(path,'program_content/'+str(path.relative_to(root/'backend/academy/program_content')))
print('Packaged public curriculum, practical sessions, offline labs, templates, and original starter.')
