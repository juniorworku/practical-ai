def route(state):
    if state['verdict']=='accepted': return 'finish'
    if state['verdict']=='rejected': return 'repair' if state['attempts']<2 else 'failed'
    raise ValueError('unknown verdict')
assert route({'verdict':'accepted','attempts':1})=='finish'
assert route({'verdict':'rejected','attempts':1})=='repair'
assert route({'verdict':'rejected','attempts':2})=='failed'
print('conditional edges distinguish acceptance, repair and exhaustion')

# Bounded exercise variation
try: route({'verdict':'pending','attempts':0})
except ValueError: pass
else: raise AssertionError('undefined edge silently routed')
print("Exercise variation: PASS")
