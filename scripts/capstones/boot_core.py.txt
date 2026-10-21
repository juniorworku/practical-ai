"""A bounded read-only agent with a scripted proposal adapter, never a hidden LLM."""
import re
KIND='bootcamp'
VERSION='support-policy-v1'
POLICIES=[{'id':'refund-v1','text':'Refunds are available within 14 days for unopened items. Opened items are excluded.'}]
def scripted(observation):return {'name':'draft'} if observation else {'name':'search'}
def run(text,mode,decide=scripted,max_steps=2):
 if type(max_steps) is not int or not 1<=max_steps<=5:raise ValueError('step_budget')
 observation=None;trace=['validate']
 for _ in range(max_steps):
  action=decide(dict(observation) if observation else None)
  if type(action) is not dict or set(action)!={'name'}:raise ValueError('action_contract')
  name=action['name'];trace.append(name)
  if name=='search':
   observation=dict(POLICIES[0])
   if len(observation['text'])>512:raise ValueError('context')
  elif name=='draft':
   if not observation:raise ValueError('evidence_required')
   if mode=='timeout':raise TimeoutError('fixture')
   proposal={'text':observation['text'],'citations':[observation['id']]} if mode=='fixture' else {'text':'90 days','citations':['invented']}
   if set(proposal)!={'text','citations'} or proposal['citations']!=[observation['id']] or proposal['text']!=observation['text']:raise ValueError('provider_contract')
   return {'status':'needs_review',**proposal,'context_chars':len(observation['text']),'model':'scripted_fixture','trace':trace+['validated_draft','await_review']}
  else:return {'status':'denied','text':None,'citations':[],'trace':trace}
 return {'status':'failed','error':'step_budget','text':None,'citations':[],'trace':trace}
def process(text,mode,documents):
 terms=set(re.findall(r'[a-z]+',text.lower()))
 if terms & {'send','delete','issue','transfer'}:return {'status':'denied','text':None,'citations':[],'trace':['validate','deny_action']}
 if terms & {'ignore','override'}:return {'status':'abstain','text':None,'citations':[],'trace':['validate','untrusted_instruction']}
 if not terms & {'refund','refunds','opened','unopened'}:return {'status':'abstain','text':None,'citations':[],'trace':['validate','retrieve','no_evidence']}
 return run(text,mode)
if __name__=='__main__':
 assert run('refund','fixture',max_steps=1)['error']=='step_budget'
 assert run('refund','fixture',lambda observation:{'name':'delete'})['status']=='denied'
 try:run('refund','fixture',lambda observation:{'name':'draft'})
 except ValueError:pass
 else:raise AssertionError('draft before evidence')
 print('bounded agent: budget, allowlist and evidence-before-draft checks passed')
