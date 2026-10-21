def fuse(rankings,offset=60):
    scores={}
    for ranking in rankings:
        unique=list(dict.fromkeys(ranking))
        for rank,item in enumerate(unique,1): scores[item]=scores.get(item,0)+1/(offset+rank)
    return sorted(scores,key=lambda item:(-scores[item],item))
assert fuse([['a','b'],['b','a']])==['a','b']
assert fuse([['a','a','b']])==['a','b']
print('ranks fused with stable ties and no duplicate votes')

# Bounded exercise variation
assert fuse([['a','b'],['b','a'],['b']])[0]=='b'
print("Exercise variation: PASS")
