"""Probe a running student server. Keys come from the operator environment."""
import json
import os
import urllib.error
import urllib.request

keys=json.loads(os.environ['STUDENT_KEYS'])
a=next(key for key,owner in keys.items() if owner=='team-a')
b=next(key for key,owner in keys.items() if owner=='team-b')
origin=os.environ.get('PROBE_ORIGIN','http://127.0.0.1:8094')
def post(key,body):
    request=urllib.request.Request(origin+'/answer',data=json.dumps(body).encode(),headers={
        'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=30) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as error:
        with error:return error.code,json.load(error)

with urllib.request.urlopen(origin+'/health',timeout=5) as response:
    health=json.load(response)
assert health['ready'] and health['provider_checked'] is False
status,first=post(a,{'queries':['refund days?','unknown']})
assert status==200 and [row['source'] for row in first['results']]==['a-refunds-v1',None]
status,again=post(a,{'queries':['refund days?']})
assert status==200 and again['results'][0]['cached']
assert post(b,{'queries':['refund days?']})[1]['results'][0]['source'] is None
assert post('invalid',{'queries':['refund']})[0]==401
assert post(a,{'queries':['refund'],'owner':'team-b'})[0]==400
print(json.dumps({'probe':'owner-source-v2','passed':True,
    'first_request_cached':first['results'][0]['cached'],
    'provider':health['provider'],'semantic_quality':'not evaluated'},indent=2))
# Saves no keys or private questions. A first cache hit after a server/container
# replacement is restart evidence when the operator records that lifecycle.
