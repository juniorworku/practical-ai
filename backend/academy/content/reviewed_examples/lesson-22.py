def route(operation):
    try: return 200,{'answer':operation()}
    except TimeoutError: return 503,{'code':'provider_unavailable','retryable':True}
def unavailable(): raise TimeoutError('private upstream detail')
assert route(lambda:'Insufficient evidence')[0]==200
status,body=route(unavailable)
assert status==503 and body['retryable'] and 'private' not in str(body)
print('abstention=200; upstream timeout=503; private detail omitted')

# Bounded exercise variation
assert route(unavailable)[1]['code']=='provider_unavailable'
print("Exercise variation: PASS")
