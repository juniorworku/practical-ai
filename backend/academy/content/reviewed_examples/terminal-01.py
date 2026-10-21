import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory(prefix='tutor-student-') as folder:
    root=Path(folder).resolve();exercises=root/'exercises';exercises.mkdir()
    (exercises/'answer.py').write_text("print('hello learner')\n")
    names=sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())
    assert names==['exercises/answer.py']
    assert (exercises/'answer.py').resolve().is_relative_to(root)
print('workspace contains only exercises/answer.py; app untouched')

# Bounded exercise variation
# Repeat with a fresh workspace so the earlier temporary directory need not exist.
with tempfile.TemporaryDirectory(prefix='tutor-notes-') as folder:
    root=Path(folder).resolve();note=root/'NOTES.md';note.write_text('next: test one boundary')
    assert note.resolve().is_relative_to(root) and note.read_text().startswith('next:')
print("Exercise variation: PASS")
