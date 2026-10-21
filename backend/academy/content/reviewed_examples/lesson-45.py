def event(request,stage,duration,**extra):
    return {'request_id':request,'stage':stage,'duration_ms':duration,'count':extra.get('count',0)}
trace=[event('r1','retrieval',12,count=2,text='PRIVATE'),event('r1','generation',80,count=1)]
assert {e['request_id'] for e in trace}=={'r1'}
assert all('text' not in e for e in trace)
assert sum(e['duration_ms'] for e in trace)==92
print('two correlated stages; raw text excluded from trace')

# Bounded exercise variation
trace.append(event('r1','validation',3));assert sum(e['duration_ms'] for e in trace)==95
print("Exercise variation: PASS")
