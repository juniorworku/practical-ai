executed=[]
def execute_plan(plan):
    if any(step not in {'search','finish'} for step in plan): raise ValueError('invalid plan')
    executed.extend(plan)
try: execute_plan(['search','delete'])
except ValueError: pass
else: raise AssertionError('unsafe plan accepted')
assert executed==[]
execute_plan(['search','finish']);assert executed==['search','finish']
print('complete plan validated before any execution')

# Bounded exercise variation
before=list(executed)
try: execute_plan(['search','shell','finish'])
except ValueError: pass
else: raise AssertionError('unknown action accepted')
assert executed==before
print("Exercise variation: PASS")
