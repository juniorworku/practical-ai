"""Operate actual student containers: restart, outage, restore and quota behavior."""
import json,subprocess,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/academy/content/capstones';report=[]
def compose(folder,project,*args,input=None):
 result=subprocess.run(['docker','compose','-p',project,*args],cwd=folder,input=input,capture_output=True,timeout=100)
 if result.returncode:raise RuntimeError(result.stderr.decode()[-1800:])
 return result.stdout

def http(port,path,token=None):
 request=urllib.request.Request(f'http://127.0.0.1:{port}'+path,headers={'Authorization':'Bearer '+token} if token else {})
 try:
  with urllib.request.urlopen(request,timeout=6) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as error:return error.code,json.load(error)

def ready(port,path):
 deadline=time.monotonic()+45
 while time.monotonic()<deadline:
  try:
   if http(port,path)[0]==200:return
  except (OSError,ValueError):pass
  time.sleep(.3)
 raise AssertionError('readiness did not recover')

for slug,name,port,kind in [('ai-agent-bootcamp','boot',8211,'bootcamp'),('ai-workshops','workshop',8212,'workshops'),('ai-engineering-12-week','engineering',8214,'engineering')]:
 folder=BASE/slug;project='capstone-'+name;observed=json.loads(Path('/tmp/capstone-'+kind+'-observed.json').read_text());path='/api/records/'+observed['draft_id']+'/'
 original=http(port,path,'student-one')[1]
 compose(folder,project,'up','-d','--force-recreate','--wait','api')
 assert http(port,path,'student-one')[1]==original
 compose(folder,project,'stop','db')
 try:assert http(port,'/api/health/')[0]==503
 finally:compose(folder,project,'start','db')
 ready(port,'/api/health/');assert http(port,path,'student-one')[1]==original
 restored='capstone_restore_'+str(time.time_ns())
 dump=compose(folder,project,'exec','-T','db','pg_dump','-U','learner','-d','capstone','-Fc')
 compose(folder,project,'exec','-T','db','createdb','-U','learner',restored)
 compose(folder,project,'exec','-T','db','pg_restore','-U','learner','-d',restored,input=dump)
 query='SELECT id,owner,kind,payload FROM records ORDER BY id'
 source=compose(folder,project,'exec','-T','db','psql','-U','learner','-d','capstone','-At','-c',query)
 copy=compose(folder,project,'exec','-T','db','psql','-U','learner','-d',restored,'-At','-c',query)
 assert source==copy and source
 # Saturate this synthetic owner's minute bucket through the actual shared table.
 compose(folder,project,'exec','-T','db','psql','-U','learner','-d','capstone','-c',"INSERT INTO quota(owner,bucket,count) VALUES('one',floor(extract(epoch from now())/60),120) ON CONFLICT(owner,bucket) DO UPDATE SET count=120")
 code,error=http(port,path,'student-one');assert code==429 and error['error']=='quota_exceeded'
 compose(folder,project,'exec','-T','db','psql','-U','learner','-d','capstone','-c','DELETE FROM quota')
 assert http(port,path,'student-one')[0]==200
 row={'program':slug,'container_replacement_readback':True,'database_outage_503':True,'recovery_same_id':True,'actual_pg_dump_restore_equal':True,'shared_quota_429':True,'quota_recovery':True,'acceptance_checks':len(observed['checks']),'latency_report':{k:observed[k] for k in ['p50_ms','p95_ms','requests']}}
 report.append(row);print('PASS operational capstone:',slug,flush=True)
(ROOT/'docs/capstone-operations.json').write_text(json.dumps(report,indent=2)+'\n')
