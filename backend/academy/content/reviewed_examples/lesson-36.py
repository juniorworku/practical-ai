def nearest(query,rows,org,k=2):
    scoped=[r for r in rows if r['org']==org]
    if any(len(r['vector'])!=len(query) for r in scoped): raise ValueError('dimension mismatch')
    return [r['id'] for r in sorted(scoped,key=lambda r:(sum((a-b)**2 for a,b in zip(query,r['vector'])),r['id']))[:k]]
rows=[{'id':'a','org':'one','vector':[1,0]},{'id':'b','org':'two','vector':[0,0]}]
assert nearest([0,0],rows,'one')==['a']
assert nearest([0,0],rows,'unknown')==[]
print('tenant filter precedes distance ranking')

# Bounded exercise variation
try: nearest([0,0,0],rows,'one')
except ValueError: pass
else: raise AssertionError('incompatible dimensions ranked')
print("Exercise variation: PASS")
