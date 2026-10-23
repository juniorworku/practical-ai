"""Local hybrid-routing SaaS: two transparent adapters, actual persisted sources."""
import re,hashlib,json
KIND='engineering'
VERSION='engineering-router-v2'
def select_context(text,documents,budget=700):
 """Owner filtering is the caller's responsibility, before passing documents."""
 terms=set(re.findall(r'[a-z]+',text.lower()))
 ranked=[]
 for document in documents:
  # A blank-line-delimited evidence unit must retain its rule and exceptions.
  # Oversized relevant units require a reviewed split, never silent truncation.
  for position,unit in enumerate(document['text'].split('\n\n')):
   unit=unit.strip()
   score=len(terms & set(re.findall(r'[a-z]+',unit.lower())))
   if score:ranked.append((score,document['id']+':'+str(position),unit,document['revision']))
 ranked.sort(key=lambda row:(-row[0],row[1]));selected=[];used=0
 if any(len(row[2])>budget for row in ranked):
  raise ValueError('relevant evidence unit needs a reviewed split')
 for score,id,chunk,revision in ranked:
  if used+len(chunk)<=budget:selected.append((id,chunk,revision));used+=len(chunk)
 return selected,used

def process(text,mode,documents):
 terms=set(re.findall(r'[a-z]+',text.lower()))
 if terms & {'send','delete','schedule'}:return {'status':'denied','text':None,'citations':[],'trace':['permission_gate']}
 if mode=='timeout':raise TimeoutError('fixture')
 if mode=='malformed':raise ValueError('fixture')
 # The tokenizer is an explicit word baseline, not measured model tokens.
 try:selected,used=select_context(text,documents)
 except ValueError:
  return {'status':'needs_correction','text':None,'citations':[],
          'issues':['relevant_evidence_unit_exceeds_700_characters'],
          'trace':['owner_filter','paragraph_units','rank','reviewed_split_required']}
 if not selected:return {'status':'abstain','text':None,'citations':[],'context_chars':0,'trace':['owner_filter','paragraph_units','rank','no_evidence']}
 model='reasoning_fixture' if terms & {'compare','exceptions','conflict'} else 'routine_fixture'
 # Both use a source-extractive fixture so the complete path is reproducible.
 answer=' '.join(row[1] for row in selected)
 cache_inputs={'model':model,'pipeline':VERSION,'query':text,
               'evidence':[(row[0],row[2]) for row in selected]}
 cache_key=hashlib.sha256(json.dumps(cache_inputs,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return {'status':'needs_review','text':answer,'citations':[r[0] for r in selected], 'model':model,'context_chars':used,'cache_key':cache_key,'cache_hit':False,'trace':['owner_filter','paragraph_units','rank','context_budget','route_'+model,'validated_draft','await_review']}
