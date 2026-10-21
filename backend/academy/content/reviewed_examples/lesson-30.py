def tool(arguments):
    if set(arguments)!={'query','limit'}: raise ValueError('unknown arguments')
    if type(arguments['query']) is not str or not 3<=len(arguments['query'])<=1000: raise ValueError('query')
    if type(arguments['limit']) is not int or not 1<=arguments['limit']<=10: raise ValueError('limit')
    return {'query':arguments['query'],'limit':arguments['limit']}
assert tool({'query':'refund','limit':3})['limit']==3
try: tool({'query':'refund','limit':3,'delete':True})
except ValueError: pass
else: raise AssertionError('write authority accepted')
print('bounded read-only arguments accepted; extra authority rejected')

# Bounded exercise variation
try: tool({'query':'refund','limit':True})
except ValueError as error: assert str(error)=='limit'
else: raise AssertionError('boolean limit accepted')
print("Exercise variation: PASS")
