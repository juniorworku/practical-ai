EDGES={'accepted':{'parsing','failed'},'parsing':{'indexing','failed'},'indexing':{'ready','failed'},'ready':set(),'failed':{'accepted'}}
def transition(old,new):
    if new not in EDGES.get(old,set()): raise ValueError('invalid transition')
    return new
assert transition('indexing','ready')=='ready'
try: transition('accepted','ready')
except ValueError: pass
else: raise AssertionError('skipped indexing')
print('legal edge accepted; skipped work rejected')

# Bounded exercise variation
assert transition('failed','accepted')=='accepted'
try: transition('ready','parsing')
except ValueError: pass
else: raise AssertionError('terminal state reopened')
print("Exercise variation: PASS")
