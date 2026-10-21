def generate(request,evidence):
    if not evidence: return {'status':'abstain','text':None}
    try: return {'status':'ok','text':request(evidence),'model':'fixture'}
    except TimeoutError: return {'status':'retryable','text':None}
    except PermissionError: return {'status':'configuration_error','text':None}
def timeout(e): raise TimeoutError()
def denied(e): raise PermissionError()
assert generate(lambda e:e[0],['14 days'])['text']=='14 days'
assert generate(timeout,['14 days'])['status']=='retryable'
assert generate(denied,['14 days'])['status']=='configuration_error'
assert generate(timeout,[])['status']=='abstain'
print('success, timeout, authentication and missing evidence distinguished')

# Bounded exercise variation
assert all(generate(f,['14 days'])['text'] is None for f in [timeout,denied])
print("Exercise variation: PASS")
