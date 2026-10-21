import tempfile,tomllib
from pathlib import Path
with tempfile.TemporaryDirectory() as folder:
    project=Path(folder)/'pyproject.toml'
    project.write_text('[project]\nname="policy-lab"\nversion="0.1.0"\nrequires-python=">=3.12"\ndependencies=[]\n')
    metadata=tomllib.loads(project.read_text())['project']
    assert metadata['requires-python'] == '>=3.12'
    assert metadata['dependencies'] == []
print('declared project parsed; no install performed')

# Bounded exercise variation
assert metadata['version'] == '0.1.0'
assert not metadata['dependencies']
print("Exercise variation: PASS")
