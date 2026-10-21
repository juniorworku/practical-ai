def valid(case):
    return bool(case['id']) and (bool(case['relevant']) if case['category']=='answerable' else not case['relevant'])
cases=[{'id':'refund','question':'refund window?','relevant':['p1'],'category':'answerable'},
       {'id':'warranty','question':'warranty length?','relevant':[],'category':'unanswerable'}]
assert all(valid(c) for c in cases)
assert len({c['id'] for c in cases})==len(cases)
assert not valid({'id':'bad','relevant':[],'category':'answerable'})
print('positive and abstention fixtures labeled; inconsistent label rejected')

# Bounded exercise variation
assert valid({'id':'shipping','relevant':[],'category':'unanswerable'})
print("Exercise variation: PASS")
