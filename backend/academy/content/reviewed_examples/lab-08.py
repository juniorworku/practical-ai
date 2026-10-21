rows=[{'id':'a','org':'one','v':[0,0]},{'id':'b','org':'one','v':[1,0]},{'id':'c','org':'one','v':[3,0]},{'id':'secret','org':'two','v':[0,0]}]
def retrieve(query,org,k):
    return [r['id'] for r in sorted([r for r in rows if r['org']==org],key=lambda r:(sum((a-b)**2 for a,b in zip(query,r['v'])),r['id']))[:k]]
def recall(ids,relevant): return len(set(ids)&relevant)/len(relevant)
ranked=retrieve([0,0],'one',2)
assert ranked==['a','b'] and recall(ranked,{'a','b'})==1
assert 'secret' not in ranked
print('scoped fixture vector ranking; recall at 2=1')

# Bounded exercise variation
assert recall(retrieve([0,0],'one',1),{'a','b'})==.5
print("Exercise variation: PASS")
