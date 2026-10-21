store={'docs':{'a':'private','b':'other'},'chunks':[{'doc':'a'},{'doc':'b'}],'cache':{'a:question':'answer','b:question':'other'}}
def delete(document):
    store['docs'].pop(document,None)
    store['chunks'][:]=[c for c in store['chunks'] if c['doc']!=document]
    for key in list(store['cache']):
        if key.split(':',1)[0]==document: del store['cache'][key]
delete('a')
assert 'a' not in store['docs'] and store['chunks']==[{'doc':'b'}]
assert list(store['cache'])==['b:question']
print('document, chunks and cached answers deleted; unrelated data retained')

# Bounded exercise variation
delete('a');assert store['docs']=={'b':'other'}
print("Exercise variation: PASS")
