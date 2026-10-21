def measurement(start,end,usage=None):
    if end<start: raise ValueError('clock went backward')
    return {'elapsed_ms':(end-start)*1000,'tokens':usage,'usage_status':'measured' if usage is not None else 'unknown'}
a=measurement(1,1.25)
assert a['elapsed_ms']==250 and a['tokens'] is None
assert measurement(1,2,0)['usage_status']=='measured'
print('elapsed=250 ms fixture; missing usage remains unknown')

# Bounded exercise variation
assert measurement(1,2,0)['tokens']==0
assert measurement(1,2)['tokens'] is None
print("Exercise variation: PASS")
