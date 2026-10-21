def searchable(document):
    return document['state']=='ready'
doc={'id':'doc1','state':'accepted'}
assert not searchable(doc)
doc['state']='ready';assert searchable(doc)
doc['state']='failed';assert not searchable(doc)
print('accepted and failed are not searchable; ready is searchable')

# Bounded exercise variation
assert not searchable({'id':'doc2','state':'indexing'})
print("Exercise variation: PASS")
