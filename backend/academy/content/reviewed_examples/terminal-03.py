def select(ids,capacity):
    if type(capacity) is not int or capacity<0: raise ValueError('capacity')
    return ids[:capacity]
ids=['p1','p2','p3']
assert select(ids,2)==['p1','p2'] and ids==['p1','p2','p3']
try: select(ids,-1)
except ValueError: pass
else: raise AssertionError('negative capacity accepted')
print('bounded evidence selection; original input preserved')

# Bounded exercise variation
assert select(ids,0)==[]
assert select(ids,10)==ids and select(ids,10) is not ids
print("Exercise variation: PASS")
