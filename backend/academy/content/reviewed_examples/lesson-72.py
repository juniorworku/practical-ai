expected={'refund':'answer','unknown':'abstain'}
baseline={'refund':'answer','unknown':'abstain'}
candidate={'refund':'answer','unknown':'answer'}
def accuracy(outputs): return sum(outputs[k]==v for k,v in expected.items())/len(expected)
assert accuracy(baseline)==1 and accuracy(candidate)==.5
calls={'baseline':4,'candidate':2}
assert calls['candidate']<calls['baseline']
print('candidate uses fewer fixture calls but fails abstention; quality regresses')

# Bounded exercise variation
candidate['unknown']='abstain';assert accuracy(candidate)==1
print("Exercise variation: PASS")
