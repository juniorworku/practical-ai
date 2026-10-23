import json

def select(owner, query, rows, budget=180, output_reserve=40):
    if output_reserve<0 or budget<=output_reserve:raise ValueError('invalid allocation')
    # Exact bytes of this local serialization only, not the provider chat template.
    envelope={'instruction':'Answer only from evidence','query':query,'evidence':[]}
    if len(json.dumps(envelope,ensure_ascii=False).encode())+output_reserve>budget:raise ValueError('query exceeds allowance')
    eligible=sorted((r for r in rows if r['owner']==owner),key=lambda r:r['id'])
    for row in eligible:
        candidate={**envelope,'evidence':[*envelope['evidence'],row]}
        if len(json.dumps(candidate,ensure_ascii=False).encode())+output_reserve<=budget:
            envelope=candidate
    return envelope

rows=[{'id':'a1','owner':'a','text':'Refund: 14 days. Exceptions need review.'},
      {'id':'b1','owner':'b','text':'Private other-owner policy.'}]
selected=select('a','refund',rows,budget=250)
assert [r['id'] for r in selected['evidence']]==['a1']
assert 'Exceptions need review.' in selected['evidence'][0]['text']
assert select('a','refund',rows,budget=160)['evidence']==[]
assert len('😄'.encode())!=len('😄')
print('Aggregate serialization allowance preserves owner scope and whole policy exceptions')
