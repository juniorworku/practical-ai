def ingest(text,revision):
    if not text.strip(): raise ValueError('empty document')
    return [{'id':f'{revision}:{i}','revision':revision,'text':part.strip()} for i,part in enumerate(text.split('.')) if part.strip()]
def search(query,chunks): return [c for c in chunks if query in c['text'].lower()]
chunks=ingest('Refund window is 14 days. Unused items only.','policy-v1')
assert search('unused',chunks)[0]['id']=='policy-v1:1'
try: ingest('   ','empty')
except ValueError: pass
else: raise AssertionError('blank document ingested')
print('sentence chunks preserve revision and position; blank input rejected')

# Bounded exercise variation
revised=ingest('Refund window is 7 days. Unused items only.','policy-v2')
assert not ({c['id'] for c in chunks}&{c['id'] for c in revised})
print("Exercise variation: PASS")
