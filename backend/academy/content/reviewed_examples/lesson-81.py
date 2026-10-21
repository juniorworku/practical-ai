trace=[]
def exercise(discovered):
    trace.append('discover')
    if 'search_policies' not in discovered: raise ValueError('required capability missing')
    trace.append('call');return {'is_error':False,'ids':['p1']}
assert exercise(['search_policies'])['ids']==['p1']
assert trace==['discover','call']
try: exercise([])
except ValueError: pass
else: raise AssertionError('missing tool called')
print('client sequence checked; missing capability blocked before call')

# Bounded exercise variation
assert trace.count('call')==1
print("Exercise variation: PASS")
