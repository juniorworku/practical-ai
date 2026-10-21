from pathlib import Path
import tempfile,hashlib
def parse(path):
    raw=path.read_bytes();text=raw.decode('utf-8')
    if not text.strip(): raise ValueError('no extractable text')
    return {'text':text,'source':path.name,'revision':hashlib.sha256(raw).hexdigest(),'parser':'utf8-v1'}
with tempfile.TemporaryDirectory() as folder:
    p=Path(folder)/'policy.txt';p.write_text('refund 14 days')
    result=parse(p);assert result['source']=='policy.txt'
    p.write_text('  ')
    try: parse(p)
    except ValueError: pass
    else: raise AssertionError('empty indexed')
print('text extracted with provenance; blank extraction rejected')

# Bounded exercise variation
assert len(result['revision'])==64 and result['parser']=='utf8-v1'
print("Exercise variation: PASS")
