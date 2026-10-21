required={'http','worker','durable_db'}
targets={'http_only':{'http'},'full_stack':{'http','worker','durable_db'}}
def fits(name): return required<=targets[name]
assert not fits('http_only') and fits('full_stack')
print('deployment target checked against actual runtime requirements')

# Bounded exercise variation
required.add('gpu');assert not fits('full_stack')
print("Exercise variation: PASS")
