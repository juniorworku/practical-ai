REQUIRED={'scope_isolation','citations','abstention'}
def allow(report): return all(report.get(key) is True for key in REQUIRED)
assert not allow({'citations':True,'abstention':True})
assert allow({key:True for key in REQUIRED})
assert not allow({key:'passed' for key in REQUIRED})
print('missing and non-boolean evidence block release')

# Bounded exercise variation
report={key:True for key in REQUIRED};report['scope_isolation']=False;assert not allow(report)
print("Exercise variation: PASS")
