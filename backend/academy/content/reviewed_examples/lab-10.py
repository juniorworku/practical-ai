cases=[{'id':'supported','citation':'p1','text':'14 days','supported':True},
       {'id':'invented','citation':'fake','text':'14 days','supported':False},
       {'id':'wrong_fact','citation':'p1','text':'90 days','supported':False}]
report=[{'id':c['id'],'structure':c['citation'] in {'p1'},'semantic':c['supported']} for c in cases]
assert report[1]['structure'] is False
assert report[2]['structure'] is True and report[2]['semantic'] is False
assert sum(r['structure'] and r['semantic'] for r in report)==1
print('unknown citation and unsupported known citation exposed separately')

# Bounded exercise variation
abstention={'id':'missing','citations':[],'answer':None};assert not abstention['citations'] and abstention['answer'] is None
print("Exercise variation: PASS")
