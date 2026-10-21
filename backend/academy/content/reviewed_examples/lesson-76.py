def review(draft,evidence): return draft['text']==evidence['text']
draft={'text':'90 days','confidence':.99};evidence={'id':'p1','text':'14 days'}
assert not review(draft,evidence)
assert review({'text':'14 days','confidence':.1},evidence)
print('evidence outranks builder confidence in controlled fixture review')

# Bounded exercise variation
draft['confidence']=1;assert not review(draft,evidence)
print("Exercise variation: PASS")
