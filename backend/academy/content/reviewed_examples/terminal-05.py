def buggy(citation,allowed): return bool(citation)
assert buggy('invented',{'p1'})  # Reproduces the defect; not desired behavior.
def valid(citation,allowed): return citation in allowed
assert valid('p1',{'p1'})
assert not valid('invented',{'p1'})
assert not valid('',{'p1'})
print('defect reproduced; membership repair passes positive and counterexample')

# Bounded exercise variation
assert valid('p2',{'p1','p2'})
assert not valid('p3',{'p1','p2'})
print("Exercise variation: PASS")
