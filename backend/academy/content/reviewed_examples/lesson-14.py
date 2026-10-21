def answer(question,retrieve,generate):
    evidence=retrieve(question)
    return generate(evidence) if evidence else 'Insufficient evidence'
calls=[]
def fake(evidence): calls.append(evidence);return evidence[0]
assert answer('unknown',lambda q:[],fake)=='Insufficient evidence'
assert calls==[]
assert answer('refund',lambda q:['14 days'],fake)=='14 days'
assert calls==[['14 days']]
print('empty retrieval skips generation; evidence reaches injected dependency')

# Bounded exercise variation
def broken(q): raise TimeoutError('retrieval')
try: answer('refund',broken,fake)
except TimeoutError: pass
else: raise AssertionError('retrieval outage hidden')
print("Exercise variation: PASS")
