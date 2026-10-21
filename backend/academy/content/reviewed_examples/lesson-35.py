from math import sqrt
def normalize(vector):
    norm=sqrt(sum(x*x for x in vector))
    if not norm: raise ValueError('zero vector')
    return [x/norm for x in vector]
assert normalize([3,4])==[0.6,0.8]
try: normalize([0,0])
except ValueError: pass
else: raise AssertionError('undefined direction accepted')
model={'name':'fixture-v1','dimensions':2}
assert len(normalize([3,4]))==model['dimensions']
print('vector normalized; zero vector rejected; dimension recorded')

# Bounded exercise variation
assert normalize([2])==[1.0]
assert len(normalize([2]))!=model['dimensions']
print("Exercise variation: PASS")
