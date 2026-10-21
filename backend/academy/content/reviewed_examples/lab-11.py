run={'dataset':'v1','prompt':'p1','source':'policy-v1','spans':[('retrieval',10),('generation',80),('validation',5)],'tokens':None,'quality_pass':False}
assert sum(ms for stage,ms in run['spans'])==95
assert run['tokens'] is None and not run['quality_pass']
assert {'dataset','prompt','source'}<=run.keys()
print('95 ms synthetic sequential path; usage unknown; quality failure retained')

# Bounded exercise variation
run['spans'].append(('retry',20));assert sum(ms for stage,ms in run['spans'])==115
print("Exercise variation: PASS")
