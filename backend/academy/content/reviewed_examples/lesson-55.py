def choose(candidate,previous,healthy,compatible):
    if not compatible: raise ValueError('manual recovery required')
    return candidate if healthy else previous
assert choose('v2','v1',False,True)=='v1'
assert choose('v2','v1',True,True)=='v2'
try: choose('v2','v1',False,False)
except ValueError: pass
else: raise AssertionError('unsafe rollback assumed')
print('unhealthy candidate rolls back only under compatible schema')

# Bounded exercise variation
try: choose('v2','v1',True,False)
except ValueError: pass
else: raise AssertionError('compatibility bypassed')
print("Exercise variation: PASS")
