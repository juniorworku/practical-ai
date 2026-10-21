required=['tests','evaluation','recovery']
def assess(report):
    return 'pilot' if all(report.get(k)=='observed_pass' for k in required) else 'blocked'
report={'tests':'observed_pass','evaluation':'observed_pass','recovery':'unknown'}
assert assess(report)=='blocked'
report['recovery']='observed_pass';assert assess(report)=='pilot'
print('unknown recovery blocks release; complete fixture evidence permits pilot only')

# Bounded exercise variation
report['evaluation']='failed';assert assess(report)=='blocked'
print("Exercise variation: PASS")
