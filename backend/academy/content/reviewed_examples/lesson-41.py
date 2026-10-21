def state(passages):
    if not passages: return 'missing'
    versions={}
    for p in passages: versions.setdefault(p['policy'],set()).add(p['revision'])
    return 'conflict' if any(len(v)>1 for v in versions.values()) else 'available'
a={'policy':'refund','revision':'v1'}
assert state([])=='missing'
assert state([a,{'policy':'delivery','revision':'v2'}])=='available'
assert state([a,{'policy':'refund','revision':'v2'}])=='conflict'
print('unrelated versions allowed; conflicting revisions of one policy flagged')

# Bounded exercise variation
assert state([a,dict(a)])=='available'
print("Exercise variation: PASS")
