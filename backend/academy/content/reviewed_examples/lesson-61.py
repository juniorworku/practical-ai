def run(budget=2):
    observation=None;trace=[]
    for step in range(budget):
        action='search' if observation is None else 'finish';trace.append(action)
        if action=='search': observation={'id':'p1','text':'14 days'}
        else: return {'status':'completed','citation':observation['id'],'trace':trace}
    return {'status':'step_budget','trace':trace}
assert run()['trace']==['search','finish']
assert run(1)['status']=='step_budget'
print('search precedes finish; step exhaustion is explicit')

# Bounded exercise variation
assert 'citation' not in run(1)
print("Exercise variation: PASS")
