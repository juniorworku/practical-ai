"""Run 120 concrete HTTP cases with labels held outside the candidate request."""
import concurrent.futures,json,statistics,time
from pathlib import Path
from check import call
BASE='http://127.0.0.1:8214'

def cases():
 rows=[]
 # Twelve variants per family are isolation/input variants, not independent task families.
 for i in range(12):
  rows.extend([
   ('supported',{'input':f'refund policy {i}'},'student-one',201,'needs_review'),
   ('complex',{'input':f'compare refund exceptions {i}'},'student-one',201,'needs_review'),
   ('missing',{'input':f'unicorn wallpaper {i}'},'student-one',201,'abstain'),
   ('denied_write',{'input':f'delete refund {i}'},'student-one',201,'denied'),
   ('wrong_owner',{'input':f'refund policy {i}'},'student-two',201,'abstain'),
   ('unknown_identity',{'input':f'refund policy {i}'},'invalid',401,None),
   ('bad_shape',{'input':'refund','owner':'two'},'student-two',400,None),
   ('blank',{'input':'   '},'student-two',400,None),
   ('timeout',{'input':'refund','mode':'timeout'},'student-two',201,'failed'),
   ('malformed',{'input':'refund','mode':'malformed'},'student-two',201,'failed')])
 return rows

def run_case(case):
 family,body,token,expected_code,expected_state=case;start=time.perf_counter()
 try:
  code,data=call(BASE,'POST','/api/ask/',body,token)
  passed=code==expected_code and (expected_state is None or data.get('status')==expected_state)
  if family=='supported':passed=passed and bool(data.get('citations')) and '14 days' in (data.get('text') or '')
  if family=='complex':passed=passed and data.get('model')=='reasoning_fixture'
  if family=='wrong_owner':passed=passed and not data.get('citations')
  return {'family':family,'passed':bool(passed),'http_status':code,'actual_state':data.get('status'),'elapsed_ms':(time.perf_counter()-start)*1000}
 except (OSError,ValueError) as error:return {'family':family,'passed':False,'error':type(error).__name__,'elapsed_ms':(time.perf_counter()-start)*1000}
if __name__=='__main__':
 # Seed through the public service. Two owners distribute this bounded workload
 # under 120 requests/minute each; run in a fresh quota window after other drills.
 code,document=call(BASE,'POST','/api/documents/',{'source':'evaluation-policy','text':'Refund policy is 14 days for unopened items.'})
 assert code==201
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(run_case,cases()))
 times=sorted(r['elapsed_ms'] for r in rows)
 report={'attempted':len(rows),'passed':sum(r['passed'] for r in rows),'concurrency':4,'p50_ms':statistics.median(times),'p95_ms':times[int(.95*(len(times)-1))],'cost_usd':None,'semantic_model_review':'not_performed','mode':'scripted_adapters_real_http_postgresql','cases':rows}
 Path('evaluation-observed.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='cases'}))
 assert report['passed']==report['attempted']==120,'retain failing report; do not change labels to match candidate'
