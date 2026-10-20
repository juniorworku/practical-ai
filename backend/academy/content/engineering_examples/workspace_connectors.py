"""Optional connector adapters. Importing this module performs no calls.
Use your own authorized sandbox; OAuth issuance/refresh is an operator prerequisite.
Requires httpx. No write is retried after an uncertain response.
"""
import hashlib,hmac,json,time
import httpx

def verify_slack(raw, timestamp, signature, signing_secret, now=None):
    now=time.time() if now is None else now
    if abs(now-int(timestamp))>300:raise ValueError('stale event')
    expected='v0='+hmac.new(signing_secret.encode(),b'v0:'+str(timestamp).encode()+b':'+raw,hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,signature):raise ValueError('bad signature')
    return json.loads(raw)

def payload_hash(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def require_review(payload,approval,owner,now=None):
    now=time.time() if now is None else now
    if not approval or approval['owner']!=owner or approval['hash']!=payload_hash(payload) or approval['expires']<=now:
        raise PermissionError('current exact-payload approval required')
    # Approval is loaded from your trusted DB, never accepted directly from model arguments.

class Connectors:
    def __init__(self,slack_token,google_token,allowed_channels,allowed_calendar):
        self.slack_token=slack_token;self.google_token=google_token
        self.allowed_channels=set(allowed_channels);self.allowed_calendar=allowed_calendar
    async def history(self,channel):
        if channel not in self.allowed_channels:raise PermissionError('channel scope')
        # Requires membership and the corresponding Slack history read scope.
        async with httpx.AsyncClient(timeout=10) as client:
            r=await client.get('https://slack.com/api/conversations.history',headers={'Authorization':'Bearer '+self.slack_token},params={'channel':channel,'limit':20})
            r.raise_for_status();data=r.json()
            if not data.get('ok'):raise RuntimeError('connector rejected history')
            return {'messages':data['messages'],'next_cursor':data.get('response_metadata',{}).get('next_cursor','')}
    async def gmail_metadata(self,message_id):
        from urllib.parse import quote
        # Requires a granted Gmail metadata/read scope; never implies send authority.
        url='https://gmail.googleapis.com/gmail/v1/users/me/messages/'+quote(message_id,safe='')
        async with httpx.AsyncClient(timeout=10) as client:
            r=await client.get(url,headers={'Authorization':'Bearer '+self.google_token},params={'format':'metadata'})
            r.raise_for_status();data=r.json()
            return {'id':data['id'],'threadId':data.get('threadId'),'headers':data.get('payload',{}).get('headers',[])}
    async def gmail_reviewed_draft(self,owner,operation,to,subject,body,approval):
        import base64
        from email.message import EmailMessage
        payload={'operation':operation,'to':to,'subject':subject,'body':body}
        require_review(payload,approval,owner)
        message=EmailMessage();message['To']=to;message['Subject']=subject;message.set_content(body)
        raw=base64.urlsafe_b64encode(message.as_bytes()).decode()
        # Gmail compose scope can be broad. The app exposes draft creation only.
        # Persist the intent first. A lost response is uncertain, not a safe retry.
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                r=await client.post('https://gmail.googleapis.com/gmail/v1/users/me/drafts',headers={'Authorization':'Bearer '+self.google_token},json={'message':{'raw':raw}})
            except (httpx.TimeoutException,httpx.NetworkError):return {'state':'uncertain','operation':operation}
            r.raise_for_status();return {'state':'draft_created','draft_id':r.json()['id']}
    async def freebusy(self,start,end):
        # Requires calendar.freebusy or an appropriately scoped read grant.
        async with httpx.AsyncClient(timeout=10) as client:
            r=await client.post('https://www.googleapis.com/calendar/v3/freeBusy',headers={'Authorization':'Bearer '+self.google_token},json={'timeMin':start,'timeMax':end,'items':[{'id':self.allowed_calendar}]})
            r.raise_for_status();data=r.json()
            calendar=data.get('calendars',{}).get(self.allowed_calendar,{})
            if calendar.get('errors') or 'busy' not in calendar:raise RuntimeError('availability unavailable')
            return calendar['busy']
    async def create_reviewed_event(self,owner,operation,event,approval):
        from urllib.parse import quote
        payload={'calendar':self.allowed_calendar,'event':event,'operation':operation}
        require_review(payload,approval,owner)
        # Stable base32hex-compatible ID; same scoped operation maps to same destination ID.
        event_id=hashlib.sha256((owner+':'+operation).encode()).hexdigest()
        base='https://www.googleapis.com/calendar/v3/calendars/'+quote(self.allowed_calendar,safe='')+'/events'
        headers={'Authorization':'Bearer '+self.google_token}
        async with httpx.AsyncClient(timeout=10) as client:
            try:r=await client.post(base,headers=headers,params={'sendUpdates':'none'},json={**event,'id':event_id})
            except (httpx.TimeoutException,httpx.NetworkError):return {'state':'uncertain','destination_id':event_id}
            if r.status_code==409:
                observed=await client.get(base+'/'+event_id,headers=headers);observed.raise_for_status()
                # Caller compares actual event fields to the approved canonical payload.
                return {'state':'needs_reconciliation','destination_id':event_id,'observed':observed.json()}
            r.raise_for_status();return {'state':'committed','destination_id':r.json()['id']}
