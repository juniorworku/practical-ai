import json

def records(chunks, max_line=200):
    pending = b''
    for chunk in chunks:
        pending += chunk
        while b'\n' in pending:
            line, pending = pending.split(b'\n', 1)
            if len(line) > max_line:
                raise ValueError('line budget exceeded')
            if line.strip():
                yield json.loads(line)
        if len(pending) > max_line:
            raise ValueError('unfinished line budget exceeded')
    if pending.strip():
        raise ValueError('truncated stream: missing final newline')

raw = '{"text":"café"}\n{"done":true}\n'.encode()
cut = raw.index(b'\xc3') + 1
output = list(records([raw[:cut], raw[cut:cut+3], raw[cut+3:]]))
assert output == [{'text':'café'}, {'done':True}]
try:
    list(records([b'{"done":']))
except ValueError:
    print('Truncated stream rejected; no false done signal')
else:
    raise AssertionError('truncated stream accepted')
print('UTF-8 and framing preserved:', output)
