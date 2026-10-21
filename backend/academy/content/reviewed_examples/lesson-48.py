import hashlib,json
def fingerprint(config): return hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
a={'dataset':'v1','prompt':'p1','embedding':'e1','chunk_size':200}
b={**a,'prompt':'p2'}
changed=[k for k in a if a[k]!=b[k]]
assert changed==['prompt'] and fingerprint(a)!=fingerprint(b)
assert fingerprint(a)==fingerprint(dict(reversed(list(a.items()))))
print('one variable changed; stable configuration identities differ')

# Bounded exercise variation
c={**a,'chunk_size':300};assert [k for k in a if a[k]!=c[k]]==['chunk_size']
print("Exercise variation: PASS")
