calls=[]
def pipeline(query):
    evidence=[{'id':'p1','text':'14 days'}] if query=='refund' else []
    if not evidence: return {'text':'Insufficient evidence','citations':[]}
    calls.append(evidence)
    answer={'text':evidence[0]['text'],'citations':[evidence[0]['id']]}
    assert set(answer['citations'])<={p['id'] for p in evidence}
    return answer
assert pipeline('refund')['citations']==['p1']
assert pipeline('unknown')['citations']==[] and len(calls)==1
print('evidence traverses pipeline; unknown question bypasses generation')

# Bounded exercise variation
pipeline('unknown');assert len(calls)==1
print("Exercise variation: PASS")
