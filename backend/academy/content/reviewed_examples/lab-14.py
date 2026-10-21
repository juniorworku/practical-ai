report={'grounding':'pass','isolation':'pass','restore':'untested','public_https':'untested'}
def ready(r): return all(r[k]=='pass' for k in ['grounding','isolation','restore'])
assert not ready(report)
report['restore']='pass';assert ready(report)
assert report['public_https']=='untested'
print('handoff keeps untested public deployment visible; local pilot gate distinct')

# Bounded exercise variation
report['isolation']='fail';assert not ready(report)
print("Exercise variation: PASS")
