def repair(builder,limit=2):
    for attempt in range(1,limit+1):
        text=builder(attempt)
        if text=='14 days': return {'verdict':'accepted','attempts':attempt}
    return {'verdict':'rejected','attempts':limit}
assert repair(lambda n:'90 days' if n==1 else '14 days')=={'verdict':'accepted','attempts':2}
assert repair(lambda n:'90 days')['verdict']=='rejected'
print('repair succeeds within two attempts; uncorrected draft remains rejected')

# Bounded exercise variation
assert repair(lambda n:'90 days' if n==1 else '14 days',1)['verdict']=='rejected'
print("Exercise variation: PASS")
