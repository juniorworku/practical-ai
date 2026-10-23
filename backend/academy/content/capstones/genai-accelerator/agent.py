"""A bounded read-only agent integrated with the actual persisted ingestion API."""
import json,os,urllib.request,urllib.error
BASE=os.environ.get('CAPSTONE_URL','http://127.0.0.1:8215')
TOKEN=os.environ.get('CAPSTONE_IDENTITY','demo-one')
def request(method,path,body=None):
 data=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request(BASE+path,data=data,method=method,headers={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)
 except urllib.error.HTTPError as error:raise RuntimeError('service_status_'+str(error.code)) from None

def search(document_id,question):
 return request('POST','/ask',{'document_id':document_id,'question':question})
def scripted(observations):
 return {'name':'finish'} if observations else {'name':'search'}
def valid_evidence(result,document_id):
 # Membership, shape and internal consistency are mechanical checks, not entailment.
 if type(result) is not dict or set(result)!={'mode','answer','citations','context_chars','usage_tokens'}:return False
 if result['mode']!='lexical_fixture' or result['usage_tokens'] is not None:return False
 cites=result['citations'];answer=result['answer'];size=result['context_chars']
 if type(cites) is not list or any(type(c) is not str for c in cites):return False
 if len(cites)!=len(set(cites)):return False
 for citation in cites:
  prefix=document_id+':'
  if not citation.startswith(prefix):return False
  position=citation[len(prefix):]
  if not position.isascii() or not position.isdigit():return False
 if type(size) is not int or not 0<=size<=1000:return False
 if not cites:return answer is None and size==0
 return type(answer) is str and bool(answer.strip()) and len(answer)==size+len(cites)-1 and size>0

def run(document_id,question,decide=scripted,max_steps=2):
 if type(max_steps) is not int or not 1<=max_steps<=5:raise ValueError('max_steps')
 if type(question) is not str or not 3<=len(question.strip())<=200:raise ValueError('question')
 observations=[];trace=[]
 for _ in range(max_steps):
  # Copy rather than let the proposal function modify evidence owned by the host.
  action=decide(tuple(json.loads(json.dumps(observations))))
  if type(action) is not dict or set(action)!={'name'}:return {'status':'invalid_proposal','trace':trace}
  name=action['name'];trace.append(name)
  if name=='search':
   try:result=search(document_id,question)
   except (RuntimeError,OSError,ValueError):return {'status':'service_unavailable','trace':trace}
   if not valid_evidence(result,document_id):return {'status':'invalid_evidence','trace':trace}
   observations.append(result)
  elif name=='finish':
   if not observations:return {'status':'missing_evidence','trace':trace}
   result=observations[-1]
   return {'status':'completed' if result['citations'] else 'abstained','answer':result['answer'],'citations':result['citations'],'trace':trace,'usage_tokens':None}
  else:return {'status':'denied_action','trace':trace}
 return {'status':'step_budget','trace':trace}
