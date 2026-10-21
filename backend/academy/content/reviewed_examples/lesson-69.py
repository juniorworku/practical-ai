import tempfile,json
from pathlib import Path
state={'version':1,'thread':'t1','owner':'one','next':'verify','completed':['retrieve','draft']}
with tempfile.TemporaryDirectory() as folder:
    file=Path(folder)/'checkpoint.json';file.write_text(json.dumps(state))
    loaded=json.loads(file.read_text())
    assert loaded['owner']=='one' and loaded['version']==1
    assert loaded['next']=='verify' and loaded['completed']==['retrieve','draft']
print('state reloaded from file; next node and completed work preserved')

# Bounded exercise variation
def resume_checkpoint(saved,authenticated_owner):
    if saved.get('owner')!=authenticated_owner: raise PermissionError('checkpoint owner')
    if saved.get('version')!=1: raise ValueError('checkpoint version')
    return saved['next']
assert resume_checkpoint(loaded,'one')=='verify'
try: resume_checkpoint(loaded,'two')
except PermissionError: pass
else: raise AssertionError('cross-owner checkpoint returned')
print("Exercise variation: PASS")
