def service(provider):
    try: return {'status':'ok','text':provider()}
    except TimeoutError: return {'status':'retryable_error','text':None}
def timeout(): raise TimeoutError('synthetic')
assert service(timeout)=={'status':'retryable_error','text':None}
assert service(lambda:'14 days')=={'status':'ok','text':'14 days'}
print('timeout exercised through service; recovery verified')

# Bounded exercise variation
def malformed(): raise ValueError('malformed')
try: service(malformed)
except ValueError: pass
else: raise AssertionError('programming/contract failure hidden')
print("Exercise variation: PASS")
