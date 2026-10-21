from pathlib import Path
import tempfile
def resource(root,name):
    resolved=(root/name).resolve()
    if not resolved.is_relative_to(root.resolve()): raise ValueError('outside package')
    return resolved.read_text()
with tempfile.TemporaryDirectory() as folder:
    root=Path(folder);(root/'guide.txt').write_text('teach one concept, then wait')
    assert resource(root,'guide.txt').startswith('teach one concept')
    try: resource(root,'../escape.txt')
    except ValueError: pass
    else: raise AssertionError('package boundary escaped')
print('referenced file inspected; traversal denied; nothing activated')

# Bounded exercise variation
with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    try: resource(root,Path(folder).parent/'not-in-package.txt')
    except ValueError: pass
    else: raise AssertionError('absolute escape accepted')
print("Exercise variation: PASS")
