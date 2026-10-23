import json

def records(chunks, *, max_line=80, max_total=240, max_records=2):
    pending=b'';total=0;count=0
    for chunk in chunks:
        if not isinstance(chunk,bytes):raise ValueError('bytes required')
        total+=len(chunk)
        if total>max_total:raise ValueError('total allowance')
        pending+=chunk
        while b'\n' in pending:
            line,pending=pending.split(b'\n',1)
            if len(line)>max_line:raise ValueError('record allowance')
            if not line.strip():continue
            count+=1
            if count>max_records:raise ValueError('record count')
            yield json.loads(line)
        if len(pending)>max_line:raise ValueError('unfinished allowance')
    if pending.strip():raise ValueError('truncated stream')

raw='{"text":"café 😄"}\n{"done":true}\n'.encode()
expected=[{'text':'café 😄'},{'done':True}]
for split in range(len(raw)+1):
    assert list(records([raw[:split],raw[split:]]))==expected
assert list(records([raw[n:n+1] for n in range(len(raw))]))==expected
for bad in [[raw[:-1]],[b'{}\n'*3],[b'x'*81],[b' '*241],[b'{broken}\n']]:
    try:list(records(bad))
    except ValueError:pass
    else:raise AssertionError('bad stream accepted')
print('Every two-chunk partition and one-byte delivery preserved exact UTF-8 records')
