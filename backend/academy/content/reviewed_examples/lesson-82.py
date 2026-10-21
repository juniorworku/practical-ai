from contextlib import contextmanager
trace=[]
@contextmanager
def connection():
    trace.append('open')
    try: yield 'session'
    finally: trace.append('close')
try:
    with connection() as session:
        assert session=='session';raise TimeoutError('fixture')
except TimeoutError: pass
assert trace==['open','close']
print('transport resource closed after failed operation')

# Bounded exercise variation
with connection(): pass
assert trace==['open','close','open','close']
print("Exercise variation: PASS")
