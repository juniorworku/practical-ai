def answer(question):
    if question == 'refund window':
        return {'text':'14 days for unused items', 'sources':['policy-v1']}
    return {'text':'Insufficient evidence', 'sources':[]}
assert answer('refund window')['text'] == '14 days for unused items'
assert answer('issue a refund')['sources'] == []
print('supported policy preserved; unsupported action abstained')

# Bounded exercise variation
assert answer('warranty')['text'] == 'Insufficient evidence'
assert 'unused' in answer('refund window')['text']
print("Exercise variation: PASS")
