import hashlib
ledger={};effects=[]
def digest(text): return hashlib.sha256(text.encode()).hexdigest()
approval={'owner':'one','digest':digest('draft event'),'expires':20,'reviewer':'r1'}
def resume(owner,payload,now,key):
    if owner!=approval['owner'] or digest(payload)!=approval['digest'] or now>=approval['expires'] or not approval['reviewer']: raise ValueError('approval')
    scoped=(owner,key,digest(payload))
    if scoped not in ledger: effects.append(payload);ledger[scoped]=f'receipt-{len(effects)}'
    return ledger[scoped]
assert resume('one','draft event',10,'k1')==resume('one','draft event',10,'k1')
assert effects==['draft event']
try: resume('one','changed',10,'k1')
except ValueError: pass
else: raise AssertionError('changed proposal executed')
print('approved exact payload replayed once; changed payload denied')

# Bounded exercise variation
try: resume('one','draft event',20,'k2')
except ValueError: pass
else: raise AssertionError('expired approval executed')
assert len(effects)==1
print("Exercise variation: PASS")
