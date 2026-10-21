"""Complete DRF adapter; run only against this capstone's synthetic database."""
import os,json,hashlib,time,uuid
from django.conf import settings
settings.configure(SECRET_KEY=os.environ['DJANGO_SECRET_KEY'],DEBUG=False,
 ALLOWED_HOSTS=['127.0.0.1','localhost','api'],ROOT_URLCONF=__name__,
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':'capstone','USER':'learner','PASSWORD':os.environ['POSTGRES_PASSWORD'],'HOST':'db','PORT':'5432','OPTIONS':{'connect_timeout':3}}},
 INSTALLED_APPS=['rest_framework'],REST_FRAMEWORK={'UNAUTHENTICATED_USER':None})
import django
django.setup()
from django.db import connection,transaction,DatabaseError
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core import process,VERSION,KIND
IDENTITIES={'student-one':('one','student'),'student-two':('two','student'),'reviewer-one':('one','reviewer')}
class Reject(Exception):
 def __init__(self,status,detail):self.status=status;self.detail=detail

def record(owner,kind,payload,key=None):
 id=key or str(uuid.uuid4())
 with connection.cursor() as c:
  c.execute('INSERT INTO records(id,owner,kind,payload) VALUES(%s,%s,%s,%s::jsonb) ON CONFLICT(id) DO NOTHING',[id,owner,kind,json.dumps(payload)])
 return id

def get_record(id,owner,lock=False):
 with connection.cursor() as c:
  c.execute('SELECT kind,payload FROM records WHERE id=%s AND owner=%s'+(' FOR UPDATE' if lock else ''),[id,owner]);row=c.fetchone()
 if not row:raise Reject(404,'not_found')
 return row[0],json.loads(row[1]) if isinstance(row[1],str) else row[1]

def initialize():
 with connection.cursor() as c:
  c.execute('CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY,owner TEXT NOT NULL,kind TEXT NOT NULL,payload JSONB NOT NULL)')
  c.execute('CREATE INDEX IF NOT EXISTS records_owner_kind ON records(owner,kind)')
  c.execute('CREATE TABLE IF NOT EXISTS quota(owner TEXT NOT NULL,bucket BIGINT NOT NULL,count INTEGER NOT NULL,PRIMARY KEY(owner,bucket))')

# Initialize once as an explicit release step, never on each HTTP request.
def identity(request):
 found=IDENTITIES.get(request.headers.get('Authorization','').removeprefix('Bearer '))
 if not found:raise Reject(401,'fixture_identity_required')
 return found

def admit(owner):
 window=int(time.time())//60
 with connection.cursor() as c:
  c.execute('INSERT INTO quota(owner,bucket,count) VALUES(%s,%s,1) ON CONFLICT(owner,bucket) DO UPDATE SET count=quota.count+1 RETURNING count',[owner,window]);count=c.fetchone()[0]
  c.execute('DELETE FROM quota WHERE bucket<%s',[window-2])
 if count>int(os.environ.get('REQUESTS_PER_MINUTE','120')):raise Reject(429,'quota_exceeded')

def exact(body,allowed,required):
 if type(body) is not dict or set(body)-set(allowed) or not set(required)<=set(body):raise Reject(400,'invalid_fields')

def guarded(fn):
 def wrapped(request,*args,**kwargs):
  try:
   owner,role=identity(request);admit(owner)
   return fn(request,owner,role,*args,**kwargs)
  except Reject as error:
   return Response({'error':error.detail},status=error.status,headers={'Retry-After':'60'} if error.status==429 else {})
  except DatabaseError:return Response({'error':'database_unavailable'},status=503)
 return wrapped

@api_view(['GET'])
def health(request):
 try:
  with connection.cursor() as c:c.execute('SELECT count(*) FROM records');c.fetchone()
  return Response({'ready':True,'program':KIND,'version':VERSION,'database':'postgresql'})
 except DatabaseError:return Response({'ready':False},status=503)

