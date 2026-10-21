records={};writes=[]
def apply(org,key,payload):
    scoped=(org,key)
    if scoped in records:
        old,result=records[scoped]
        if old!=payload: raise ValueError('idempotency conflict')
        return result
    result=f'receipt-{len(writes)+1}';writes.append(payload);records[scoped]=(payload,result);return result
assert apply('one','k1','draft')==apply('one','k1','draft')
assert writes==['draft']
try: apply('one','k1','changed')
except ValueError: pass
else: raise AssertionError('conflicting replay accepted')
print('exact replay reused receipt; changed payload rejected')

# Bounded exercise variation
assert apply('two','k1','draft')=='receipt-2' and len(writes)==2
print("Exercise variation: PASS")
