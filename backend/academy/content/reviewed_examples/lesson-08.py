EXAMPLE={'answer':'30 days','id':'demo'}
def render(evidence):
    return {'answer':evidence['text'],'id':evidence['id']} if evidence else {'answer':'Insufficient evidence','id':None}
assert render({'text':'14 days','id':'current'})=={'answer':'14 days','id':'current'}
assert render(None)['id'] is None
print('current evidence selected; demonstration not treated as policy')

# Bounded exercise variation
assert render({'text':'7 days','id':'current-v2'})['answer']=='7 days'
print("Exercise variation: PASS")
