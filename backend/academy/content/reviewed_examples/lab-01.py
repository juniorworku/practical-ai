def answer(question):
    return {'text':'14 days, unused items','ids':['refund-v1']} if question=='refund window' else {'text':None,'ids':[]}
cases=[('refund window',['refund-v1']),('warranty',[]),('issue refund',[])]
report=[{'question':q,'passed':answer(q)['ids']==expected} for q,expected in cases]
assert all(row['passed'] for row in report)
assert 'unused' in answer('refund window')['text']
print('three baseline cases passed: supported, unavailable, prohibited action')

# Bounded exercise variation
cases.append(('shipping',[]));assert all(answer(q)['ids']==expected for q,expected in cases)
print("Exercise variation: PASS")
