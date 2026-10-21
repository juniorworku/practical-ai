import hashlib,json
def identity(org,text,parser='v1'):
    return hashlib.sha256(json.dumps([org,text,parser],ensure_ascii=False).encode()).hexdigest()
a=identity('one','14 days')
assert a==identity('one','14 days')
assert a!=identity('one','30 days')
assert a!=identity('two','14 days')
print('stable identity; tenant and content revisions distinct')

# Bounded exercise variation
assert a!=identity('one','14 days','v2')
print("Exercise variation: PASS")
