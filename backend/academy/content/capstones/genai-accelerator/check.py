"""Actual HTTP → queue → worker → PostgreSQL → grounded fixture response checks."""
import json,time,urllib.request,urllib.error,uuid,os
BASE=os.getenv('LAB_URL','http://127.0.0.1:8215')
def request(path,body=None,token='demo-one'):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(BASE+path,data=data,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=5) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as error:return error.code,json.load(error)
assert request('/health')[0]==200
text='Refund window is 14 days. Unused items only. Fixture '+uuid.uuid4().hex
code,uploaded=request('/documents',{'text':text});assert code==202
id=uploaded['id']
assert request('/documents/'+id,token='demo-two')[0]==404
assert request('/ask',{'document_id':id,'question':'refund'},token='demo-two')[0]==404
for attempt in range(50):
    code,row=request('/documents/'+id)
    if row['state']=='ready':break
    time.sleep(.2)
else:raise AssertionError('worker did not make document ready')
assert row['chunks'] and row['chunks'][0]['text']=='Refund window is 14 days'
assert request('/documents',{'text':text})[1]['id']==id
code,answer=request('/ask',{'document_id':id,'question':'refund'})
assert code==200 and answer['answer']=='Refund window is 14 days'
assert answer['citations']==[id+':0'] and answer['context_chars']<=1000
assert request('/ask',{'document_id':id,'question':'warranty'})[1]['answer'] is None
assert request('/documents',{'text':'   '})[0]==422
assert request('/ask',{'document_id':id,'question':'   '})[0]==422
print(json.dumps({'document_id':id,'worker_ready':True,'scope_denial':True,'deduplicated':True,'grounded_fixture':answer,'unanswerable_abstained':True},indent=2))
