ADR={'choice':'read-only pipeline','alternative':'autonomous writer','trigger':'approved writes required'}
def revisit(requirement): return requirement==ADR['trigger']
assert not revisit('new UI theme')
assert revisit('approved writes required')
print('decision tied to a concrete change in requirements')

# Bounded exercise variation
assert not revisit('rename the application')
print("Exercise variation: PASS")
