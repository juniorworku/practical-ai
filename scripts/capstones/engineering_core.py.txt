"""Local hybrid-routing SaaS: two transparent adapters, actual persisted sources."""
import re,hashlib
KIND='engineering'
VERSION='engineering-router-v1'
def process(text,mode,documents):
 terms=set(re.findall(r'[a-z]+',text.lower()))
 if terms & {'send','delete','schedule'}:return {'status':'denied','text':None,'citations':[],'trace':['permission_gate']}
 if mode=='timeout':raise TimeoutError('fixture')
 if mode=='malformed':raise ValueError('fixture')
 # The tokenizer is an explicit word baseline, not measured model tokens.
 ranked=[]
 for document in documents:
  for position,start in enumerate(range(0,len(document['text']),350)):
   chunk=document['text'][start:start+350]
   score=len(terms & set(re.findall(r'[a-z]+',chunk.lower())))
   if score:ranked.append((score,document['id']+':'+str(position),chunk,document['revision']))
 ranked.sort(key=lambda row:(-row[0],row[1]));selected=[];used=0
 for score,id,chunk,revision in ranked:
  if used+len(chunk)<=700:selected.append((id,chunk,revision));used+=len(chunk)
 if not selected:return {'status':'abstain','text':None,'citations':[],'context_chars':0,'trace':['owner_filter','chunk','rank','no_evidence']}
 model='reasoning_fixture' if terms & {'compare','exceptions','conflict'} else 'routine_fixture'
 # Both use a source-extractive fixture so the complete path is reproducible.
 answer=' '.join(row[1] for row in selected)
 cache_key=hashlib.sha256((model+VERSION+text+str([(r[0],r[2]) for r in selected])).encode()).hexdigest()
 return {'status':'needs_review','text':answer,'citations':[r[0] for r in selected], 'model':model,'context_chars':used,'cache_key':cache_key,'cache_hit':False,'trace':['owner_filter','chunk','rank','context_budget','route_'+model,'validated_draft','await_review']}
