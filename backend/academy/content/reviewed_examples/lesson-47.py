human=[True,False,False];judge=[True,True,False]
agreement=sum(a==b for a,b in zip(human,judge))/len(human)
false_accept=sum(not a and b for a,b in zip(human,judge))
assert agreement==2/3 and false_accept==1
print('agreement=2/3; false accepts=1; disagreement needs review')

# Bounded exercise variation
always=[True]*3
assert sum(not a and b for a,b in zip(human,always))==2
print("Exercise variation: PASS")
