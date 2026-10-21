from copy import deepcopy
def run(question,decide,max_steps=3):
    if type(max_steps) is not int or not 1<=max_steps<=20: raise ValueError('step budget')
    if type(question) is not str or not 3<=len(question)<=200: raise ValueError('question')
    observations=[];trace=[]
    for step in range(max_steps):
        try: action=decide(question,tuple(deepcopy(observations)))
        except TimeoutError: return 'provider_timeout',trace
        if type(action) is not dict or type(action.get('name')) is not str: return 'invalid_decision',trace
        trace.append(action['name'])
        if action['name']=='search':
            if set(action)!={'name','query'} or type(action['query']) is not str or not 3<=len(action['query'].strip())<=200: return 'invalid_arguments',trace
            evidence=[{'id':'p1','text':'14 days'}] if action['query']=='refund' else []
            observations.append(evidence)
        elif action['name']=='finish':
            if set(action)!={'name','id'} or not (action['id'] is None or type(action['id']) is str and 1<=len(action['id'])<=100): return 'invalid_arguments',trace
            if not observations: return 'premature_finish',trace
            evidence=observations[-1]
            if not evidence: return 'abstained',trace
            return ('completed' if action.get('id') in {e['id'] for e in evidence} else 'unsupported_citation'),trace
        else: return 'denied_action',trace
    return 'step_budget',trace

def scripted(question,observations):
    if not observations: return {'name':'search','query':question}
    hits=observations[-1]
    return {'name':'finish','id':hits[0]['id'] if hits else None}
assert run('refund',scripted)==('completed',['search','finish'])
assert run('warranty',scripted)==('abstained',['search','finish'])
assert run('refund',scripted,1)[0]=='step_budget'
assert run('refund',lambda q,o:{'name':'delete'})[0]=='denied_action'
print('scripted agent completed, abstained on empty search and denied unknown authority')

# Bounded exercise variation
def invented(question,observations):
    return {'name':'finish','id':'fake'} if observations else {'name':'search','query':question}
assert run('refund',invented)[0]=='unsupported_citation'
assert run('refund',lambda q,o:{'name':'finish','id':'p1'})[0]=='premature_finish'
def tamper(question,observations):
    if not observations: return {'name':'search','query':question}
    observations[-1].append({'id':'fake','text':'invented'})
    return {'name':'finish','id':'fake'}
assert run('refund',tamper)[0]=='unsupported_citation' 
assert run('refund',lambda q,o:None)[0]=='invalid_decision'
def timeout(q,o): raise TimeoutError('fixture')
assert run('refund',timeout)[0]=='provider_timeout'

print("Exercise variation: PASS")
