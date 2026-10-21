def select(passages,budget):
    out=[];seen=set();used=0
    for p in passages:
        if p['id'] in seen or used+len(p['text'])>budget: continue
        out.append(p);seen.add(p['id']);used+=len(p['text'])
    return out
passages=[{'id':'a','text':'14 days'},{'id':'a','text':'14 days'},{'id':'b','text':'unused items only'}]
assert [p['id'] for p in select(passages,10)]==['a']
assert select(passages,0)==[]
print('whole passage a retained once; evidence budget respected')

# Bounded exercise variation
assert [p['id'] for p in select(passages,24)]==['a','b']
print("Exercise variation: PASS")
