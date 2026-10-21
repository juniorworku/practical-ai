DOCS=[{'id':'a','org':'one','text':'refund 14 days'},{'id':'b','org':'two','text':'refund 90 days'}]
def search(query,authenticated_org):
    scoped=[d for d in DOCS if d['org']==authenticated_org]
    return [d['id'] for d in scoped if query in d['text']]
assert search('refund','one')==['a']
assert search('refund','two')==['b']
print('tenant scope applied before search')

# Bounded exercise variation
assert search('refund','unknown')==[]
print("Exercise variation: PASS")
