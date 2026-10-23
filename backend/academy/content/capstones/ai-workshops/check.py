"""Actual HTTP -> validation -> PostgreSQL -> review -> durable readback checks."""
import argparse,json,time,urllib.request,urllib.error,concurrent.futures,statistics,math
from pathlib import Path

def call(base,method,path,data=None,token='student-one'):
 body=json.dumps(data).encode() if data is not None else None
 request=urllib.request.Request(base+path,data=body,method=method,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=8) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as error:return error.code,json.load(error)

def _check(base,kind,out):
 observations=[]
 def expect(label,condition):
  observations.append({'case':label,'passed':bool(condition)})
  out.write_text(json.dumps({'program':kind,'completed':False,'checks':observations},indent=2))
  if not condition:raise AssertionError(label)
 expect('database_readiness',call(base,'GET','/api/health/')[1]['ready'])
 if kind=='engineering':
  code,doc=call(base,'POST','/api/documents/',{'source':'refund','text':'Refund policy is 14 days for unopened items.'});expect('source_ingested',code==201)
  expect('same_source_same_identity',call(base,'POST','/api/documents/',{'source':'refund','text':'Refund policy is 14 days for unopened items.'})[1]['id']==doc['id'])
 text='Supplier: Studio\nQuantity: 2\nUnit price: 10.00\nCurrency: USD' if kind=='workshops' else 'What is the refund policy?'
 code,draft=call(base,'POST','/api/ask/',{'input':text});expect('candidate_path',code==201 and draft['status']=='needs_review')
 if kind=='workshops':
  expect('exact_total',draft['record']['total']=='20.00')
  expect('missing_price_review',call(base,'POST','/api/ask/',{'input':'Supplier: Studio\nQuantity: 2\nCurrency: USD'})[1]['status']=='needs_correction')
  expect('negative_quantity_rejected',call(base,'POST','/api/ask/',{'input':text.replace('Quantity: 2','Quantity: -2')})[1]['status']=='needs_correction')
 else:
  expect('actual_evidence',bool(draft['citations']) and '14 days' in draft['text'])
  expect('unsupported_abstains',call(base,'POST','/api/ask/',{'input':'unicorn wallpaper'})[1]['status']=='abstain')
  expect('write_denied',call(base,'POST','/api/ask/',{'input':'delete refund records'})[1]['status']=='denied')
  if kind=='engineering':
   routed=call(base,'POST','/api/ask/',{'input':'compare refund exceptions'})[1]
   expect('hybrid_routing',routed['model']=='reasoning_fixture' and draft['model']=='routine_fixture')
   expect('other_owner_no_evidence',call(base,'POST','/api/ask/',{'input':'refund policy'},'student-two')[1]['status']=='abstain')
 expect('unauthorized_identity',call(base,'POST','/api/ask/',{'input':text},'invalid')[0]==401)
 expect('owner_not_model_controlled',call(base,'POST','/api/ask/',{'input':text,'owner':'two'})[0]==400)
 expect('bad_input_rejected',call(base,'POST','/api/ask/',{'input':'  '})[0]==400)
 for mode,error in [('timeout','provider_timeout'),('malformed','invalid_provider_output')]:
  _,failed=call(base,'POST','/api/ask/',{'input':text,'mode':mode})
  expect('failed_'+mode,failed['status']=='failed' and failed['error']==error and failed['text'] is None)
  expect('failure_saved',call(base,'GET','/api/records/'+failed['id']+'/')[1]['error']==error)
 path='/api/records/'+draft['id']+'/'
 expect('stored_readback',call(base,'GET',path)[1]['text']==draft['text'])
 expect('wrong_owner_denied',call(base,'GET',path,token='student-two')[0]==404)
 approval={'version':draft['version'],'digest':draft['approval_digest']}
 expect('student_cannot_approve',call(base,'POST',path+'approve/',approval)[0]==403)
 expect('stale_version_denied',call(base,'POST',path+'approve/',{**approval,'version':0},'reviewer-one')[0]==409)
 expect('changed_payload_denied',call(base,'POST',path+'approve/',{**approval,'digest':'changed'},'reviewer-one')[0]==409)
 code,approved=call(base,'POST',path+'approve/',approval,'reviewer-one')
 expect('reviewed_local_effect',code==200 and approved['external_delivery'] is False)
 # Concurrent duplicate confirmation must observe the same persisted receipt.
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  receipts=list(pool.map(lambda _:call(base,'POST',path+'approve/',approval,'reviewer-one'),range(4)))
 expect('concurrent_replay_same_receipt',all(code==200 and r['receipt']==approved['receipt'] for code,r in receipts))
 expect('receipt_not_approvable',call(base,'POST','/api/records/'+approved['receipt']+'/approve/',approval,'reviewer-one')[0]==409)
 expect('stored_effect_is_scoped',call(base,'GET','/api/records/'+approved['receipt']+'/',token='student-two')[0]==404)
 samples=[]
 for _ in range(12):
  start=time.perf_counter();code,value=call(base,'POST','/api/ask/',{'input':text});samples.append((time.perf_counter()-start)*1000);expect('load_candidate',code==201 and value['status']=='needs_review')
 report={'completed':True,'program':kind,'mode':'local_scripted_provider','document_id':doc['id'] if kind=='engineering' else None,'draft_id':draft['id'],'receipt':approved['receipt'],'checks':observations,'p50_ms':statistics.median(samples),'p95_ms':sorted(samples)[math.ceil(.95*len(samples))-1],'requests':len(samples),'cost_usd':None,'provider_usage_tokens':None,'cloud_load_test':False}
 out.write_text(json.dumps(report,indent=2));print(json.dumps({'passed':len(observations),'program':kind,'report':str(out)}))
def check(base,kind,out):
 out.write_text(json.dumps({'program':kind,'completed':False,'checks':[]}))
 try:return _check(base,kind,out)
 except Exception as error:
  report=json.loads(out.read_text());report.update(completed=False,error_type=type(error).__name__)
  out.write_text(json.dumps(report,indent=2))
  raise  # Retain the original failing assertion/trace and a nonzero exit.

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--base',required=True);parser.add_argument('--kind',required=True);parser.add_argument('--output',type=Path,default=Path('observed.json'));args=parser.parse_args();check(args.base,args.kind,args.output)
