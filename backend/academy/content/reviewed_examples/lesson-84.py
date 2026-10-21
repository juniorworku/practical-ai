def consume(result):
    if result.get('is_error') is not False: raise ValueError('tool failed')
    if type(result.get('text')) is not str: raise ValueError('malformed content')
    return result['text']
assert consume({'is_error':False,'text':'14 days'})=='14 days'
try: consume({'is_error':True,'text':'looks like an answer'})
except ValueError: pass
else: raise AssertionError('error treated as evidence')
print('successful content accepted; error envelope never used as evidence')

# Bounded exercise variation
try: consume({'text':'14 days'})
except ValueError: pass
else: raise AssertionError('unknown status treated as success')
print("Exercise variation: PASS")
