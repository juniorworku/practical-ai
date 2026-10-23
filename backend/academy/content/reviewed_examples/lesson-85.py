from copy import deepcopy
def validate(value):
    if type(value) is not dict or set(value)!={'action','query','source_id'}: raise ValueError('shape')
    if value['action']=='search':
        if type(value['query']) is not str or not 3<=len(value['query'])<=200 or value['source_id'] is not None: raise ValueError('search')
    elif value['action']=='finish':
        if value['query'] is not None or not (value['source_id'] is None or type(value['source_id']) is str and 1<=len(value['source_id'])<=100): raise ValueError('finish')
    else: raise ValueError('denied action')
    return value
def decide(question,observations,request):
    return validate(request({'question':question,'observations':deepcopy(list(observations))}))
result=decide('refund',[],lambda payload:{'action':'search','query':'refund','source_id':None})
assert result['action']=='search'
try: validate({'action':'delete','query':None,'source_id':None})
except ValueError: pass
else: raise AssertionError('model granted authority')
print('injected transport exercised; model proposal validated before execution')

# Bounded exercise variation
try: validate({'action':'finish','query':'refund','source_id':'p1'})
except ValueError: pass
else: raise AssertionError('invalid finish accepted')
original=[{'sources':[{'id':'p1','text':'14 days'}]}]
def mutating_transport(payload):
    payload['observations'][0]['sources'][0]['text']='90 days'
    return {'action':'finish','query':None,'source_id':'p1'}
assert decide('refund',original,mutating_transport)['action']=='finish'
assert original[0]['sources'][0]['text']=='14 days'

print("Exercise variation: PASS")
