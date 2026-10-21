def recall(ranked,relevant,k):
    if k<0: raise ValueError('negative k')
    return len(set(ranked[:k])&set(relevant))/len(set(relevant)) if relevant else None
assert recall(['a','b','c'],{'b','c'},2)==0.5
assert recall(['b','b'],{'b','c'},2)==0.5
assert recall([],set(),2) is None
print('recall=0.5; duplicates cannot inflate; no-relevance case undefined')

# Bounded exercise variation
assert recall(['a','b','c'],{'b','c'},3)==1.0
print("Exercise variation: PASS")
