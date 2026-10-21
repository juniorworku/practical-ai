def research(run): return {'run':run,'id':'p1','text':'14 days'}
def build(evidence): return {'run':evidence['run'],'citation':evidence['id'],'text':evidence['text']}
def review(draft,evidence):
    return draft['run']==evidence['run'] and draft['citation']==evidence['id'] and draft['text']==evidence['text']
evidence=research('r1');draft=build(evidence)
assert review(draft,evidence)
assert not review({**draft,'text':'90 days'},evidence)
assert not review({**draft,'run':'r2'},evidence)
print('supervised handoff supported; wrong claim and cross-run message rejected')

# Bounded exercise variation
assert not review({**draft,'citation':'fake'},evidence)
print("Exercise variation: PASS")
