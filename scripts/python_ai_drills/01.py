from dataclasses import dataclass, FrozenInstanceError

@dataclass(frozen=True, slots=True)
class Request:
    owner: str
    query: str
    sources: tuple[str, ...]

def parse(trusted_owner, body):
    if trusted_owner not in {'team-a','team-b'}: raise ValueError('owner denied')
    if not isinstance(body,dict) or set(body)!={'query','sources'}: raise ValueError('unexpected fields')
    query=body['query'];sources=body['sources']
    if not isinstance(query,str) or not query.strip() or len(query)>2000: raise ValueError('query')
    if not isinstance(sources,list) or len(sources)>4 or any(not isinstance(s,str) or not s for s in sources): raise ValueError('sources')
    return Request(trusted_owner,query,tuple(sources))

original={'query':'refund','sources':['policy-v1']}
request=parse('team-a',original)
original['sources'].append('other')
assert request.sources==('policy-v1',), 'input alias crossed immutable boundary'
for body in [[],{**original,'owner':'team-b'},{'query':True,'sources':[]},{'query':'refund','sources':[3]}]:
    try:parse('team-a',body)
    except ValueError:pass
    else:raise AssertionError('bad body accepted')
try:request.query='changed'
except FrozenInstanceError:pass
else:raise AssertionError('request mutated')
print('Exact schema, trusted identity and immutable nested values verified')
