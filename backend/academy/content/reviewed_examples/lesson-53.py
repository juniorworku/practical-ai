TRUSTED={'proxy-internal'}
def secure(peer,transport_tls,forwarded_proto):
    return transport_tls or (peer in TRUSTED and forwarded_proto=='https')
assert not secure('public-client',False,'https')
assert secure('proxy-internal',False,'https')
assert secure('public-client',True,None)
print('forged forwarded header ignored; trusted proxy honored')

# Bounded exercise variation
assert not secure('proxy-internal',False,'http')
print("Exercise variation: PASS")
