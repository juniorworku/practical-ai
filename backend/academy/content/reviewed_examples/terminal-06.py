calls=[]
def execute(name,query):
    if name!='search': raise ValueError('denied')
    if type(query) is not str or not query.strip(): raise ValueError('query')
    calls.append(name);return ['p1'] if query=='refund' else []
assert execute('search','refund')==['p1']
try: execute('delete','all')
except ValueError: pass
else: raise AssertionError('unsafe call executed')
assert calls==['search']
print('read-only application tool exercised; no protocol claim')

# Bounded exercise variation
assert execute('search','warranty')==[] and calls==['search','search']
print("Exercise variation: PASS")
