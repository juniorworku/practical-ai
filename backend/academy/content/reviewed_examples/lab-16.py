def workflow(limit=2):
    trace=['retrieve'];evidence='14 days'
    for attempt in range(1,limit+1):
        draft='90 days' if attempt==1 else evidence;trace+=['draft','verify']
        if draft==evidence: return {'verdict':'accepted','attempts':attempt,'trace':trace}
        if attempt<limit: trace.append('repair')
    return {'verdict':'rejected','attempts':limit,'trace':trace}
assert workflow()['trace']==['retrieve','draft','verify','repair','draft','verify']
assert workflow(1)['verdict']=='rejected'
print('repair route observed; exhausted workflow never labeled accepted')

# Bounded exercise variation
result=workflow();assert result['attempts']==2 and result['trace'].count('repair')==1
print("Exercise variation: PASS")
