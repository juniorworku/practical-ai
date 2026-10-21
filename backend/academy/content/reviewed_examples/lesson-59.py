from math import ceil
rows=[{'ms':v,'ok':i!=9} for i,v in enumerate([10,11,12,13,14,15,16,17,18,100])]
def percentile(values,p): return sorted(values)[ceil(p*len(values))-1]
assert percentile([r['ms'] for r in rows],.95)==100
assert sum(not r['ok'] for r in rows)/len(rows)==.1
print('nearest-rank p95=100 ms fixture; error rate=10%')

# Bounded exercise variation
rows.append({'ms':200,'ok':False});assert sum(not r['ok'] for r in rows)==2 and len(rows)==11
print("Exercise variation: PASS")
