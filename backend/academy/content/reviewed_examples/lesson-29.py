def ready(probes): return all(probe() for probe in probes)
assert ready([lambda:True,lambda:True])
assert not ready([lambda:True,lambda:False])
status=200 if ready([lambda:False]) else 503
assert status==503
print('dependency failure blocks readiness, not process liveness')

# Bounded exercise variation
assert ready([lambda:True])
print("Exercise variation: PASS")
