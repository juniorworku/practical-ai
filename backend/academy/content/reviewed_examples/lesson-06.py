def available(window,instructions,question,output):
    remaining=window-instructions-question-output
    if min(window,instructions,question,output)<0 or remaining<0: raise ValueError('context overflow')
    return remaining
assert available(100,10,20,30)==40
try: available(100,10,20,80)
except ValueError: pass
else: raise AssertionError('overflow accepted')
print('40 units for evidence; overflow rejected')

# Bounded exercise variation
assert available(100,10,20,40)==30
print("Exercise variation: PASS")
