"""Complete, offline executable experiments for the 12-week engineering program.
Every file supplies its fixtures. Live connectors are a separate opt-in bundle.
"""
import textwrap
LABS={}
def add(key,code,reason,change):
 LABS[key]={'code':textwrap.dedent(code).strip()+'\n','reason':reason,'change':change}

add(1, '''
from dataclasses import dataclass
@dataclass(frozen=True)
class Result:
    status: str
    text: str
    input_tokens: int
    output_tokens: int
    usage_kind: str

def adapter(question):
    if not question.strip(): raise ValueError('question required')
    return Result('draft','Synthetic supported draft',12,5,'fixture')
result=adapter('What is the returns policy?')
assert result.status=='draft' and result.usage_kind=='fixture'
assert result.input_tokens+result.output_tokens==17
print(result)
''','The adapter owns a stable application contract even when the SDK changes. Status, text and usage have different meanings: a draft is not approval, and supplied fixture counts are not measured provider billing. Model IDs and SDK versions belong in the run manifest. Keep provider exceptions behind typed application errors without copying credentials or full prompts into logs.','Implement a second adapter with the identical contract and a permanent authentication error. Assert caller behavior is unchanged, then record the installed SDK version and selected capability before any live request.')
add(2, '''
import hashlib,json
def context_key(owner, model, prompt_version, source_version, turns):
    payload=[owner,model,prompt_version,source_version,turns]
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
turns=[{'role':'user','text':'Returns?'},{'role':'assistant','text':'Unopened within 14 days.'}]
k=context_key('acme','fixture','p1','s1',turns)
assert k!=context_key('other','fixture','p1','s1',turns)
assert k!=context_key('acme','fixture','p1','s2',turns)
window,fixed,output_reserve=1000,240,200
available=window-fixed-output_reserve
assert available==560
print({'retrieval_allowance':available,'cache_scope_tests':'passed','token_kind':'supplied fixture'})
''','A stateless completion needs the relevant turns supplied again; a server-side session ID references managed state and still needs ownership and lifecycle rules. The cache fingerprint includes tenant, model, prompt, source revision and actual turns. Omitting one can return another user’s content or a stale answer. The 560-unit allowance is a fixture arithmetic check; a real tokenizer or provider count must replace it before enforcing a model-specific limit.','Add tool schemas and metadata to the budget. Test a model migration, permission revocation and an expired cache entry. Distinguish provider prompt caching from caching complete answers; they have different correctness and billing boundaries.')
add(3, '''
import asyncio
async def main():
    active=peak=0
    semaphore=asyncio.Semaphore(2)
    async def generate(index):
        nonlocal active,peak
        async with semaphore:
            active+=1;peak=max(peak,active)
            try:
                await asyncio.sleep(.001)
                if index==3: raise TimeoutError('fixture timeout')
                return ('draft',index)
            finally: active-=1
    outcomes=await asyncio.gather(*(generate(i) for i in range(6)),return_exceptions=True)
    assert peak==2 and active==0
    assert sum(isinstance(x,TimeoutError) for x in outcomes)==1
    assert sum(isinstance(x,tuple) for x in outcomes)==5
    print({'requests':6,'peak_active':peak,'failed':1,'completed':5})
asyncio.run(main())
''','An async function is cooperative, not automatically bounded. The semaphore caps active provider calls; finally releases accounting on success or failure. gather(return_exceptions=True) keeps every outcome for a batch evaluation; an interactive session may instead cancel siblings on disconnect. Six tasks are safe as a small fixture, but creating a task for every unbounded upload still exhausts memory. Use an admission limit and a bounded queue as well.','Add an overall asyncio.timeout budget, cancel a waiting task and assert the semaphore is not leaked. Compare queue wait with provider service time. Run the same workload with one and four slots and measure the quality/cost/latency change rather than assuming more concurrency helps.')
add(4, '''
import asyncio
async def main():
    queue=asyncio.Queue(maxsize=2)
    accepted=dropped=0
    for sequence in range(5):
        frame={'sequence':sequence,'pcm':b'\\x00\\x00'*160}
        try: queue.put_nowait(frame); accepted+=1
        except asyncio.QueueFull: dropped+=1
    frames=[]
    while not queue.empty():
        item=await queue.get();frames.append(item['sequence']);queue.task_done()
    assert frames==[0,1] and dropped==3
    # At 16kHz mono PCM16, 320 bytes represents 10 milliseconds.
    assert (320/(16000*2))*1000==10
    print({'accepted':accepted,'overload':dropped,'frame_ms':10})
asyncio.run(main())
''','Audio is a timed stream, not a series of unrelated text prompts. Sequence numbers expose missing frames; byte rate depends on channel count, sample rate and sample width. This deliberately fast producer fills a bounded queue. Dropping speech may destroy meaning, so the exercise makes overload visible rather than declaring the session accurate. A live gateway must choose pause, explicit rejection or a documented drop strategy and measure its effect.','Implement a producer that awaits queue capacity, a slow consumer and a disconnect. Verify both tasks terminate and record maximum queued audio milliseconds. Never send browser WebM/Opus bytes while labeling them raw PCM16.')
add(5, '''
from collections import deque
playback=deque([('old-turn',b'frame-a'),('old-turn',b'frame-b')])
state={'turn':'old-turn','interrupted':False,'last_ack':7}
def interrupt(new_turn):
    playback.clear();state.update(turn=new_turn,interrupted=True)
interrupt('new-turn')
assert not playback and state['turn']=='new-turn'
replayed=[6,7,8,9]
accepted=[seq for seq in replayed if seq>state['last_ack']]
assert accepted==[8,9]
print({'queued_old_audio':len(playback),'resume_sequences':accepted})
''','Receiving an interruption event is insufficient if queued old audio continues playing. Clear the playback queue and stop already scheduled audio nodes; then move to the new turn. The acknowledgement example isolates duplicate sequence handling, not proof that a provider supports replaying arbitrary audio. Resumption handles are session secrets and cannot substitute for application ownership. Reconnect may land on another replica.','In the voice app, interrupt during playback and verify old audio actually stops. Expire a session and reconnect with a bounded history policy. Measure turn-end-to-first-playable-audio separately from time spent opening the socket.')
add(6, '''
from math import ceil
turns=[{'first_audio_ms':150,'cost_units':2,'correct':True},
       {'first_audio_ms':240,'cost_units':3,'correct':True},
       {'first_audio_ms':1200,'cost_units':4,'correct':False},
       {'first_audio_ms':None,'cost_units':1,'correct':False}]
finished=[x['first_audio_ms'] for x in turns if x['first_audio_ms'] is not None]
p95=sorted(finished)[ceil(.95*len(finished))-1]
assert p95==1200 and sum(x['cost_units'] for x in turns)==10
print({'attempts':4,'playable_audio_turns':3,'p95_completed_ms':p95,
       'accepted':2,'cost_per_accepted':5,'failed_before_audio':1})
''','The voice release report keeps the no-audio failure in reliability and spend even though no first-audio latency exists for it. Label the latency denominator as completed audio turns. A low first-token value is not low audible latency if buffers delay playback. These synthetic metrics validate accounting only; speech intelligibility, task correctness, interruptions and real network behavior need separate observations.','Build the live voice capstone from the complete integration files. Test ten prerecorded consented/synthetic turns, a disconnect and an interruption. Define a provisional p95/quality/cost gate before measuring; retain failures and revise the target honestly if hardware or provider limits prevent it.')
add(7, '''
import hashlib
jobs={}
def ingest(owner,filename,raw):
    if len(raw)>1000: return 'rejected_size'
    suffix=filename.rsplit('.',1)[-1].lower()
    if suffix not in {'txt','pdf','docx','vtt'}: return 'unsupported'
    key=(owner,hashlib.sha256(raw).hexdigest())
    jobs.setdefault(key,{'state':'received','filename':filename,'bytes':len(raw)})
    return key
key=ingest('acme','note.txt',b'Approved policy')
assert ingest('acme','note.txt',b'Approved policy')==key
assert ingest('other','note.txt',b'Approved policy')!=key
assert ingest('acme','huge.pdf',b'x'*1001)=='rejected_size'
print({'jobs':len(jobs),'duplicate_same_owner':'deduplicated','oversize':'rejected'})
''','Intake records an immutable content digest and owner before parsing. Same bytes under another tenant are not permission to reuse private output. A filename extension is only an initial allowlist, not trusted content detection. Worker limits must include decompressed DOCX size, PDF page count and parser time; a small upload can still trigger excessive work. Activation and upload receipt remain separate states.','Use the mixed-media parser bundle on one PDF, DOCX, plain-text note and timestamped transcript. Preserve original digest and page/paragraph/time offsets. Add an unreadable scan and keep it quarantined instead of returning an empty but successful index.')
add(8, '''
sections=[{'id':'rule','text':'Unopened items may be returned within 14 days. Opened items excluded.'},
          {'id':'shipping','text':'Shipping takes five working days.'}]
def chunks(rows,budget):
    result=[]
    for row in rows:
        estimate=len(row['text'].split())
        if estimate>budget: raise ValueError('section needs reviewed split')
        result.append({**row,'estimated_word_units':estimate})
    return result
result=chunks(sections,20)
assert 'Opened items excluded.' in result[0]['text']
try: chunks(sections,3)
except ValueError: print('oversized rule refused; exception stays attached')
else: raise AssertionError('should refuse unsafe split')
''','The example preserves a rule and its exception as one section rather than optimizing for equal-sized fragments. Word units are explicitly an estimate, not provider tokens. A semantic chunker also has computation cost and can change boundaries nondeterministically; compare it against a fixed token baseline using the same relevance labels. Every chunk needs owner, document revision and offset in addition to text.','Implement a real tokenizer-based splitter with overlap and preserved offsets. Compare three chunk sizes and a heading/semantic strategy on queries whose answer requires a nearby exception; report recall, context spend and downstream claim support.')
add(9, '''
index={'model':'fixture-embedding-v1','dimensions':3,'revision':'index-1'}
def accept(vector,model):
    if model!=index['model'] or len(vector)!=index['dimensions']:
        raise ValueError('embedding space mismatch')
    if not all(type(x) in (int,float) for x in vector): raise ValueError('numeric vector required')
    return True
assert accept([1.,0.,0.],'fixture-embedding-v1')
for vector,model in [([1.,0.],'fixture-embedding-v1'),([1.,0.,0.],'different-model')]:
    try: accept(vector,model)
    except ValueError: continue
    raise AssertionError('must not mix spaces')
print('embedding model and dimension gates passed')
''','Vectors from different embedding models are not interchangeable even if their lengths happen to match. Store model/version, dimension and normalization policy with the index manifest. Re-embedding should build a new searchable revision, evaluate it and switch an active pointer; silently mixing vectors can produce plausible but meaningless nearest neighbors. The fixture does not simulate semantic embedding quality.','Use a documented embedding API or installed local model, record measured usage and vector dimension, and implement finite-number validation. Rebuild an isolated index under a different model and prove the old active revision remains available until promotion.')
add(10, '''
rows=[{'id':'a1','owner':'acme','revision':'v1','score':.8},
      {'id':'b1','owner':'other','revision':'v1','score':.99},
      {'id':'a2','owner':'acme','revision':'v2','score':.7}]
def scoped_search(owner,revision):
    eligible=[r for r in rows if r['owner']==owner and r['revision']==revision]
    return sorted(eligible,key=lambda r:(-r['score'],r['id']))
assert [r['id'] for r in scoped_search('acme','v1')]==['a1']
assert scoped_search('unknown','v1')==[]
print('tenant and active-revision filter applied before output')
''','Similarity scores do not authorize retrieval. SQL must include tenant and active revision, with a server-established identity. Exact filtered search is a useful small-data baseline before HNSW. Approximate-index filtering can reduce returned matches; observe recall and execution plans rather than assuming LIMIT k always yields k relevant allowed rows. Tenant isolation must hold even when the closest vector belongs to someone else.','Run the complete pgvector schema/query example. Seed two owners with identical text, test denied access and compare exact recall with HNSW while varying its ef_search on fixed queries. Record index build time, memory assumptions and source activation behavior.')
add(11, '''
def rrf(rankings,k=60):
    scores={}
    for ranking in rankings:
        for rank,identifier in enumerate(dict.fromkeys(ranking),1):
            scores[identifier]=scores.get(identifier,0)+1/(k+rank)
    return sorted(scores,key=lambda identifier:(-scores[identifier],identifier))
lexical=['a','b','c'];dense=['b','d','a']
combined=rrf([lexical,dense])
assert combined[:2]==['b','a']
assert len(combined)==len(set(combined))==4
print({'hybrid_rank':combined,'method':'reciprocal-rank fusion'})
''','Lexical and vector scores have different scales; adding raw values makes an undocumented calibration assumption. Reciprocal-rank fusion combines rank positions without claiming those scores are comparable probabilities. Deduplication prevents repeated IDs in one list from receiving extra votes. Fusion cannot recover a passage absent from both candidate sets, and two weak retrievers do not automatically improve quality.','Compare lexical, dense and fused rankings on a fixed relevance set including vocabulary mismatch and exact product codes. Sweep candidate depth, report recall@k/MRR and added latency, and keep tenant/revision filtering identical across all methods.')
add(12, '''
# A deterministic fake reranker lets us test identity mapping and budget behavior.
candidates=[{'id':'c3','text':'irrelevant'}, {'id':'c1','text':'unopened return policy'}, {'id':'c2','text':'shipping'}]
provider_response=[{'index':1,'relevance_score':.9},{'index':2,'relevance_score':.4}]
def map_results(response):
    if any(type(r['index']) is not int or not 0<=r['index']<len(candidates) for r in response):
        raise ValueError('unknown candidate index')
    return [candidates[r['index']]['id'] for r in response]
assert map_results(provider_response)==['c1','c2']
try:map_results([{'index':99}])
except ValueError:print('rerank candidate identity checked; top result c1')
else:raise AssertionError()
''','A reranker scores only the candidates it receives. Map the provider’s original candidate index back to your immutable chunk ID, not to a reordered list. Relevance scores are not calibrated answer confidence. Reranking adds a network call, token processing and latency; skip or fall back under a documented remaining-time budget, then measure the quality effect rather than silently changing behavior.','Use the documented Cohere adapter with an explicitly selected model or a local reranker. Evaluate no-rerank and rerank on identical candidate lists; retain provider failures, measured cost and p95. Test an out-of-range index and duplicate result IDs.')
add(13, '''
retrieved={'p1':'Only unopened items within 14 days qualify.'}
claims=[{'text':'Opened items qualify.','source':'p1','human_support':False}]
identity=all(c['source'] in retrieved for c in claims)
supported=sum(c['human_support'] for c in claims)
assert identity and supported==0
print({'citation_identity':identity,'reviewed_supported_claims':supported,'claims':len(claims),'ready':False})
''','The source exists but contradicts the claim. Separating identity from entailment avoids a common false certificate: valid citations can accompany an unsupported answer. Claim support here is a manual fixture label; semantic judgments need a rubric and evidence, not a confidence string. Applicability also matters: a correct rule for another account or date may still be the wrong answer.','Add answer, clarify and abstain outcomes; include an outdated source and a conflicting current policy. Require the final answer to cite immutable page/time offsets and keep an unsupported draft out of approved export.')
add(14, '''
import asyncio
async def main():
    events=[];done=False
    async def stream():
        yield {'event':'draft_delta','text':'Unopened '}
        await asyncio.sleep(0)
        yield {'event':'draft_delta','text':'within 14 days.'}
        yield {'event':'draft_complete','source_ids':['p1']}
    async for event in stream():
        events.append(event)
        if event['event']=='draft_complete':done=True
    assert done and events[-1]['source_ids']==['p1']
    partial=events[:-1]
    assert not any(e['event']=='draft_complete' for e in partial)
    print({'partial_is_approved':False,'completed_events':len(events)})
asyncio.run(main())
''','Streaming reduces perceived waiting but exposes provisional output before final validation. The client must render deltas as a draft and wait for a complete event carrying status/source identity. A disconnect after two deltas is not a completed answer and must not enter the full-answer cache. Retrieval-first streaming also needs latency measurement for the silent phase before generation begins.','Add error and cancellation events, preserve the question across disconnect and show an unambiguous incomplete state. Compare time-to-first-byte with retrieval duration and full-answer latency. Validate citations only against the authorized selected evidence.')
add(15, '''
queries=[{'id':'q1','gold':{'p1'},'ranked':['p2','p1'],'expected':'answer','actual':'answer'},
         {'id':'q2','gold':set(),'ranked':[],'expected':'abstain','actual':'abstain'},
         {'id':'q3','gold':{'p3'},'ranked':['p4'],'expected':'answer','actual':'abstain'}]
answerable=[q for q in queries if q['gold']]
recall=sum(len(set(q['ranked'][:2])&q['gold'])/len(q['gold']) for q in answerable)/len(answerable)
assert recall==.5
assert len(queries)-len(answerable)==1
print({'recall_at_2_answerable':recall,'answerable':2,'no_source_cases':1,'behaviors_correct':2,'all_cases':3})
''','Retrieval recall needs an explicit denominator. The no-source query has no relevant passage and is scored for correct abstention rather than forcing a 0/0 recall. A correct abstention on unavailable sources and an incorrect abstention caused by retrieval failure are operationally different. This three-case fixture validates scoring; a capstone needs a larger held-out set and factual review.','Ship the mixed-media knowledge-base capstone with owner-scoped uploads, parse-status UI, source-linked streaming and an evaluation report. Test unsupported questions, failed parsing, conflicting revisions, unauthorized reads and a restore; compare hybrid/reranked quality against the lexical baseline.')
add(16, '''
allowed={'draft_reply':{'fields':{'channel','text'},'effect':'local_draft'}}
def dispatch(actor,tool,args):
    contract=allowed.get(tool)
    if not contract or type(args) is not dict or set(args)!=contract['fields']:return 'rejected'
    if args['channel'] not in actor['channels']:return 'denied'
    if not all(type(value) is str for value in args.values()):return 'invalid_type'
    return {'status':'draft','owner':actor['owner'],'text':args['text']}
actor={'owner':'acme','channels':{'support'}}
assert dispatch(actor,'draft_reply',{'channel':'private','text':'hello'})=='denied'
assert dispatch(actor,'send_reply',{'channel':'support','text':'hello'})=='rejected'
assert dispatch(actor,'draft_reply',{'channel':'support','text':'hello'})['status']=='draft'
print('tool schema, application authority and draft-only effect verified')
''','A function schema tells the model how to propose an operation; it does not confer permission. The dispatcher validates allowed fields, authenticated actor scope, types and effects. Real connectors also need least-privilege OAuth scopes, token storage/rotation, retry categories and destination-specific error mapping. Never accept a model-generated user/tenant ID as identity.','Define independent read/draft/calendar-proposal contracts for Gmail, Slack and Calendar. Keep send/create disabled until exact human approval. Record connector response IDs and test revoked scopes and a forbidden channel before any live account integration.')
add(17, '''
import sqlite3,tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'state.sqlite';db=sqlite3.connect(path)
    db.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY,owner TEXT,state TEXT,version INT)')
    with db:db.execute('INSERT INTO jobs VALUES(?,?,?,?)',('j1','acme','awaiting_review',1))
    db.close();db=sqlite3.connect(path)
    def resume(owner,version):
        with db:return db.execute("UPDATE jobs SET state='ready',version=version+1 WHERE id='j1' AND owner=? AND state='awaiting_review' AND version=?",(owner,version)).rowcount
    assert resume('other',1)==0 and resume('acme',1)==1 and resume('acme',1)==0
    db.close()
print('checkpoint survives reopen; scoped version consumed once')
''','Persist state at a meaningful boundary, not only in a conversation buffer. A conditional state/version update prevents a duplicate resume from advancing twice. LangGraph checkpoints use a thread ID to load state; a thread ID is still not authorization. An interrupt can cause a node to execute again on resume, so work before the interrupt must be safe to repeat or isolated in idempotent tasks.','Implement the same wait/resume path using the documented LangGraph checkpointer example. Replace its in-memory saver with a durable store before claiming restart recovery. Interrupt before and after the approval boundary and compare traces to this simpler SQL baseline.')
add(18, '''
import hashlib,json
payload={'owner':'acme','destination':'calendar:team','start':'2026-11-03T10:00:00+03:00','attendees':['synthetic@example.test'],'revision':2}
def fingerprint(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
approved={'digest':fingerprint(payload),'expires_at':100,'actor':'reviewer'}
def permitted(current,now,actor_active):
    return now<approved['expires_at'] and actor_active and fingerprint(current)==approved['digest']
assert permitted(payload,99,True)
assert not permitted(dict(payload,start='2026-11-03T11:00:00+03:00'),99,True)
assert not permitted(payload,100,True) and not permitted(payload,99,False)
print('approval binds exact time, recipients, destination and active reviewer authority')
''','A calendar draft becomes consequential when it creates an event or invitation. The reviewed payload includes timezone, time interval, calendar, attendees and revision; editing any effect field invalidates approval. Human approval must be checked again at dispatch, including expiry and revoked roles. A hash detects changed bytes but is neither an identity system nor a remote idempotency guarantee.','Add end time, duration, timezone validation and an expired reviewer role. In the workspace app, show the exact proposal to the human, persist the decision and prevent stale browser tabs from scheduling changed content.')
add(19, '''
import hashlib,json
cache={}
def memory(owner,source_revision,question,summary):
    key=hashlib.sha256(json.dumps([owner,source_revision,question]).encode()).hexdigest()
    cache[key]=summary
    return key
first=memory('acme','v1','returns','Unopened within 14 days; opened excluded.')
second=memory('acme','v2','returns','Unopened within 21 days; opened excluded.')
assert first!=second
assert 'opened excluded' in cache[first]
assert first!=memory('other','v1','returns','different tenant')
print('owner/revision memory isolation passed; exception preserved in summary fixture')
''','Memory is selected application data, not permission to paste all history into every call. A rolling summary can lose exceptions, dates and unresolved decisions; evaluate it against exact source facts and keep recoverable originals. Cached summaries require source/permission invalidation and retention rules. Provider KV/prompt caches and your application memory have different lifecycles.','Write a memory-selection policy that budgets the recent turns, durable facts and tool outputs separately. Test a source revision and revoked membership; compare summary compression savings with a deliberately omitted exception failure.')
add(20, '''
import asyncio
async def branch(name):
    await asyncio.sleep(0)
    return {'branch':name,'source':'p1','claim':'Only unopened items','cost':2}
async def main():
    results=await asyncio.gather(branch('policy'),branch('account'))
    claims={r['claim'] for r in results}
    total=sum(r['cost'] for r in results)
    assert len(results)==2 and len(claims)==1 and total==4
    print({'workers':2,'unique_claims':len(claims),'total_cost':total,'quality_gain_not_established':True})
asyncio.run(main())
''','Parallel delegation can reduce wall time for independent work but also duplicate retrieval, spend and disagreement. Here two workers produce the same claim and double fixture cost without measured quality improvement. Use LangChain for provider/tool composition, LangGraph for explicit state and resumption, or CrewAI for role/task coordination only when its ownership and failure semantics fit the requirement. Framework choice does not remove an evaluator or effect permissions.','Compare the single-workflow baseline with a two-branch design on the same cases. Cancel a failed sibling, preserve per-branch provenance and define conflict arbitration. Adopt delegation only if observed quality or latency justifies its extra cost and operational state.')
add(21, '''
response={'jsonrpc':'2.0','id':1,'result':{'tools':[{'name':'lookup_policy','inputSchema':{'type':'object','properties':{'id':{'type':'string'}},'required':['id'],'additionalProperties':False}}]}}
allowed={'lookup_policy'}
names={tool['name'] for tool in response['result']['tools']}
assert names<=allowed
proposal={'tool':'lookup_policy','arguments':{'id':'p1'},'claimed_owner':'other'}
authenticated_owner='acme'
assert authenticated_owner!=proposal['claimed_owner']
print({'discovered_tools':sorted(names),'authority_source':'application authentication','protocol_fixture_only':True})
''','MCP separates a host, per-server clients and capability-providing servers. Discovery describes tools/resources/prompts; it does not authorize all discovered behavior. Validate negotiated capabilities and schema at invocation, scope credentials to the actual server and enforce the authenticated owner in the tool implementation. This JSON fixture is a discovery-contract check, not a complete MCP server or handshake.','Run a local MCP server with one read-only policy tool using the official SDK bundle. Test initialization, tools/list, valid/invalid calls, cancellation and a cross-owner ID. Record transport and protocol/SDK versions instead of assuming every server supports the same features.')
add(22, '''
ledger={};effects=[]
def schedule(key,approved,lose_response=False):
    if not approved:return 'needs_review'
    if key in ledger:return 'reconcile' if ledger[key]=='uncertain' else 'already_committed'
    ledger[key]='claimed'
    effects.append({'key':key,'destination':'fake-calendar'})
    ledger[key]='uncertain' if lose_response else 'committed'
    return ledger[key]
assert schedule('acme:event-1:r2',True,True)=='uncertain'
assert schedule('acme:event-1:r2',True)=='reconcile'
assert len(effects)==1
assert schedule('acme:event-2:r1',False)=='needs_review'
print({'fake_effects':len(effects),'lost_response':'reconcile same key, never blind replay'})
''','A timeout after a remote calendar accepts the event is uncertain. Do not infer failure and issue a new key. Save the same operation ID, inspect the remote event or idempotency record and reconcile before retrying. This dictionary is a single-process teaching fixture; multiple workers require an atomic durable claim, and remote duplicate prevention depends on the destination’s API contract.','Persist the ledger in PostgreSQL with a scoped unique operation key. Add two workers, a restart after the remote effect and revoked approval. Keep local transaction rollback separate from cancelling an already created external calendar event.')
add(23, '''
seen=set();deliveries=[];jobs=[]
def receive(event):
    deliveries.append(event['id'])
    if event['id'] in seen:return 'duplicate'
    seen.add(event['id']);jobs.append({'id':event['id'],'state':'queued'})
    return 'accepted'
event={'id':'slack-event-7','channel':'support','text':'Returns?'}
assert receive(event)=='accepted' and receive(event)=='duplicate'
assert len(deliveries)==2 and len(jobs)==1
# A worker failure does not remove the accepted job.
jobs[0]['state']='retry_wait'
assert jobs[0]['id']=='slack-event-7'
print({'deliveries':2,'durable_design_jobs':1,'worker_state':jobs[0]['state'],'storage_in_this_fixture':'memory'})
''','Webhooks can be redelivered. Verify signatures over the exact raw body before trusting payloads, enforce replay windows and acknowledge quickly after durable enqueue. Work in the request handler risks provider timeout and duplicate deliveries. The memory fixture illustrates deduplication only; its printed storage label explicitly does not claim durable enqueue. A polling connector also needs a cursor and retention-aware replay policy.','In the connector app, verify signatures with a fixture signing secret, store the inbox ID and payload digest transactionally and resume the worker after restart. Test a reused event ID with changed content, an invalid signature, duplicate delivery and an unavailable provider.')
add(24, '''
import hashlib,json
def review(proposal):
    return hashlib.sha256(json.dumps(proposal,sort_keys=True).encode()).hexdigest()
class WorkspaceFixture:
    def __init__(self):self.ledger={};self.effects=[];self.payloads={}
    def process(self,event_id,proposal,scope,evidence,approval,lose_response=False):
        if not scope or proposal['owner']!='acme' or proposal['channel']!='support':return 'deny'
        if not evidence:return 'abstain'
        if approval!=review(proposal):return 'needs_review'
        key=(proposal['owner'],event_id,proposal['revision'])
        if key in self.ledger:
            if self.payloads[key]!=review(proposal):return 'payload_conflict'
            return 'reconcile' if self.ledger[key]=='uncertain' else 'already_committed'
        self.ledger[key]='claimed';self.payloads[key]=review(proposal)
        self.effects.append({'key':key,'text':proposal['text']})  # Fake local destination.
        self.ledger[key]='uncertain' if lose_response else 'committed'
        return self.ledger[key]
service=WorkspaceFixture()
proposal={'owner':'acme','channel':'support','text':'Unopened items only','revision':1}
assert service.process('e1',proposal,True,True,None)=='needs_review'
assert service.process('e1',proposal,False,True,review(proposal))=='deny'
assert service.effects==[]
assert service.process('e1',proposal,True,True,review(proposal))=='committed'
assert service.process('e1',proposal,True,True,review(proposal))=='already_committed'
assert service.process('e2',proposal,True,True,review(proposal),lose_response=True)=='uncertain'
assert service.process('e2',proposal,True,True,review(proposal))=='reconcile'
changed={**proposal,'text':'Changed under reused event ID'}
assert service.process('e1',changed,True,True,review(changed))=='payload_conflict'
assert len(service.effects)==2
print({'fake_effects':2,'duplicate_did_not_write':True,'lost_response':'uncertain then reconcile'})
''','The workspace fixture actually runs proposal, authorization, approval, duplicate and uncertain-outcome branches. Returned states and the effect list must agree; comparing literal expected/actual strings would not exercise a dispatcher. This is still a single-process fake destination, not durable remote exactly-once delivery. The live adapters and durable local state examples are subsequent integration pieces.','Integrate verified intake, scoped evidence, local drafts, exact reviewed actions and the durable ledger. Start with fake destinations and failure cases, then optionally test your own granted connectors while retaining the same boundaries.')
add(25, '''
# Reviewed claim labels are supplied; they are not inferred by string overlap.
claims=[{'claim':'Unopened within 14 days','supported':True}, {'claim':'Opened eligible','supported':False}]
supported=sum(c['supported'] for c in claims)
score=supported/len(claims) if claims else None
assert score==.5
print({'reviewed_faithfulness':score,'claims':2,'semantic_labels':'human fixture',
       'mechanical_citation_identity_can_still_pass':True})
''','Faithfulness measures support by retrieved evidence; answer relevance asks whether the response addresses the question, while context recall asks whether necessary evidence was retrieved. These are different rubrics. Ragas/TruLens can automate judge-based scoring, but a changing model judge can change scores. Keep deterministic contracts and relevance-label metrics separate from stochastic semantic assessment, record judge versions and audit disagreements.','Write a five-example rubric covering negation, contradiction, applicability and missing evidence. Compare a human review with a documented Ragas or TruLens run on the same rows, recording cost and disagreement rather than certifying model judgments as truth.')
add(26, '''
def policy_decision(request):
    if request['owner']!='acme':return 'deny'
    if request['prompt']=='returns window':return 'answer'
    if request['prompt']=='unlisted warranty':return 'abstain'
    return 'clarify'
cases=[{'id':'window','request':{'owner':'acme','prompt':'returns window'},'expected':'answer'},
       {'id':'missing','request':{'owner':'acme','prompt':'unlisted warranty'},'expected':'abstain'},
       {'id':'ambiguous','request':{'owner':'acme','prompt':'it?'},'expected':'clarify'},
       {'id':'scope','request':{'owner':'other','prompt':'returns window'},'expected':'deny'}]
results=[{'id':c['id'],'actual':policy_decision(c['request']),'expected':c['expected']} for c in cases]
assert len(results)==4 and all(r['actual']==r['expected'] for r in results)
assert all('expected' not in c['request'] for c in cases)
print({'concrete_cases':4,'contract_passed':4,'semantic_model_evaluation':False})
''','Four actual requests now exercise a deterministic policy contract: answer, abstain, clarify and denied owner. Each has input, expected outcome and an observed executor result. These supplied rules test harness mechanics, not model reasoning. The complete appendix supplies120 concrete scoped cases and an optional HTTP target; labels stay outside application requests.','Run the supplied120-case harness, inspect its twelve families and adapt the HTTP contract to your integrated service. Keep a fixed held-out split, report unavailable attempts and separately review semantic support before claiming answer quality.')
add(27, '''
import hashlib,json
manifest={'prompt':'p3','model':'fixture-v1','dataset':'cases-v2','parser':'parse-v1','context_policy':'ctx-v2','judge':'human-rubric-v1'}
fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
result={'contract_failures':0,'critical_failures':1,'quality_passed':99,'quality_total':100}
promote=result['contract_failures']==0 and result['critical_failures']==0
assert not promote
assert len(fingerprint)==64
print({'manifest_recorded':True,'promotion':promote,'reason':'critical regression blocks aggregate gain'})
''','CI needs a reproducible manifest tying code, prompt, model, dataset, parser, context/cache policy and judge to observed results. Separate inexpensive deterministic tests from explicitly budgeted provider evaluations. A 99/100 aggregate cannot waive a critical authorization or unsupported-action failure. Deployment promotion should depend on the relevant gates, not only a green unit-test job.','Add a CI configuration that runs offline contracts on every change and a separately authorized integration job with secrets and cost limits. Store reports as artifacts; simulate prompt/source/model changes and verify each changes the release manifest.')
add(28, '''
trace=[{'run':'r1','span':'retrieval','ms':20,'status':'ok'},
       {'run':'r1','span':'provider','ms':800,'status':'timeout'},
       {'run':'r1','span':'retry_wait','ms':100,'status':'stopped_budget'}]
allowed={'run','span','ms','status'}
assert all(set(event)==allowed for event in trace)
assert sum(event['ms'] for event in trace)==920
assert any(event['status']=='timeout' for event in trace)
print({'run_ms_sequential':920,'outcome':'failed','source_content_logged':False})
''','A trace explains where time and failures occurred without becoming a copy of confidential prompts. For sequential spans, summing durations can reconstruct elapsed work; parallel spans require a critical-path/wall-time view to avoid double counting. Correlate run IDs with prompt/source revisions and usage, and redact raw provider errors. LangSmith/Phoenix integrations should honor the same payload minimization and retention policy.','Instrument the same pipeline with a trace exporter and compare one slow retrieval, one slow model and one retry storm. Verify that a canary secret never appears in logs or external trace payloads. Include queue wait and cancellation outcomes.')
add(29, '''
from math import ceil
runs=[{'ms':100+i*10,'cost':1,'accepted':i%4!=0} for i in range(20)]
accepted=sum(r['accepted'] for r in runs);cost=sum(r['cost'] for r in runs)
p95=sorted(r['ms'] for r in runs)[ceil(.95*len(runs))-1]
assert accepted==15 and p95==280
print({'attempts':20,'accepted':accepted,'p95_ms':p95,'cost_per_accepted':round(cost/accepted,4)})
''','Optimize against accepted outputs rather than provider success alone. All attempts consume resources even when rejected, and rate-limit waits affect user-visible latency. A cache can reduce spend while harming freshness; a cheap model can increase correction work. Report the Pareto trade-off under a fixed workload and an explicit quality floor, not an unsupported universal saving percentage.','Compare two context budgets, a tenant/revision-aware cache and two model routes on the same labeled workload. Include review time, cache invalidation, cold starts and provider failures. Keep an unoptimized baseline and explain when your recommendation would reverse.')
add(30, '''
report={'dataset_cases':120,'completed':113,'unavailable':7,'critical_failures':1,
        'quality_reviewed':100,'quality_passed':94,'estimated_cost_units':18}
assert report['completed']+report['unavailable']==report['dataset_cases']
assert report['quality_reviewed']<=report['completed']
promote=report['critical_failures']==0 and report['unavailable']==0
assert not promote
print({'promotion':promote,'unavailable_kept':7,'unreviewed_completed':13})
''','The LLMOps capstone combines 100+ real labeled edge-case inputs, deterministic regressions, semantic review, versioned traces and latency/cost accounting. Not every completed response has been semantically reviewed; show that denominator. A release report needs the strongest counterexample, critical-failure disposition and exact candidate manifest, not a single “AI accuracy” percentage.','Run the 120-case dataset through the integrated agentic service, preserve raw observations and export category-level results. Block one intentionally bad candidate in CI, fix its cause and rerun the affected set plus fresh review before promotion.')
add(31, '''
services={'frontend':{'browser_url':'http://127.0.0.1:8091','proxy':'backend:8000'},
          'backend':{'database_host':'db','secret_source':'runtime'},
          'db':{'public_port':False,'volume':'data'}}
assert not services['db']['public_port']
assert services['backend']['database_host']=='db'
assert services['backend']['secret_source']=='runtime'
print('browser origin, container DNS, runtime credentials and durable storage separated')
''','Images package code; volumes or managed stores preserve state. A browser cannot use Docker service DNS directly. A same-origin proxy separates browser routing from internal service names. Readiness must query the dependency needed to serve work; a hard-coded healthy response can mask a missing database. Runtime credentials belong outside built layers and source control.','Use the complete DRF/PostgreSQL/Nginx Docker bundle in the deployment appendix. Save a synthetic record, recreate the backend, stop the database and verify readiness failure, then rehearse an isolated restore. The small network lab is unauthenticated; add and test owner isolation in your actual SaaS before cloud deployment.')
add(32, '''
connections=240
safe_per_instance=12
minimum=(connections+safe_per_instance-1)//safe_per_instance
configured_max=10
assert minimum==20 and configured_max<minimum
print({'offered_connections':connections,'measured_safe_per_instance':12,
       'minimum_instances_at_capacity':minimum,'configured_max':configured_max,'admission_or_capacity_change_required':True})
''','A concurrency setting is an admission limit, not measured hardware capacity. The simple division is a planning lower bound that ignores headroom, cold starts, uneven load and downstream quotas. Cloud Run WebSockets are long-running HTTP requests subject to a configured timeout; reconnects may land on another replica. ECS tasks similarly need load-balancer health, task capacity, connection draining and shared state.','Deploy your container to one chosen platform only after setting budget and maximum-instance limits. Run a stepped load experiment, report offered/accepted/completed connections and p95, and test reconnect after a replica is replaced. State the tested scale instead of claiming thousands of users from configuration alone.')
add(33, '''
# Illustrative GPU memory budget, not measurements of any model or device.
budget={'gpu_gib':24,'weights_gib':14,'runtime_gib':3,'safety_gib':2,'kv_per_request_gib':1}
remaining=budget['gpu_gib']-budget['weights_gib']-budget['runtime_gib']-budget['safety_gib']
slots=int(remaining//budget['kv_per_request_gib'])
assert slots==5
print({'illustrative_slots':slots,'real_concurrency_requires_measurement':True})
''','Self-hosting moves spend and operations to your GPU; it is not free inference. Resident weights, runtime buffers, safety headroom and KV cache all compete for memory. Context length and output length affect the per-request cache footprint. Ollama is a useful local-serving path; vLLM adds serving/batching controls for supported hardware/models. Quantization can change quality, so evaluate the exact artifact and tokenizer.','Run the documented local chat adapter against an installed model, then a GPU serving endpoint if hardware is available. Record model/license/revision, memory, cold-load time, tokens/sec, p95 and quality. Treat the five-slot fixture as arithmetic only; never use it as a device capacity claim.')
add(34, '''
# Single-process token-bucket fixture. Replicas need a shared atomic store.
class Bucket:
    def __init__(self,capacity,refill):self.capacity=capacity;self.tokens=capacity;self.refill=refill;self.last=0
    def take(self,now,amount=1):
        self.tokens=min(self.capacity,self.tokens+(now-self.last)*self.refill);self.last=now
        if amount>self.tokens:return False
        self.tokens-=amount;return True
bucket=Bucket(2,1)
assert bucket.take(0) and bucket.take(0) and not bucket.take(0)
assert bucket.take(1)
print('burst bounded; one request admitted after refill; shared atomic store still required')
''','Limit incoming requests separately from model-token budgets, worker concurrency and downstream provider quotas. A per-process bucket can be exceeded across replicas; a real distributed limiter needs atomic shared state and a chosen failure policy. Include Retry-After or a stable overload response and preserve accepted work. Fallback to another model/provider changes context capability, cost, privacy and quality, so it needs explicit routing and evaluation.','Implement a shared quota with atomic reservations and refund/reconciliation for actual usage. Test a retry storm across two workers, an unavailable quota store and zero remaining monthly budget. Bound maximum instances and stop/fallback behavior before load testing.')
add(35, '''
requests=[{'id':'q1','kind':'routine','owner':'acme'}, {'id':'q2','kind':'complex','owner':'acme'}, {'id':'q3','kind':'unknown','owner':'acme'}]
def route(request,budget):
    if budget<=0:return 'budget_exhausted'
    if request['kind']=='routine':return 'local'
    if request['kind']=='complex':return 'premium'
    return 'review'
assert [route(r,10) for r in requests]==['local','premium','review']
assert route(requests[0],0)=='budget_exhausted'
print('routing contract checked; semantic difficulty classifier and quality remain unevaluated')
''','Routing fixtures can verify a policy without proving that a classifier can recognize task difficulty. Evaluate route selection, output quality and escalation on the same cases. Hybrid serving needs consistent response contracts, context limits, trace correlation and tenant ownership across both endpoints. A premium fallback is not permission to move previously local confidential data off-device.','Integrate the local/premium adapters with explicit data-routing consent, remaining-deadline checks and a capped budget. Compare all-premium, all-local and hybrid on a held-out workload. Test shared cache isolation, stale sources, provider failure and idempotent jobs across replicas.')
add(36, '''
gates={'quality_floor':True,'critical_failures_zero':True,'load_report_with_denominators':False,
       'restore_observed':True,'owner_isolation':True,'budget_and_rate_caps':True,'context_cache_policy':True}
missing=[name for name,passed in gates.items() if not passed]
assert missing==['load_report_with_denominators']
assert not all(gates.values())
print({'release_ready':False,'missing_evidence':missing,'configuration_is_not_scale_evidence':True})
''','Graduation is an evidence-backed release decision, not an automatic production-ready label. The final SaaS must connect tenant authentication, source-grounded work, reviewed actions, hybrid models, persistent state, evaluation, observability, quotas and recovery. Autoscaling configuration alone does not establish thousands of concurrent users. Unknown or unmet gates remain visible and constrain the claim.','Run a fresh-operator handover and the fixed final workload. Include actual deployed revision, measured concurrency, p95/quality/cost, 120-case report, context/cache manifest, restart/restore and a budget-exhaustion drill. Fix or explicitly defer every blocker; only claim the scale and conditions actually observed.')
