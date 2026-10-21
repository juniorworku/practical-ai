rows=[{'query':'refund','baseline':.5,'hybrid':1.0},{'query':'exception','baseline':1.0,'hybrid':.5}]
regressions=[r['query'] for r in rows if r['hybrid']<r['baseline']]
assert regressions==['exception']
mean_gain=sum(r['hybrid']-r['baseline'] for r in rows)/len(rows)
assert mean_gain==0
print('mean gain=0; exception-query regression retained')

# Bounded exercise variation
rows.append({'query':'support','baseline':0,'hybrid':1});assert sum(r['hybrid']-r['baseline'] for r in rows)>0
assert [r['query'] for r in rows if r['hybrid']<r['baseline']]==['exception']
print("Exercise variation: PASS")
