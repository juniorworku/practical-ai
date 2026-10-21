def settings(values):
    mode=values.get('mode','fake')
    if mode not in {'fake','real'}: raise ValueError('invalid mode')
    if mode=='real' and not values.get('key'): raise ValueError('key required for real mode')
    return {'mode':mode,'timeout':20}
assert settings({})['mode']=='fake'
try: settings({'mode':'real'})
except ValueError as error: assert str(error)=='key required for real mode'
else: raise AssertionError('missing key accepted')
print('fake explicit; missing real key rejected')

# Bounded exercise variation
value=settings({'mode':'real','key':'SYNTHETIC'})
assert value['mode']=='real' and 'SYNTHETIC' not in str(value)
print("Exercise variation: PASS")
