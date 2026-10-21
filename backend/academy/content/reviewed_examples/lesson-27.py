def retry(code,attempts,queued,capacity=10):
    return code in {'timeout','database_busy'} and attempts<3 and queued<capacity
assert retry('timeout',0,0)
assert not retry('unsupported_file',0,0)
assert not retry('timeout',3,0)
assert not retry('timeout',0,10)
print('transient retry bounded by attempts and queue pressure')

# Bounded exercise variation
assert retry('timeout',2,9)
assert not retry('timeout',3,9)
print("Exercise variation: PASS")
