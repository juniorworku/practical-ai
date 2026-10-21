calls=[]
def rerank(rows,score,limit=2):
    return sorted(rows[:limit],key=lambda r:(-score(r),r['id']))
def fixture(row): calls.append(row['id']);return row['relevance']
rows=[{'id':'a','relevance':0},{'id':'b','relevance':1},{'id':'c','relevance':2}]
result=rerank(rows,fixture)
assert [r['id'] for r in result]==['b','a'] and len(calls)==2
print('two scorer calls; included relevant candidate promoted')

# Bounded exercise variation
calls.clear();assert rerank(rows,fixture,3)[0]['id']=='c';assert len(calls)==3
print("Exercise variation: PASS")