@api_view(['POST'])
@guarded
def ask(request,owner,role):
 exact(request.data,['input','mode'],['input'])
 text=request.data['input'];mode=request.data.get('mode','fixture')
 if type(text) is not str or not 3<=len(text.strip())<=1000:raise Reject(400,'input_3_to_1000_characters')
 if mode not in ['fixture','timeout','malformed']:raise Reject(400,'unknown_fixture_mode')
 started=time.perf_counter()
 with connection.cursor() as c:
  c.execute("SELECT payload FROM records WHERE owner=%s AND kind='document' ORDER BY id",[owner]);documents=[json.loads(r[0]) if isinstance(r[0],str) else r[0] for r in c.fetchall()]
 try:result=process(text,mode,documents)
 except TimeoutError:result={'status':'failed','error':'provider_timeout','text':None,'citations':[]}
 except ValueError:result={'status':'failed','error':'invalid_provider_output','text':None,'citations':[]}
 result.update(input=text,version=1,source_version=VERSION,elapsed_ms=round((time.perf_counter()-started)*1000,3),usage_tokens=None,cost_usd=None)
 result['approval_digest']=hashlib.sha256(json.dumps({'text':result.get('text'),'citations':result.get('citations'),'source_version':result['source_version']},sort_keys=True).encode()).hexdigest()
 id=record(owner,'draft',result);return Response({'id':id,**result},status=201)

@api_view(['GET'])
@guarded
def detail(request,owner,role,id):
 kind,payload=get_record(id,owner);return Response({'id':id,'kind':kind,**payload})

@api_view(['POST'])
@guarded
def approve(request,owner,role,id):
 if role!='reviewer':raise Reject(403,'reviewer_required')
 exact(request.data,['version','digest'],['version','digest'])
 if type(request.data['version']) is not int or type(request.data['digest']) is not str:raise Reject(400,'invalid_approval')
 with transaction.atomic():
  kind,payload=get_record(id,owner,True)
  digest=hashlib.sha256(json.dumps({'text':payload.get('text'),'citations':payload.get('citations'),'source_version':payload.get('source_version')},sort_keys=True).encode()).hexdigest()
  if request.data['version']!=payload['version'] or request.data['digest']!=digest:raise Reject(409,'approval_payload_changed')
  if kind!='draft' or payload['status'] not in ['needs_review','approved']:raise Reject(409,'draft_not_approvable')
  # One row lock and transaction bind the decision to the exact stored draft.
  receipt='effect:'+id
  if payload['status']=='needs_review':
   record(owner,'local_effect',{'draft_id':id,'text':payload['text'],'destination':'local_reviewed_outbox'},receipt)
   payload.update(status='approved',receipt=receipt)
   with connection.cursor() as c:c.execute('UPDATE records SET payload=%s::jsonb WHERE id=%s',[json.dumps(payload),id])
 return Response({'receipt':receipt,'status':'approved','external_delivery':False})

@api_view(['POST'])
@guarded
def documents(request,owner,role):
 if KIND!='engineering':raise Reject(404,'route_not_in_program')
 exact(request.data,['text','source'],['text','source'])
 text=request.data['text'];source=request.data['source']
 if type(text) is not str or not 1<=len(text)<=10000 or not text.strip() or type(source) is not str or not 1<=len(source)<=60:raise Reject(400,'invalid_document')
 digest=hashlib.sha256(text.encode()).hexdigest()
 id='doc:'+owner+':'+digest
 record(owner,'document',{'id':id,'source':source,'revision':digest,'text':text},id)
 return Response({'id':id,'state':'ready','revision':digest},status=201)

def index(request):return HttpResponse(open('index.html').read(),content_type='text/html')
urlpatterns=[path('',index),path('api/health/',health),path('api/ask/',ask),path('api/records/<str:id>/',detail),path('api/records/<str:id>/approve/',approve),path('api/documents/',documents)]
application=get_wsgi_application()
if __name__=='__main__':initialize();print('schema ready')
