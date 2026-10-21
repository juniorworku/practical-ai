def ask(question,document):
    if type(question) is not str or not 3<=len(question.strip())<=200: raise ValueError('question')
    if document['state']!='ready': return {'status':'pending','ids':[]}
    return {'status':'answer','ids':[document['id']],'text':document['text']}
doc={'id':'p1','state':'ready','text':'14 days'}
assert ask('refund',doc)['ids']==['p1']
assert ask('refund',{**doc,'state':'indexing'})['status']=='pending'
try: ask(12,doc)
except ValueError: pass
else: raise AssertionError('invalid request accepted')
print('validated service gates answer on durable readiness state')

# Bounded exercise variation
assert ask('refund',{**doc,'state':'failed'})['ids']==[]
print("Exercise variation: PASS")
