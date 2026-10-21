CAPABILITIES={'researcher':{'search'},'reviewer':{'verify'}}
def allowed(role,operation): return operation in CAPABILITIES.get(role,set())
assert allowed('researcher','search')
assert not allowed('reviewer','search')
assert not allowed('researcher','send')
print('role capabilities enforced; role names alone grant no extra authority')

# Bounded exercise variation
assert not allowed('supervisor','delete')
print("Exercise variation: PASS")
