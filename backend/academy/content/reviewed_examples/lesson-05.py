DOCS=[{'id':'p1','text':'refund window 14 days'}]
def retrieve(query):
    return [p for p in DOCS if set(query.split()) & set(p['text'].split())]
def answer(query):
    passages=retrieve(query)
    return {'text':passages[0]['text'],'ids':[passages[0]['id']]} if passages else {'text':'Insufficient evidence','ids':[]}
assert answer('refund')['ids']==['p1']
assert answer('warranty')['ids']==[]
print('retrieval-sensitive positive and missing-evidence checks passed')

# Bounded exercise variation
assert answer('???')['ids']==[]
print("Exercise variation: PASS")
