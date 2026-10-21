def validate(message):
    if set(message)!={'task','evidence_ids'}: raise ValueError('fields')
    if type(message['task']) is not str or not message['task']: raise ValueError('task')
    if type(message['evidence_ids']) is not list or any(type(i) is not str for i in message['evidence_ids']): raise ValueError('evidence')
    return message
assert validate({'task':'answer refund','evidence_ids':['p1']})['evidence_ids']==['p1']
try: validate({'task':'answer refund','evidence_ids':'p1'})
except ValueError: pass
else: raise AssertionError('malformed handoff accepted')
print('typed handoff accepted; ambiguous evidence representation rejected')

# Bounded exercise variation
try: validate({'task':'answer','evidence_ids':['p1'],'write_permission':True})
except ValueError: pass
else: raise AssertionError('authority field accepted')
print("Exercise variation: PASS")
