def select(ids,capacity):
    if type(capacity) is not int or capacity<0: raise ValueError('capacity')
    return ids[:capacity]
ids=['p1','p2','p3']
assert select(ids,2)==['p1','p2']
assert select(ids,0)==[]
assert len(ids)==3
print('two sources selected; empty capacity; original retained')
