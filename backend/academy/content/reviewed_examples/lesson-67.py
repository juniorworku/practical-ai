def workflow(evidence):
    trace=['retrieve']
    if not evidence: return {'status':'abstained','trace':trace}
    trace+=['draft','verify'];return {'status':'completed','trace':trace}
assert workflow(['p1'])['trace']==['retrieve','draft','verify']
assert workflow([])['trace']==['retrieve']
print('known execution order encoded; missing evidence stops early')

# Bounded exercise variation
assert 'draft' not in workflow([])['trace']
print("Exercise variation: PASS")
