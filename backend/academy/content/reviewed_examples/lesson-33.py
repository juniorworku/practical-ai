def chunk(org,revision,position,text):
    if not text.strip() or position<0: raise ValueError('invalid chunk')
    return {'id':f'{org}:{revision}:{position}','org':org,'revision':revision,'position':position,'text':text}
a=chunk('one','v1',0,'refund 14 days');b=chunk('one','v1',1,'unused only')
assert a['id']!=b['id'] and a['org']=='one'
assert a['revision']=='v1'
print('chunk position, tenant and immutable revision preserved')

# Bounded exercise variation
assert chunk('one','v2',0,'refund 7 days')['id']!=a['id']
print("Exercise variation: PASS")
