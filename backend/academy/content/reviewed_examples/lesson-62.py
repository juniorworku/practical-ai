calls=[]
def execute(proposal):
    if type(proposal) is not dict or set(proposal)!={'name','query'} or proposal['name']!='search': raise ValueError('denied')
    if type(proposal['query']) is not str or not 3<=len(proposal['query'].strip())<=200: raise ValueError('query')
    calls.append(proposal['query']);return ['p1']
assert execute({'name':'search','query':'refund'})==['p1']
try: execute({'name':'delete','query':'all'})
except ValueError: pass
else: raise AssertionError('write executed')
assert calls==['refund']
print('validated search executed; denied action produced no call')

# Bounded exercise variation
try: execute({'name':'search','query':''})
except ValueError: pass
else: raise AssertionError('empty query executed')
assert len(calls)==1
for bad in [None,[],{'name':'search','query':'   '}]:
    before=list(calls)
    try:execute(bad)
    except ValueError:pass
    else:raise AssertionError('invalid proposal executed')
    assert calls==before

print("Exercise variation: PASS")
