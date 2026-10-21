def scrub(event):
    return {key:event[key] for key in ['release','request_id','category'] if key in event}
raw={'release':'v1','request_id':'r1','category':'timeout','prompt':'PRIVATE','unexpected_secret':'SYNTHETIC'}
clean=scrub(raw)
assert clean=={'release':'v1','request_id':'r1','category':'timeout'}
assert 'PRIVATE' not in str(clean) and 'SYNTHETIC' not in str(clean)
print('allowlisted diagnostic fields retained; sensitive payload omitted')

# Bounded exercise variation
assert 'document' not in scrub({**raw,'document':'PRIVATE'})
print("Exercise variation: PASS")
