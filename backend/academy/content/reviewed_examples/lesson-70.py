import hashlib
def digest(payload): return hashlib.sha256(payload.encode()).hexdigest()
approval={'owner':'one','reviewer':'r1','digest':digest('draft event'),'expires':10}
def allowed(owner,payload,now,cancelled=False):
    return not cancelled and owner==approval['owner'] and bool(approval['reviewer']) and digest(payload)==approval['digest'] and now<approval['expires']
assert allowed('one','draft event',9)
assert not allowed('one','changed event',9)
assert not allowed('two','draft event',9)
assert not allowed('one','draft event',10)
print('approval tied to exact payload, owner, reviewer and expiry')

# Bounded exercise variation
assert not allowed('one','draft event',9,True)
print("Exercise variation: PASS")
