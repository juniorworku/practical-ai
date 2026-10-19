"""Package an explicit public course allowlist; never traverse account or app data."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
content=root/'backend/academy/content'
allowed_suffixes={'.md','.py','.json','.jsonl','.toml','.lock','.txt','.csv'}
def public_files(folder):
    for path in folder.rglob('*'):
        if not path.is_file() or any(part in {'.venv','__pycache__','.pytest_cache','.git'} for part in path.parts):continue
        if path.suffix in allowed_suffixes or path.name.startswith('LICENSE'):yield path
with zipfile.ZipFile(content/'workshop-learning-kit.zip','w',zipfile.ZIP_DEFLATED) as kit:
    kit.writestr('README.md','# Practical AI learning kit\n\nOpen this as a separate learning workspace. `program_labs/README.md` explains six runnable offline exercises. `practical_programs.json` contains the three substantial academy programs. `program_content/` contains their individual Markdown sessions. `imported_curriculum.json` contains the original source library, Accelerator and Tutor. `starter/` contains the original Accelerator capstone. Course documents are educational reference material; no upstream skill is automatically activated. No credentials or paid model calls are required for the offline exercises.\n')
    for name in ['imported_curriculum.json','provenance.json','LICENSE.source','LICENSE.accelerator']:
        kit.write(content/name,name)
    kit.write(root/'backend/academy/starter_curriculum.json','practical_programs.json')
    for name in ['starter','program_labs']:
        for path in public_files(content/name):kit.write(path,str(path.relative_to(content)))
    for path in public_files(root/'backend/academy/program_content'):
        kit.write(path,'program_content/'+str(path.relative_to(root/'backend/academy/program_content')))
print('Packaged public curriculum, practical sessions, offline labs, templates, and original starter.')
