def memory(observations,limit=2): return observations[-limit:] if limit>0 else []
def key(org,revision,query): return (org,revision,query)
observations=[{'id':'p1'},{'id':'p2'},{'id':'p3'}]
assert memory(observations)==[{'id':'p2'},{'id':'p3'}]
assert key('one','v1','refund')!=key('two','v1','refund')
assert key('one','v1','refund')!=key('one','v2','refund')
print('bounded observations retain IDs; scoped revision-aware cache keys differ')

# Bounded exercise variation
assert memory(observations,0)==[]
print("Exercise variation: PASS")
