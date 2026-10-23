import hashlib
import json

def key(owner, model, source_version, prompt_version, query):
    fields = [owner, model, source_version, prompt_version, query]
    return hashlib.sha256(json.dumps(fields, ensure_ascii=False).encode()).hexdigest()

cache = {}
a = key('a','fixture-v1','source-v1','prompt-v1','refund?')
cache[a] = {'answer':'14 days','source':'a1'}
assert key('b','fixture-v1','source-v1','prompt-v1','refund?') not in cache
assert key('a','fixture-v1','source-v2','prompt-v1','refund?') not in cache
assert key('a','fixture-v2','source-v1','prompt-v1','refund?') not in cache
assert len(a) == 64
# This dictionary is intentionally process-local. Lesson 9 adds persistence.
print('Version and owner boundaries produce different keys')
