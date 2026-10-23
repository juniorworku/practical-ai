import statistics
import math

cases = [('supported','a1','a1'), ('missing',None,None), ('isolation',None,'b1'), ('empty',None,None)]
correct = sum(expected == observed for _,expected,observed in cases)
latency_ms = [10,12,20,80]
rank = max(0, math.ceil(.95*len(latency_ms))-1)
report = {'cases':len(cases),'source_accuracy':correct/len(cases),
          'p50_ms':statistics.median(latency_ms),'p95_ms':sorted(latency_ms)[rank],
          'failed':[name for name,expected,observed in cases if expected != observed],
          'measurement':'synthetic fixture, not provider timings'}
assert report['source_accuracy'] == .75
assert report['failed'] == ['isolation']
assert report['p95_ms'] == 80
print(report)
# Deterministic source checks do not certify that generated claims are faithful.
