import math
import statistics
import time

rows=[]
for name,critical,run in [('valid',False,lambda:'a1'),('outage',False,lambda:1/0),('owner-denied',True,lambda:None)]:
    started=time.perf_counter()
    try:
        value=run();passed=value==({'valid':'a1','owner-denied':None}.get(name));error=None
    except Exception as failure:passed=False;error=type(failure).__name__
    rows.append({'id':name,'critical':critical,'passed':passed,'error':error,'ms':(time.perf_counter()-started)*1000})
times=sorted(r['ms'] for r in rows)
assert len(times)==3 and rows[1]['error']=='ZeroDivisionError'
assert not all(r['passed'] for r in rows), 'outages cannot vanish from the gate'
print({'p50_ms':statistics.median(times),'p95_ms':times[math.ceil(.95*len(times))-1],
       'failed':[r['id'] for r in rows if not r['passed']], 'population':'all three real local attempts',
       'cost':None,'semantic_quality':'unmeasured'})
# Three observations teach a calculation and failure accounting, not stable p95.
