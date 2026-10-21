def context(rows,org,budget):
    out=[];used=0
    for row in rows:
        if row['org']!=org or used+len(row['text'])>budget: continue
        out.append(row);used+=len(row['text'])
    return out
rows=[{'id':'secret','org':'two','text':'x'},{'id':'a','org':'one','text':'14 days'},{'id':'b','org':'one','text':'unused only'}]
assert [r['id'] for r in context(rows,'one',10)]==['a']
assert context(rows,'unknown',100)==[]
print('scope filtered before bounded context selection')

# Bounded exercise variation
assert [r['id'] for r in context(rows,'one',18)]==['a','b']
print("Exercise variation: PASS")
