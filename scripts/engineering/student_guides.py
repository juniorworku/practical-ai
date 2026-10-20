"""Authored explanations, traces, bounded practice and complete solutions.
The practice deliberately stays smaller than the subsequent integration project.
"""
import textwrap
GUIDES={}
def add(n,prerequisite,explanations,trace,task,extension,hints,diagnosis):
    assert len(explanations)==len(trace)==len(hints)==3
    GUIDES[n]=dict(prerequisite=prerequisite,explanations=explanations,trace=trace,task=task,
      extension=textwrap.dedent(extension).strip()+'\n',hints=hints,diagnosis=diagnosis)

add(1,'Python functions, dictionaries and exceptions. A dataclass is introduced below; no SDK knowledge is assumed.',[
 'Start by listing what the caller needs before selecting a model: text input, audio output, tool calls and a maximum context are separate capabilities. A text-only model cannot satisfy an audio-output requirement by changing its prompt. Check the requested capability against explicit adapter metadata before a network call; a rejected request should consume no provider work.',
 'A provider adapter translates provider-specific fields into a stable application result. Here Result is a dataclass: its annotated fields define an explicit record, and frozen=True prevents accidental field reassignment after construction. An adapter is useful because the HTTP route can read result.status and result.text without knowing whether the provider called its field content or message.',
 'Usage has both a quantity and an origin. The supplied 12 input and 5 output counts are synthetic fixture counts, so the record says usage_kind=fixture. Real API usage may be missing or include other categories; do not replace unavailable usage with zero and label it measured. A returned draft also remains distinct from a reviewed, persisted final answer.'
],['Construct Result with five explicit fields; the fixture stores 12+5=17 units.','Observe that adapter returns draft; no caller approval or save has occurred.','Trace empty input through ValueError before any result is constructed.'],
 'Add capability preflight and a permanent-authentication error path. Check that an unsupported audio request never increments the call counter and an authentication failure never becomes a successful draft.', '''
calls=0
class AuthenticationFailure(Exception):pass
def guarded_adapter(question, capability='text', authenticated=True):
    global calls
    if capability not in {'text'}:return {'status':'unsupported','usage':None}
    if not authenticated:raise AuthenticationFailure('credentials rejected')
    calls+=1
    return adapter(question)
assert guarded_adapter('Hello','audio')['status']=='unsupported' and calls==0
try:guarded_adapter('Hello',authenticated=False)
except AuthenticationFailure:pass
else:raise AssertionError('authentication failure became success')
assert calls==0 and guarded_adapter('Hello').status=='draft' and calls==1
print('practice: unsupported/auth failures made no provider call; text produced one draft')
''',['List the capability set before calling adapter.','Count calls only after capability and authentication checks pass.','Assert both the returned status and the number of calls; an error string alone is insufficient.'],
 'If calls is nonzero after the audio test, preflight runs too late. If the auth case returns a Result, a permanent credential failure was swallowed. Correct ordering is capability → authenticated request → normalization; transient retry policy is a later concern.')
add(2,'Session 1: distinguish application records from provider responses. A SHA-256 digest is an identity fingerprint here, not encryption.',[
 'A stateless request does not remember earlier messages merely because they came from the same browser. The application selects and resends relevant turns. A stateful session instead references retained conversation state, but the application must still bind the session to an owner and enforce expiry. These are storage/lifecycle choices; neither guarantees an unlimited context window.',
 'Give retained sessions an owner and an expiry checked on every lookup. For example, a session for acme expiring at time 100 must reject other at time 99 and acme at time 100. Do not use an unguessable-looking session ID as your only permission check. Expired memory can be rebuilt from authorized durable records rather than silently reused.',
 'The cache key serializes owner, model, prompt/source versions and actual turns before hashing. Changing an input should change the key. A permission revision and expiration are separate validity conditions: an identical hash does not make revoked or expired content usable. The context allowance is window minus instructions, tool schemas, metadata and output reserve; exceeding it should be visible before provider work.'
],['The same turns with owner=other produce a different digest.','Changing source revision s1→s2 also changes the digest.','The baseline allowance is 1000−240−200=560 supplied units; adding 60 tool and 20 metadata units leaves 480.'],
 'Add permission-revision and expiry checks to a cached answer. Test the exact expiry boundary and a revoked permission without making a provider call.', '''
def cache_read(entry,owner,permission_revision,now):
    if entry['owner']!=owner or entry['permission']!=permission_revision or now>=entry['expires']:return None
    return entry['answer']
entry={'owner':'acme','permission':'role-1','expires':100,'answer':'approved synthetic policy'}
assert cache_read(entry,'acme','role-1',99)==entry['answer']
assert cache_read(entry,'acme','role-1',100) is None
assert cache_read(entry,'acme','role-2',99) is None
assert cache_read(entry,'other','role-1',99) is None
assert 1000-240-200-60-20==480
print('practice: expiry, owner and permission invalidation passed; remaining fixture allowance 480')
''',['A key match is necessary but not sufficient for reuse.','Use now >= expires to reject the exact expiry boundary.','Test owner, permission and time independently so one passing condition cannot hide another failure.'],
 'A revoked permission must miss even before expiry. If a role-2 request hits this record, add permission state to lookup validation. The 480 figure is fixture arithmetic, not a measured tokenizer or bill.')
add(3,'Python async def creates a coroutine; await suspends it so other work can progress. Review try/finally for cleanup.',[
 'A semaphore holds a finite number of permits. async with semaphore waits for a permit and releases it when the block exits, including on exceptions. This caps active service operations; it does not cap the number of waiting tasks. The six-task fixture is finite, while production admission needs a bounded pending queue too.',
 'An overall deadline includes time waiting for a semaphore, provider execution and retry delays. Put asyncio.timeout around the entire operation if queue wait must count. An inner HTTP timeout alone starts too late to bound total user waiting. A deadline should produce a recorded timeout outcome rather than silently remove a request from the report.',
 'Cancellation is control flow, not an ordinary successful result. A browser disconnect can cancel a task while it is waiting or holding a permit. finally releases your own resources, and the semaphore context releases its permit. After cancel(), await the task or gather it with return_exceptions=True so cleanup actually finishes before checking state.'
],['Six tasks compete for two permits; peak active reaches two.','Task 3 raises TimeoutError but its finally block decrements active.','gather keeps five results and one exception, and active returns to zero.'],
 'Hold a semaphore permit, cancel a waiting task, and prove it can be acquired afterward. Separately force an overall deadline while waiting.', '''
async def cancellation_check():
    gate=asyncio.Semaphore(1)
    await gate.acquire()
    waiting=asyncio.create_task(gate.acquire())
    await asyncio.sleep(0)
    waiting.cancel()
    await asyncio.gather(waiting,return_exceptions=True)
    try:
        async with asyncio.timeout(.02):await gate.acquire()
    except TimeoutError:pass
    else:raise AssertionError('waiting request ignored deadline')
    gate.release()
    async with asyncio.timeout(.02):
        async with gate:pass
    assert not gate.locked()
asyncio.run(cancellation_check())
print('practice: cancelled waiter cleaned up, queue deadline enforced, permit reusable')
''',['Cancel a waiter while the only permit is held by the test.','Await the cancelled task before releasing the original permit.','A final successful acquire/release proves there is no leaked permit; do not inspect private semaphore fields.'],
 'If the final acquire hangs, cleanup or release ownership is wrong. Use an outer deadline to turn that hang into a useful failure. Do not release a permit from a task that never acquired it.')
add(4,'Session 3: await, queues and cancellation. PCM16 means signed two-byte samples; the fixture uses mono audio.',[
 'For mono PCM16 at 16,000 samples/second, each second is 16,000×2=32,000 bytes. A 320-byte frame is 10ms. Channels multiply this byte rate. Browser WebM/Opus is compressed container data and cannot be sent as if it were these raw samples; encoding and playback rate must be agreed at each boundary.',
 'Backpressure lets the consumer limit the producer. await queue.put(frame) pauses when the finite queue is full, whereas put_nowait raises QueueFull immediately. Pausing is appropriate only if the upstream can wait; a physical microphone continues capturing, so its capture/drop/stop behavior must also be explicit. Buffering forever only converts overload into growing latency.',
 'Queue capacity has a time meaning. Two 10ms frames hold 20ms of queued audio, excluding frames being captured, transmitted or played. Add those other stages to end-to-end latency. A queue bound limits memory; it does not establish accurate speech or prompt response. Disconnect must terminate producer and consumer rather than leave them waiting on one another.'
],['The fast baseline producer accepts sequences 0 and 1 into a two-item queue.','Sequences 2–4 overflow visibly; accepted=2 and dropped=3.','The frame-duration assertion uses 320 bytes at 32,000 bytes/second to obtain 10ms.'],
 'Replace dropping with an awaiting producer and consumer for five synthetic frames. Preserve order, cap queued frames at two, and join all work cleanly.', '''
async def backpressure_check():
    q=asyncio.Queue(maxsize=2);seen=[];depths=[]
    async def produce():
        for sequence in range(5):
            await q.put(sequence);depths.append(q.qsize())
        await q.put(None)
    async def consume():
        while True:
            item=await q.get()
            try:
                if item is None:return
                seen.append(item);await asyncio.sleep(0)
            finally:q.task_done()
    async with asyncio.timeout(1):
        await asyncio.gather(produce(),consume());await q.join()
    assert seen==list(range(5)) and max(depths)<=2
asyncio.run(backpressure_check())
print('practice: five frames retained in order; queue stayed within two frames (20ms)')
''',['Start producer and consumer together with gather.','Use one explicit end sentinel and call task_done even for that sentinel.','Await queue.join after both tasks complete; a missing task_done makes this fail under the outer deadline.'],
 'If only two frames arrive, put_nowait/drop behavior remains. If join hangs, an item was not acknowledged. This synthetic producer can pause; measure what a real capture source does under congestion.')
add(5,'Session 4: frame queues and the distinction between capture, transmission and playback.',[
 'Barge-in means a new user turn interrupts the old reply. Generation cancellation, server queue removal and browser scheduled-node cancellation are three separate operations. Clearing a Python deque demonstrates only the queue part; the voice appendix also stops scheduled audio nodes. Tagging output with a turn/session identity helps reject late old output.',
 'A replay boundary distinguishes acknowledged work from uncertain work. In the fixture, last_ack=7 means sequences 6 and 7 must not be replayed as new. Sequences 8 and 9 are merely unacknowledged; whether audio may actually be replayed depends on the provider protocol. Acknowledgement of transport bytes is also different from approval of an external write.',
 'A session resumption handle can expose retained conversation and therefore acts like a secret. Bind lookup to the authenticated owner and expiry. On reconnect, an old socket can still deliver a late callback: compare the callback connection/generation with the active one before modifying playback or UI. A new connection must not be closed by the old connection’s cleanup.'
],['interrupt clears both old-turn frames and records new-turn.','Filtering with seq > last_ack removes already acknowledged sequences 6 and 7.','The remaining [8,9] are candidates for protocol-specific recovery, not blanket replay permission.'],
 'Add an owner/session-generation guard for late audio callbacks. Test that an old connection cannot enqueue audio into the new turn.', '''
def receive_audio(owner,generation,current,frame,out):
    if owner!=current['owner'] or generation!=current['generation']:return 'stale'
    out.append(frame);return 'queued'
current={'owner':'acme','generation':2};out=[]
assert receive_audio('acme',1,current,b'old',out)=='stale'
assert receive_audio('other',2,current,b'private',out)=='stale'
assert receive_audio('acme',2,current,b'new',out)=='queued'
assert out==[b'new']
print('practice: old-generation and wrong-owner audio rejected; current audio queued once')
''',['Give the active connection a monotonically changing generation.','Check owner and generation before touching the output queue.','Assert the queue contains only the new frame, not just that an error was returned.'],
 'Returning stale after appending still leaks old audio. Move validation before mutation. A successful callback filter does not test actual audible interruption; use the supplied browser project for that later check.')
add(6,'Sessions 1–5: adapter records, async limits, PCM, interruption and lifecycle. The voice appendix supplies the full transport app.',[
 'Choose one latency start event before collecting numbers, such as end of user speech. Audible latency ends when playable response audio begins; socket-open time and provider first-token time are different measurements. Record these fields separately so a fast connection does not hide a slow answer or playback backlog.',
 'A percentile is computed over a stated population. Sort the three observed audio latencies [150,240,1200]; nearest-rank p95 selects ceil(.95×3)=3, or 1200ms. The fourth attempt has no audio latency, so it stays in the failure count instead of being assigned zero. Three observations are a scoring example, not a stable production tail estimate.',
 'Quality and spend use all attempts. Only two of the four turns were correct, while every attempt consumed fixture units: 2+3+4+1=10. Cost per accepted turn is 10/2=5. A latency-only average could make an unusable assistant look healthy. Set quality, reliability and spend gates before testing, and leave a zero-acceptance cost ratio undefined rather than dividing by zero.'
],['Keep four attempts in reliability and spend.','Compute latency only for the three playable responses and label that denominator.','Use two accepted turns for useful-output cost; do not count the wrong audible response as accepted.'],
 'Implement a voice release decision that requires quality and no-audio gates in addition to p95. Prove the fast-but-silent run fails and that zero accepted outputs yield no cost ratio.', '''
def voice_report(rows):
    values=sorted(r['first_audio_ms'] for r in rows if r['first_audio_ms'] is not None)
    accepted=sum(r['correct'] for r in rows);failed=sum(r['first_audio_ms'] is None for r in rows)
    p95=values[ceil(.95*len(values))-1] if values else None
    ratio=sum(r['cost_units'] for r in rows)/accepted if accepted else None
    ready=bool(rows) and failed==0 and accepted/len(rows)>=.9 and p95 is not None and p95<=500
    return {'ready':ready,'cost_per_accepted':ratio,'no_audio':failed}
assert voice_report(turns)=={'ready':False,'cost_per_accepted':5,'no_audio':1}
assert voice_report([{'first_audio_ms':None,'cost_units':2,'correct':False}])['cost_per_accepted'] is None
print('practice: voice release blocked by quality/no-audio gates; zero-acceptance ratio is undefined')
''',['Define the accepted-output count independently of audio existence.','Guard empty latency and zero-acceptance populations explicitly.','Use AND between mandatory gates; a good latency must not compensate for failure.'],
 'If the original four-turn run passes, a quality or reliability gate is missing. These provisional numeric thresholds teach a decision rule; replace them with a justified workload target during the integrated capstone.')
add(7,'Python byte strings, dictionaries and SHA-256 from session 2. Parsers and provenance formats are introduced here.',[
 'A digest identifies exact bytes: changing one byte changes the content identity. It does not prove authorship, permission or safety. Use (owner,digest) for intake deduplication so identical bytes submitted by different organizations do not become a cross-owner access shortcut. Keep original bytes or a recoverable source reference for audit.',
 'Parsing is a lifecycle transition, not an upload acknowledgement. received means bytes were accepted; parsed means extraction succeeded; active means all later chunk/index/evaluation gates passed. A scanned PDF may contain no extractable text, so quarantine it with a visible reason. Keep the last active revision while a replacement is being processed.',
 'A locator lets someone inspect evidence at its origin. A PDF page number, DOCX paragraph/table ID and VTT time range serve different source formats. Store the locator with the digest/revision before cleaning text. Without it, a generated citation may look plausible while the student or reviewer cannot find the actual evidence.'
],['The same owner and exact bytes reuse one job key.','Another owner creates a separate scoped key even for identical bytes.','An oversized upload is rejected before creating another job.'],
 'Add a parse-result transition that quarantines empty extraction and never replaces the active revision with a failed one.', '''
active={'acme':'old-ready'};statuses={}
def finish_parse(owner,revision,sections):
    usable=bool(sections) and all(s.get('text','').strip() and s.get('locator') for s in sections)
    statuses[(owner,revision)]='parsed' if usable else 'quarantined'
    return statuses[(owner,revision)]
assert finish_parse('acme','scan-v2',[])=='quarantined'
assert active['acme']=='old-ready'
assert finish_parse('acme','text-v2',[{'text':'Synthetic policy','locator':'page:1'}])=='parsed'
assert active['acme']=='old-ready'  # Parsing alone cannot activate an index.
print('practice: empty extraction quarantined; parsed revision did not bypass activation')
''',['Keep parse status separate from the active pointer.','Require both usable text and a locator.','Test a valid parse as well as failure; neither should silently activate retrieval.'],
 'If a successful parse changes active, indexing/evaluation were skipped. If the scan appears parsed, empty extraction is being mistaken for a usable document. Run the supplied format parsers afterward, with synthetic files.')
add(8,'Session 7: source digests and locators. The baseline deliberately estimates word units rather than real model tokens.',[
 'A meaning boundary keeps a claim with the conditions needed to interpret it. “Returns accepted” alone is incomplete if the next sentence excludes opened items. Heading/section boundaries can preserve that relationship; fixed windows are repeatable but may split it. Semantic splitting adds another selection mechanism that must be evaluated rather than assumed superior.',
 'Before selecting chunks, reserve context for instructions, tool schemas, metadata and the answer. Use the target model tokenizer for an actual token limit; a word or character count is only a declared teaching estimate. If one complete rule exceeds the budget, reject it for a reviewed split rather than silently clipping away its exception.',
 'Compare chunking policies using the same labeled queries and source revision. Record which required evidence appears in the selected context, how much context is spent and whether the final claim is supported. Offsets and locators make a failed boundary inspectable. More chunks or more overlap are costs, not quality metrics by themselves.'
],['chunks preserves each source section as one record.','The 20-word-unit budget keeps the rule and exception together.','Budget=3 raises instead of producing a misleading clipped rule.'],
 'Implement budgeted selection that preserves whole sections and records omitted IDs. Use supplied word estimates and label them as estimates; do not claim a real tokenizer implementation.', '''
def select_sections(rows,word_allowance):
    selected=[];omitted=[];used=0
    for row in rows:
        cost=len(row['text'].split())
        if used+cost>word_allowance:omitted.append(row['id']);continue
        selected.append(dict(row));used+=cost
    return selected,omitted,used
chosen,omitted,used=select_sections(sections,12)
assert [r['id'] for r in chosen]==['rule'] and omitted==['shipping']
assert 'Opened items excluded.' in chosen[0]['text'] and used<=12
assert select_sections(sections,0)[0]==[]
print('practice: whole rule/exception retained; omitted section recorded; estimate stays within allowance')
''',['Compute cost before appending a complete section.','Return omitted IDs so budget loss is visible.','Check the actual exception text and zero-budget behavior.'],
 'If the exception disappears, selection is truncating text rather than choosing whole sections. If shipping vanishes without an omitted ID, the reviewer cannot distinguish budget omission from ingestion loss. The real-tokenizer comparison belongs to the next integration step.')
add(9,'Sessions 7–8: source revisions and bounded chunks. A vector is a list of numbers; training an embedding model is not required.',[
 'An embedding API maps text to coordinates in a particular learned space. Distance is meaningful only within a compatible model/version, dimension and normalization policy. Two models can both return three numbers with unrelated meanings. Reject incompatible records before insertion rather than padding vectors or mixing them behind a shared model name.',
 'Build a parallel index for a migration: leave v1 searchable, ingest the same approved corpus through the replacement model into v2, evaluate v2 on held-out labels, then switch an active pointer. This costs temporary storage and ingestion work but makes rollback possible. A successful embedding response does not establish retrieval quality.',
 'Activation is a state transition with conditions: expected model, numeric finite vectors, completed ingestion, scope checks and evaluation evidence. NaN is a floating-point value but has no valid distance ordering; booleans should not count as coordinates. For the cosine-distance index used here, a zero vector has no direction and is also rejected. Validate these before index activation, and preserve v1 when v2 fails.'
],['accept rejects a different vector length.','The same length under different-model is also rejected.','Only the declared fixture model/dimension is accepted; no semantic quality was measured.'],
 'Add finite-coordinate validation and an activation gate that leaves v1 active when v2 has missing or failing evidence.', '''
import math
def valid_vector(vector,dimensions):
    return len(vector)==dimensions and all(type(v) in (int,float) and math.isfinite(v) for v in vector) and any(v!=0 for v in vector)
assert valid_vector([1.,0.,0.],3)
assert not valid_vector([0.,0.,0.],3)
assert not valid_vector([float('nan'),0.,0.],3) and not valid_vector([True,0.,0.],3)
active_index='v1'
def activate(candidate,parsed,indexed,evaluated):
    global active_index
    if not (parsed and indexed and evaluated):return False
    active_index=candidate;return True
assert not activate('v2',True,True,False) and active_index=='v1'
assert activate('v2',True,True,True) and active_index=='v2'
print('practice: non-finite/bool coordinates rejected; failed migration retained v1; checked v2 activated')
''',['Use math.isfinite; checking numeric type alone accepts NaN.','Keep the old active pointer until every required gate passes.','Test both failed and successful activation without destroying either revision.'],
 'If NaN passes, type checking was mistaken for numeric validity. If v1 is lost on failed evaluation, migration and activation have been combined incorrectly. The API/SQL appendix then shows where these checks sit around actual generation and insertion.')
add(10,'Session 9: compatible indexes and revision activation. Basic SQL WHERE and ORDER BY are assumed.',[
 'Tenant filtering establishes the authorized search universe. Derive owner from server authentication, select the active source revision, then search within that scope. Similarity can only rank eligible records; a closer private vector cannot override permission. An empty result for an unknown owner is expected, not a reason to broaden scope.',
 'Exact search considers all eligible vectors and gives a comparison baseline. Approximate nearest-neighbor search such as HNSW avoids some comparisons for speed, which can miss neighbors. Compare latency and retained relevant records under identical authorized filters. The three-row SQL fixture teaches scope and ordering, not an index-performance benchmark.',
 'ANN retrieval may find global candidates and apply filters in a way that yields fewer than k eligible results. Do not backfill with another tenant. Distinguish “no eligible evidence,” “relevant evidence missed” and “fewer than requested results.” Recall must be measured against labeled authorized evidence and, when evaluating approximation, the exact eligible baseline.'
],['The other owner has score .99 but is removed before output.','acme/v1 returns a1, not acme/v2 a2.','unknown/v1 returns an empty list without fallback to public/global rows.'],
 'Score approximate retrieval against exact authorized IDs and reject any scope leak before computing an aggregate recall.', '''
def ann_recall(exact_ids,approximate_ids,authorized_ids):
    if not set(approximate_ids)<=set(authorized_ids):raise PermissionError('scope leak')
    return len(set(exact_ids)&set(approximate_ids))/len(set(exact_ids)) if exact_ids else None
assert ann_recall(['r1','r2'],['r1'],['r1','r2'])==.5
assert ann_recall([],[],[]) is None
try:ann_recall(['r1'],['private'],['r1'])
except PermissionError:pass
else:raise AssertionError('unauthorized ANN output scored as ordinary miss')
print('practice: approximation recall 0.5; empty baseline undefined; leaked owner rejected')
''',['Scope validation must precede scoring.','Deduplicate IDs in numerator and denominator.','An empty exact baseline has no recall denominator; report it separately.'],
 'Counting b1 as merely a retrieval miss hides an authorization failure. Returning recall=1 for an empty baseline also hides lack of evidence. The full SQL appendix is introduced in session 9; run it before the larger ANN experiment.')
add(11,'Session 10: scoped ranked candidates. Reciprocal rank and mean are explained by the examples below.',[
 'Lexical matching is valuable for exact product codes, names and rare terms. Dense retrieval can find paraphrases that share meaning without words. Neither method authorizes a record or guarantees relevant evidence. Keep both lists in the same owner/revision scope before combining them.',
 'Dense retrieval returns similarity-ranked IDs from an embedding space, not calibrated truth probabilities. Lexical and dense score ranges may differ, so a raw sum can let one scale dominate. Preserve each original ranking for comparison; otherwise a claimed hybrid improvement cannot be traced to either source.',
 'RRF gives each item a contribution 1/(k+rank) from each list, with rank starting at one. In the fixture b is second lexically and first densely, so it gains two strong contributions. Deduplicate within each list before counting contributions; repeated IDs are not independent votes. MRR then scores the position of the first relevant item for each query.'
],['RRF ignores duplicate IDs inside an individual list via dict.fromkeys.','b outranks a because its summed reciprocal-rank contribution is larger.','The combined list has four unique IDs; relevant labels are still needed to assess quality.'],
 'Add a reciprocal-rank metric and prove a duplicate candidate does not inflate fusion. Compare the same relevant ID in baseline and fused results.', '''
def reciprocal_rank(ranked,relevant):
    return next((1/rank for rank,item in enumerate(ranked,1) if item in relevant),0)
assert rrf([['a','a','b'],dense])==rrf([['a','b'],dense])
assert reciprocal_rank(lexical,{'b'})==.5
assert reciprocal_rank(combined,{'b'})==1
assert reciprocal_rank(combined,{'missing'})==0
print('practice: duplicate vote removed; relevant b reciprocal rank improved from 0.5 to 1 on this fixture')
''',['Deduplicate before assigning ranks, not after scoring.','Find the first relevant position and use one divided by that position.','An improvement on b is one labeled observation; do not generalize to the corpus.'],
 'If duplicate a changes the fused score, one retriever is voting multiple times for the same item. If MRR is nonzero for missing, the metric is not using relevance labels correctly.')
add(12,'Session 11: immutable candidate IDs and ranked lists. The optional adapter is separate from the deterministic fixture.',[
 'A candidate ceiling bounds how many texts are sent to the reranker. Reranking cannot recover missing evidence, so first evaluate candidate recall. Sending a larger set increases text processing, latency and possibly spend; the right ceiling depends on observed quality gain and a remaining request deadline.',
 'The provider returns positions into the exact candidate array it received. Position 1 in [c3,c1,c2] means c1. Sorting that array before mapping changes identity even if every index is in range. Save the immutable submitted list and reject negative, out-of-range or duplicate indexes before using the output.',
 'A fallback policy defines what happens when reranking is unavailable or would consume the remaining deadline. Returning the authorized original ranking can be acceptable if it is labeled and evaluated; fabricating reranker scores is not. Decide the fallback before failure and retain the failure in cost/quality reports.'
],['Response index 1 maps to c1 in the original three-item array.','Index 2 maps to c2, preserving candidate identity.','Index 99 raises instead of inventing a document ID.'],
 'Implement a deadline-aware mapping wrapper that rejects duplicate indexes and returns a labeled original-order fallback when time is insufficient.', '''
def bounded_rerank(response,remaining_ms):
    if remaining_ms<50:return {'mode':'fallback','ids':[c['id'] for c in candidates]}
    indexes=[r['index'] for r in response]
    if len(indexes)!=len(set(indexes)):raise ValueError('duplicate candidate')
    return {'mode':'reranked','ids':map_results(response)}
assert bounded_rerank(provider_response,20)['mode']=='fallback'
assert bounded_rerank(provider_response,100)['ids']==['c1','c2']
try:bounded_rerank([{'index':1},{'index':1}],100)
except ValueError:pass
else:raise AssertionError('duplicate accepted')
print('practice: low-budget fallback labeled; original index mapping preserved; duplicate rejected')
''',['Check the time budget before interpreting a provider result.','Validate duplicates against original indexes.','The fallback must include its mode so the report cannot count it as a successful rerank.'],
 'If fallback receives new relevance scores, it is inventing evidence. If duplicate IDs appear, validate both index uniqueness and identity mapping. The 50ms threshold is a supplied test policy, not measured provider latency.')
add(13,'Sessions 7–12: source scope, retrieval and stable citation identity. No automatic semantic judge is assumed.',[
 'Citation identity checks whether each cited ID belongs to the selected authorized evidence. It is a useful mechanical gate, but it only proves a reference can be resolved. An answer can cite a real page and say the opposite of that page. Keep citation ID and immutable locator/revision together for inspection.',
 'Entailment asks whether a claim actually follows from the cited evidence. The baseline source permits unopened items; the claim permits opened items, so a reviewer labels it unsupported. Keyword overlap would be high even though meaning is reversed. Break long answers into claims and attach a support decision and evidence for each.',
 'Applicability asks whether a true rule governs this user, date and situation. If the item condition is missing, clarify; if evidence is absent or conflicting, abstain or review. These outcomes differ from answering. An old policy may support a sentence literally while being inapplicable to the active revision.'
],['The source p1 exists, so identity=True.','The reviewed label is False because opened reverses the policy condition.','A response with zero supported claims remains unready despite valid citation identity.'],
 'Implement answer/clarify/abstain selection from explicit evidence and applicability state. Test that an old revision cannot authorize a current answer.', '''
def grounded_decision(has_evidence,revision_current,condition_known,conflict=False):
    if not has_evidence or not revision_current or conflict:return 'abstain'
    if not condition_known:return 'clarify'
    return 'answer'
assert grounded_decision(True,True,True)=='answer'
assert grounded_decision(True,True,False)=='clarify'
assert grounded_decision(True,False,True)=='abstain'
assert grounded_decision(True,True,True,True)=='abstain'
print('practice: current evidence answers; missing condition clarifies; stale/conflicting evidence abstains')
''',['Handle missing/stale/conflicting evidence before answering.','A missing user condition is different from missing evidence.','These booleans are supplied reviewed state; the function is not a semantic understanding model.'],
 'Answering when revision_current=False confuses support with applicability. If every missing field becomes abstain, the student loses a useful clarification path. Record how each input state was established in the integrated app.')
add(14,'Session 13: authorized citations and reviewed answer states. An async generator yields provisional events over time.',[
 'A draft delta is a fragment, not a complete answer. Append fragments to a visible draft buffer while retaining the original question. The user can see progress without the application claiming that citations, schema or factual review have finished. Rendering a delta should not mutate the approved-answer store.',
 'A completion event signals the stream reached its normal terminal boundary and carries source IDs/status. Validate those IDs against the authorized evidence before making the result eligible for later review/cache. Completion of generation is not human factual approval; keep those states separate.',
 'A partial-result policy handles disconnect, error and cancellation explicitly. Keep the draft as incomplete, preserve the question and stop sibling work. Never let finally mean successful completion: finally also runs on failures. Full-answer caches should accept only the validated generation-complete state under the correct owner/revision key.'
],['Two delta events build provisional text.','Only the third event marks normal generation completion with p1.','Removing the last event leaves a partial stream; nonempty text alone cannot complete it.'],
 'Build an event reducer that accepts authorized completion, marks stream errors incomplete, refuses unknown source IDs and rejects data after completion.', '''
def reduce_events(events,allowed_sources):
    text='';state='incomplete';terminal=False
    for event in events:
        if terminal:raise ValueError('event after terminal completion')
        if event['event']=='draft_delta':text+=event['text']
        elif event['event']=='draft_complete':
            if not set(event['source_ids'])<=allowed_sources:raise PermissionError('citation scope')
            state='generation_complete';terminal=True
        elif event['event']=='error':state='incomplete';break
    return {'text':text,'state':state}
partial_events=[{'event':'draft_delta','text':'Draft'},{'event':'error'}]
assert reduce_events(partial_events,{'p1'})['state']=='incomplete'
assert reduce_events([{'event':'draft_complete','source_ids':['p1']}],{'p1'})['state']=='generation_complete'
try:reduce_events([{'event':'draft_complete','source_ids':['private']}],{'p1'})
except PermissionError:pass
else:raise AssertionError('private citation accepted')
try:reduce_events([{'event':'draft_complete','source_ids':['p1']},{'event':'draft_delta','text':'late'}],{'p1'})
except ValueError:pass
else:raise AssertionError('late delta accepted after completion')
print('practice: error remains incomplete; allowed completion recognized; private citation and late delta rejected')
''',['Use explicit states rather than bool(text).','Validate the completion provenance before changing state.','An incomplete draft can be retained for display but must not enter the complete-answer cache.'],
 'If an error leaves generation_complete, the reducer is treating cleanup or text presence as success. Even a valid completion still needs the factual review policy from session 13.')
add(15,'Sessions 7–14: the capstone combines intake, scoped retrieval, grounding and draft streaming. Start from the smaller offline scoring task.',[
 'The source lifecycle determines which records can be retrieved. received and parsed are not active; activation follows indexing and checks. Keep status visible in the UI and preserve a prior working revision after replacement failure. The capstone should expose this state rather than silently search every uploaded file.',
 'No-answer evaluation distinguishes a question with no source support from an answerable question whose evidence was missed. Only answerable queries have a relevant-passage recall denominator. Score unsupported questions for the correct abstain/clarify outcome separately, and retain failed retrieval as a failure rather than calling all abstention safe.',
 'Retrieval and answer metrics diagnose different defects. Passage recall@k is |retrieved relevant IDs|/|gold relevant IDs|, averaged over answerable queries. Hit rate only asks whether at least one gold ID appears. With two gold passages and one retrieved, recall is .5 but hit rate is 1. Final claim support must still be reviewed even if recall is perfect.'
],['q1 retrieves its gold p1 within the first two results.','q2 has no gold and is evaluated for abstention, not passage recall.','q3 misses p3, so mean recall across q1 and q3 is .5.'],
 'Add a multi-passage gold case, calculate passage recall correctly and report no-source behavior separately.', '''
def retrieval_report(dataset,k):
    eligible=[q for q in dataset if q['gold']]
    recalls=[len(set(q['ranked'][:k])&q['gold'])/len(q['gold']) for q in eligible]
    no_source=[q for q in dataset if not q['gold']]
    return {'mean_recall':sum(recalls)/len(recalls) if recalls else None,
            'no_source_correct':sum(q['actual']==q['expected'] for q in no_source)}
extra={'id':'q4','gold':{'p5','p6'},'ranked':['p5'],'actual':'answer','expected':'answer'}
assert retrieval_report([extra],2)['mean_recall']==.5
assert retrieval_report(queries,2)=={'mean_recall':.5,'no_source_correct':1}
print('practice: multi-passage recall is 0.5, not hit rate 1; no-source behavior scored separately')
''',['Do not use bool(intersection) for passage recall.','Divide each query intersection count by its own gold count before averaging.','Exclude empty gold sets from recall but retain them in the behavior report.'],
 'If the extra case scores 1, you computed hit rate. If no-source queries disappear entirely, the report hides abstention behavior. Use this scorer in the capstone report before comparing lexical/hybrid/reranked systems.')
add(16,'Python dictionaries and set comparison; source/owner boundaries from session 10. OAuth grants are an integration prerequisite, not model output.',[
 'Tool binding presents a function name and argument schema so a model can propose a call. The proposal is untrusted data: the application selects the registered function and validates required/extra fields and types. Never eval a function name or run code returned by the model. A schema-valid proposal can still be unauthorized.',
 'A connector scope is authority granted to an application for an account or resource. Slack channel membership and calendar ownership constrain it further. Bind that grant to server-established actor identity and check destination scope at dispatch. A model-supplied owner or channel cannot expand the authenticated actor’s grants.',
 'A draft boundary separates local preparation from external effects. Returning status=draft can be safe without send authority; a send or create operation needs a different dispatcher contract and current approval. Whitelist effect types, rather than assuming every allowed tool is read-only. The optional connector example later supplies actual HTTP methods behind these checks.'
],['dispatch requires the exact field set channel,text.','The private channel fails the actor scope check even with valid field names.','send_reply is not registered; draft_reply on support returns a local draft.'],
 'Reject extra owner fields and non-string arguments, then prove a valid draft remains possible. Add no send behavior.', '''
assert dispatch(actor,'draft_reply',{'channel':'support','text':'Hi','owner':'other'})=='rejected'
assert dispatch(actor,'draft_reply',{'channel':'support','text':42})=='invalid_type'
result=dispatch(actor,'draft_reply',{'channel':'support','text':'Review this answer'})
assert result['owner']=='acme' and result['status']=='draft'
print('practice: injected owner/invalid types rejected; authenticated local draft preserved')
''',['Compare the complete key set to the allowed fields.','Keep owner out of model arguments; derive it from actor.','Add a positive test after negative tests so a deny-everything implementation cannot pass.'],
 'If the result owner changes with arguments, model data has crossed the identity boundary. If the positive case fails, validation is too broad or ordered incorrectly. No real connector call is needed for this exercise.')
add(17,'Basic SQL UPDATE/WHERE and transactions. sqlite3.connect opens a file-backed store; closing and reopening tests persistence.',[
 'A checkpoint stores enough workflow state to resume at a controlled boundary: job ID, owner, state and version. Persist before acknowledging a human pause. The SQLite example closes the connection and reopens the same file to distinguish durable records from process variables. An in-memory graph saver cannot pass a process-restart test.',
 'A thread/job ID locates state but does not authorize it. A conditional update includes owner as well as ID, expected state and version. rowcount=1 means this request consumed the transition; rowcount=0 means no matching authorized current state existed. Return a controlled conflict/denial rather than silently applying a stale review.',
 'Graph interrupt/resume may rerun node code preceding an interrupt. Place irreversible effects behind a durable, approved dispatcher boundary, not in code that may replay. The optional LangGraph example first demonstrates SDK control flow with an explicitly in-memory saver; the SQL baseline teaches the persistence/version behavior you must retain when choosing a durable checkpointer.'
],['Write awaiting_review/version 1 to the file and close the connection.','After reopen, wrong owner updates zero rows; acme/version 1 updates one.','A second acme/version 1 update affects zero rows because state/version changed.'],
 'Create a separate small checkpoint table and test restart, wrong-owner denial and stale-version rejection using conditional updates.', '''
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'practice.sqlite';store=sqlite3.connect(path)
    store.execute('CREATE TABLE checkpoint(id TEXT PRIMARY KEY,owner TEXT,state TEXT,version INTEGER)')
    with store:store.execute('INSERT INTO checkpoint VALUES(?,?,?,?)',('job','acme','paused',1))
    store.close();store=sqlite3.connect(path)
    def advance(owner,version):
        with store:return store.execute("UPDATE checkpoint SET state='ready',version=version+1 WHERE id='job' AND owner=? AND version=? AND state='paused'",(owner,version)).rowcount
    assert advance('other',1)==0 and advance('acme',0)==0
    assert advance('acme',1)==1 and advance('acme',1)==0
    store.close()
print('practice: reopened checkpoint rejects wrong owner/stale version; one transition succeeds')
''',['Persist before closing the first connection.','Include expected state and version in the UPDATE predicate.','Check affected rows rather than assuming executing SQL means the transition happened.'],
 'If the duplicate advances again, either version/state was not checked or the update did not increment it. A file-backed local checkpoint is a baseline; production replicas need a suitably shared store and tested concurrency semantics.')
add(18,'Session 17: persisted state/version checks. Canonical JSON serialization and hashing detect payload changes; they are not authentication.',[
 'Approval authorizes an exact effect payload, not a vague task name. Include calendar/destination, start/end with timezone, recipients and revision. Canonical serialization ensures stable field ordering before hashing. Changing a time or attendee after review must change the fingerprint and invalidate approval.',
 'Revocation is checked at execution time: a reviewer who had authority yesterday may have lost it today. A matching hash only proves payload equality; load the approval and current role from trusted application state. Do not accept a model-generated approval dictionary as the reviewer’s actual decision.',
 'Expiry uses a precise boundary: now < expires permits, now >= expires denies. Check time interval validity before presenting a proposal; naive times without offsets are ambiguous. Normalize equivalent instants consistently for comparison, and require end after start. Idempotency and remote reconciliation are additional requirements taught separately.'
],['The unchanged payload at time 99 with active reviewer passes.','Changing start from 10:00 to 11:00 changes the digest and fails.','At exact expiry 100, or with an inactive reviewer, the same payload fails.'],
 'Validate a timezone-aware start/end interval before approval. Test a valid interval, a reversed interval and a naive time.', '''
from datetime import datetime
def valid_interval(start,end):
    try:a=datetime.fromisoformat(start);b=datetime.fromisoformat(end)
    except ValueError:return False
    return a.utcoffset() is not None and b.utcoffset() is not None and b>a
assert valid_interval('2026-11-03T10:00:00+03:00','2026-11-03T11:00:00+03:00')
assert not valid_interval('2026-11-03T11:00:00+03:00','2026-11-03T10:00:00+03:00')
assert not valid_interval('2026-11-03T10:00:00','2026-11-03T11:00:00')
print('practice: aware increasing interval accepted; reversed/naive intervals rejected before approval')
''',['Parse ISO timestamps rather than comparing their strings.','Require timezone offsets for both endpoints.','Do not replace missing timezone with the server default without a user-visible rule.'],
 'If naive times pass, a proposal may execute at a different instant on another host. If reversed intervals pass, the approved payload is invalid before any external API call. A valid interval still needs current exact-payload approval.')
add(19,'Sessions 2 and 13: cache invalidation, applicability and source evidence. Summarization is lossy compression.',[
 'Selected memory is a bounded subset of durable facts, recent turns and tool results. Choose by owner, permission, relevance and revision before budgeting. Persist originals separately so an omitted condition can be recovered. Pasting every historic message makes context expensive and may reintroduce revoked or stale evidence.',
 'Summary fidelity means preserving what changes a decision: dates, exceptions, scope and uncertainty. “Returns within 14 days” loses the opened-item exclusion, even if it is shorter and fluent. Evaluate compression against source facts and answer cases; token savings alone do not establish useful compression.',
 'An invalidation trigger changes whether retained content is usable: source revision, membership, prompt/model policy, expiry or retention requirements. A different source revision gives a different cache key in the baseline, but old entries still need permission/retention checks. Application answer caches, conversation memory and provider KV caches are separate objects with different lifecycles.'
],['The v1 and v2 summaries receive different fingerprints.','The v1 fixture retains the exception as text.','The other owner cannot share the same key even for the same question/revision.'],
 'Write an explicit owner/permission-aware memory selector and a reviewed summary-fidelity gate. Reject a compressed summary whose required exception is missing.', '''
records=[{'owner':'acme','permission':'r1','words':5,'summary':'Unopened only; opened excluded.'},
         {'owner':'other','permission':'r1','words':1,'summary':'Private'}]
def select_memory(owner,permission,allowance):
    chosen=[];used=0
    for row in records:
        if row['owner']!=owner or row['permission']!=permission:continue
        if used+row['words']>allowance:continue
        chosen.append(row);used+=row['words']
    return chosen
assert len(select_memory('acme','r1',5))==1 and select_memory('acme','revoked',5)==[]
# This is an explicit reviewed fact flag, not a semantic classifier.
reviewed={'preserves_rule':True,'preserves_exception':False}
assert not all(reviewed.values())
print('practice: scoped memory budget enforced; revoked memory excluded; missing-exception review failed')
''',['Filter scope before considering size.','Reject revoked memory even when the text fits.','Use reviewed fact labels here; string containment is not a general semantic fidelity judge.'],
 'If the short private row enters the chosen list, cost optimization overrode authorization. A summary that fails the required-exception review must not be promoted merely because its word count is low.')
add(20,'Session 3: concurrency, and session 13: source support. A framework is an implementation choice, not an evaluator.',[
 'Coordination overhead includes duplicated prompts, retrieval, model calls, queueing and state. Two workers can reduce wall time only when work can overlap meaningfully. Keep a single-workflow baseline with the same input and quality bar. Compare total accepted-output spend, not only the fastest branch.',
 'Branch provenance records who produced a claim, from which source/revision, with what outcome and cost. Agreement between two workers using the same source is not independent verification. Deduplicate claims for presentation, while retaining both calls in cost accounting and both provenance records for debugging.',
 'Conflict arbitration determines what happens when branches disagree. Do not concatenate incompatible claims or count votes without evidence. A safe first policy is review when distinct supported claims conflict. LangChain, LangGraph and CrewAI organize composition, state or roles differently; adopt one only after the simpler baseline exposes a concrete requirement.'
],['Both branches return p1 and the same claim.','The set has one unique claim but total cost is 4, not 2.','No quality gain was observed, so the fixture cannot justify delegation.'],
 'Add a conflict-aware merge that retains costs/provenance and routes incompatible claims to review.', '''
def merge_branches(results):
    claims={r['claim'] for r in results}
    return {'state':'review' if len(claims)>1 else 'draft','cost':sum(r['cost'] for r in results),
            'sources':[r['source'] for r in results]}
a={'claim':'14 days','cost':2,'source':'p1'};b={'claim':'30 days','cost':3,'source':'p2'}
assert merge_branches([a,b])=={'state':'review','cost':5,'sources':['p1','p2']}
assert merge_branches([a,a])['cost']==4 and merge_branches([a,a])['state']=='draft'
print('practice: conflicting claims require review; agreement still retains duplicate spend')
''',['Keep all costs even if claims deduplicate.','Use distinct claims to expose conflict; do not choose the last result.','Draft is not factual approval: a separate source-support check remains necessary.'],
 'If cost falls when claims deduplicate, accounting hides real calls. If p2 overwrites p1 silently, merge order is deciding truth. The review rule is deliberately conservative and must be refined using evidence in a real system.')
add(21,'Session 16: proposal/schema/authority separation. JSON-RPC is a message format; MCP adds negotiated lifecycle and capabilities.',[
 'The MCP host is the user-facing application coordinating model interaction and permissions. It maintains clients that connect to servers. A server exposes bounded capabilities such as a policy lookup; it is not automatically the host or the authenticated end user. Keep credentials and resource scope attached to the actual connection.',
 'Capability discovery reports what a server says it can provide: tools, resources or prompts. Initialization negotiates protocol support before discovery/invocation. Descriptions may be untrusted, and discovering a tool does not grant permission to use it. The baseline JSON object illustrates a discovery result only; the supplied SDK client/server demonstrates a real initialization and stdio round trip.',
 'The invocation boundary validates the chosen tool, argument schema, authenticated owner and returned data. An argument named owner does not authenticate anyone. Restrict filesystem or connector access in server code, and validate results before using them as model context. Transport support and cancellation behavior must be tested per server.'
],['The discovered tool set is compared to the application allowlist.','The proposed claimed_owner differs from authenticated_owner.','The fixture labels its authority source as application authentication, not discovery metadata.'],
 'Implement a one-tool dispatcher with strict arguments and an owner check. Reject unknown tools, extra fields and cross-owner requests.', '''
def invoke_tool(tool,args,actor_owner):
    if tool!='lookup_policy' or type(args) is not dict or set(args)!={'id','owner'}:return 'invalid'
    if not all(type(v) is str for v in args.values()):return 'invalid'
    if args['owner']!=actor_owner:return 'denied'
    policies={('acme','p1'):'Synthetic approved policy'}
    return {'status':'found' if (actor_owner,args['id']) in policies else 'not_found'}
assert invoke_tool('lookup_policy',{'id':'p1','owner':'other'},'acme')=='denied'
assert invoke_tool('lookup_policy',{'id':'p1','owner':'acme','path':'/'},'acme')=='invalid'
assert invoke_tool('lookup_policy',{'id':'p1','owner':'acme'},'acme')['status']=='found'
assert invoke_tool('lookup_policy',{'id':'p1','owner':'other'},'other')['status']=='not_found'
print('practice: scoped invocation passed; cross-owner and extra-field requests rejected')
''',['Treat actor_owner as trusted server context, not a model-controlled argument.','Validate exact argument names and types before lookup.','The fixture tests invocation policy; run the supplied MCP SDK pair separately for protocol behavior.'],
 'If claimed owner overrides actor_owner, discovery/proposal data has been mistaken for authority. Passing this dispatcher does not prove MCP handshake compatibility; that is why the real SDK appendix is separate.')
add(22,'Sessions 17–18: durable state, exact approval and version checks. Local transactions cannot roll back remote effects.',[
 'A scoped operation key identifies one intended effect for one owner/payload revision. Persist it before dispatch and reuse it across retries/reconciliation. Giving each HTTP attempt a fresh key makes duplicate delivery look like a new operation. A database unique constraint can prevent duplicate local claims, but the destination has its own guarantees.',
 'An uncertain outcome occurs when a remote system may have committed but its acknowledgement is lost. The local caller does not know whether it failed. Keep uncertain and inspect the original destination/operation ID before another write. Retrying with a new calendar ID can create a second event.',
 'Reconciliation compares observed remote state with the exact approved payload and updates the ledger to committed, absent or still uncertain. Do not infer committed just because something with a similar title exists. The dictionary fixture is single-process; the durable state example shows local persistence, while remote consistency remains a separate integration test.'
],['The first approved call appends one fake effect but loses its response.','The ledger retains uncertain under the same scoped key.','The second call returns reconcile and does not append another effect.'],
 'Add reconciliation that resolves an observed original key without dispatching again. Keep an absent/unknown remote observation uncertain rather than fabricating success.', '''
def reconcile(key,remote_keys):
    if ledger.get(key)!='uncertain':return ledger.get(key,'unknown')
    if key in remote_keys:ledger[key]='committed'
    return ledger[key]
key='acme:event-1:r2'
assert reconcile(key,set())=='uncertain' and len(effects)==1
assert reconcile(key,{key})=='committed' and len(effects)==1
assert schedule(key,True)=='already_committed' and len(effects)==1
print('practice: original operation reconciled without redispatch; one fake effect retained')
''',['Do not call schedule from the reconciliation function.','Resolve only the exact original key.','Count effects after each observation; a correct status string can hide a duplicate write.'],
 'If effects grows during reconciliation, the implementation is retrying rather than observing. A missing observation may reflect eventual consistency, so this teaching policy keeps the outcome uncertain until a destination-specific resolution rule exists.')
add(23,'Sessions 17 and 22: durable state and duplicate operation handling. The connector appendix introduces signature verification.',[
 'A durable inbox stores a verified delivery ID and payload digest before acknowledging acceptance. Then a worker can retry processing after restart without requiring the webhook sender to reproduce lost data. An in-memory set only teaches the deduplication shape; it loses accepted work when the process exits.',
 'Deduplication is scoped by owner/event ID. Repeated identical content is a duplicate; the same ID with changed content is a conflict worth retaining/rejecting, not silently overwriting. Worker retry state belongs to the stored job. A provider outage must not remove the already accepted inbox record.',
 'Signature/replay checks authenticate the exact raw body and timestamp before parsing/trusting its event fields. Do not serialize parsed JSON again before signature validation, because whitespace/key order can change signed bytes. A valid signature is distinct from allowed workspace/channel scope. Check freshness, identity and destination authority independently.'
],['Two deliveries are logged but only one memory job is created.','The worker changes the existing job to retry_wait rather than deleting it.','The printed storage label is memory, explicitly showing the durability gap.'],
 'Replace the memory-only deduplication test with a file-backed scoped inbox. Test duplicate, changed-content conflict and restart readback.', '''
import sqlite3,tempfile,hashlib
from pathlib import Path
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'inbox.sqlite';db=sqlite3.connect(path)
    db.execute('CREATE TABLE inbox(owner TEXT,event TEXT,digest TEXT,state TEXT,PRIMARY KEY(owner,event))')
    def accept(owner,event,raw):
        digest=hashlib.sha256(raw).hexdigest()
        old=db.execute('SELECT digest FROM inbox WHERE owner=? AND event=?',(owner,event)).fetchone()
        if old:return 'duplicate' if old[0]==digest else 'conflict'
        with db:db.execute('INSERT INTO inbox VALUES(?,?,?,?)',(owner,event,digest,'queued'))
        return 'accepted'
    assert accept('acme','e1',b'original')=='accepted'
    assert accept('acme','e1',b'original')=='duplicate'
    assert accept('acme','e1',b'changed')=='conflict'
    db.close();db=sqlite3.connect(path)
    assert db.execute('SELECT state FROM inbox').fetchall()==[('queued',)]
    db.close()
print('practice: scoped inbox survived reopen; duplicate/conflict did not create extra jobs')
''',['Use a composite unique key and retain a digest of the exact body.','Compare a repeated key against its original digest.','Close/reopen the store before asserting the accepted job still exists.'],
 'If restart loses the job, the durable path was not used or committed. This serial SQLite example does not prove multi-worker claim safety; use atomic insert/conflict handling and a shared store for that integration.')
add(24,'Sessions 16–23: dispatch authority, checkpoints, approvals, selected memory, reconciliation and inbox deduplication.',[
 'Bounded autonomy means the system can monitor and prepare within declared read scopes while consequential writes stay controlled. First build a deterministic event→evidence→draft→review pipeline. Add agent choice only where a fixed workflow demonstrably lacks required behavior. The capstone does not need unrestricted tool access to be useful.',
 'A reviewed action passes current scope, source support, exact-payload approval and duplicate/uncertain-operation checks at dispatch. A proposal is not permission. Test state transitions by actually invoking the dispatcher with revoked scope and stale data; literal expected/actual strings cannot test behavior.',
 'Connector evidence records what a particular granted integration actually did: scope, request/event IDs, stable error category and observed destination state. Fake destinations allow deterministic tests without sending messages. Live connector availability, OAuth refresh and factual quality are separate observations; do not treat a successful fake call as those observations.'
],['The capstone fixture computes outcomes through a dispatcher rather than copying expected labels.','An unapproved proposal remains a draft; revoked scope is denied.','A lost acknowledgement produces uncertain and a repeated key is reconciled without a second effect.'],
 'Extend the capstone dispatcher with a stale-payload approval test and a missing-evidence test. Assert the effect count stays unchanged on both.', '''
workflow=WorkspaceFixture()
proposal={'owner':'acme','channel':'support','text':'Unopened only','revision':1}
assert workflow.process('event-1',proposal,scope=True,evidence=True,approval=review({**proposal,'text':'different reviewed text'}))=='needs_review'
assert workflow.process('event-2',proposal,scope=True,evidence=False,approval=review(proposal))=='abstain'
assert workflow.effects==[]
assert workflow.process('event-3',proposal,scope=True,evidence=True,approval=review(proposal))=='committed'
assert len(workflow.effects)==1
print('practice: stale approval/missing evidence caused no effect; approved supported proposal committed once')
''',['Fingerprint all effect fields and compare with the reviewed fingerprint at dispatch.','Missing evidence should stop the effect even with valid approval.','Check the effect list as well as the returned states.'],
 'If either negative case writes, the workflow has an effect before its gates. This fixture checks exact payload identity under a supplied trusted review; the live dispatcher must also verify current reviewer authority and expiry, as taught in session 18.')
add(25,'Session 13: identity, entailment and applicability. Fractions below summarize supplied reviewed labels, not automatic truth.',[
 'Faithfulness asks whether response claims are supported by the selected context. Split an answer into claims, inspect the cited applicable evidence, label each claim supported/unsupported/uncertain and retain reasons. In the two-claim fixture one is supported, so the reviewed support fraction is 1/2. Empty or unreviewed claim sets need an explicit unavailable state.',
 'Relevance asks whether an answer addresses the user question. A perfectly supported shipping sentence can be irrelevant to a returns question. Context recall is a retrieval metric, not either answer metric. Keep separate fields so one aggregate cannot conceal the actual failure mechanism.',
 'Calibrate a model judge against reviewed examples before trusting its scores. Compare case-level decisions, record disagreement and adjudicate errors such as negation or wrong applicability. Low temperature is not deterministic truth. Version the rubric, judge/model, context and prompt; never count failed or absent judge outputs as agreement.'
],['Both claim texts are present, but only one supplied label is supported.','The reviewed fraction is.5 without claiming an automated semantic inference.','Valid citation identity could still pass independently of this failed support case.'],
 'Implement reviewed-versus-judge disagreement reporting, including missing judge outputs as a separate count.', '''
def calibrate(rows):
    compared=[r for r in rows if r['judge'] is not None]
    return {'compared':len(compared),'missing':len(rows)-len(compared),
      'disagreements':[r['id'] for r in compared if r['reviewed']!=r['judge']]}
rows=[{'id':'negation','reviewed':False,'judge':True},{'id':'supported','reviewed':True,'judge':True},
      {'id':'unavailable','reviewed':False,'judge':None}]
assert calibrate(rows)=={'compared':2,'missing':1,'disagreements':['negation']}
print('practice: negation disagreement retained; missing judgment excluded from agreement denominator')
''',['Compare only pairs with an actual judge result.','Count missing results separately rather than converting None to False.','Retain IDs so a reviewer can inspect the disagreement and evidence.'],
 'If unavailable counts as a correct unsupported judgment, missing service output is being converted into evidence. A disagreement list is a calibration starting point; it does not automatically determine whether the judge or original reviewer was right.')
add(26,'Sessions 13 and 25: grounded outcomes and reviewed labels. Begin with four real fixture inputs before the supplied 120-case harness.',[
 'A concrete case has an actual input/state, expected behavior and a reason grounded in evidence. An ID alone exercises no behavior. The revised small example sends four requests through a deterministic policy fixture and compares returned outcomes; the appendix scales contract coverage to 120 actual scoped inputs.',
 'Family splits keep related variants together. Ten tenant variants of one prompt test isolation, but they are not ten unrelated semantic tasks. If near-duplicates span training/tuning and final evaluation, a candidate can appear strong through leakage. Assign split by family before tuning, retain dataset fingerprints and keep the final set unchanged.',
 'The coverage denominator includes every attempted case: completed, malformed, denied and unavailable. A timeout is an observed failed attempt, not permission to drop a row. Separate mechanical pass/fail, reviewed answer quality, latency and missing usage. Expected labels must stay outside the application request so the system cannot simply read the answer.'
],['Each small case includes an actual prompt, owner and expected decision.','The fixture executes policy_decision rather than copying expected fields.','The appended harness preserves all outcomes and labels its default fixture mode.'],
 'Add a new scope-denial case, prove it executes, then deliberately corrupt its expected decision to ensure the contract gate detects a failure.', '''
new_case={'id':'scope-variant','request':{'owner':'other','prompt':'returns window'},'expected':'deny'}
observed=policy_decision(new_case['request'])
assert observed==new_case['expected']
broken={**new_case,'expected':'answer'}
assert policy_decision(broken['request'])!=broken['expected']
assert 'expected' not in new_case['request']
print('practice: real scoped request executed; corrupted expectation detected; labels stayed outside request')
''',['Call policy_decision with only the request object.','Change the expected field, not the function output, to inject a failing test.','One deliberately failing comparison should be detected without changing the production fixture.'],
 'If the broken expectation still passes, expected labels may be leaking into the executor or the test is checking literals rather than behavior. The four-case example teaches the contract; run the provided 120-case suite before expanding it.')
add(27,'Session 26: concrete cases and an evaluation report. CI is an automated runner for these checks, not a model-quality oracle.',[
 'A release manifest identifies the exact candidate: code, prompt, model, dataset, parser, context/cache policy and judge/rubric revisions. Serialize stable fields and hash them so a change is detectable. A manifest with the same labels but different actual source files is insufficient; use real artifact digests in the integrated pipeline.',
 'Critical gates cannot be averaged away. One unauthorized effect blocks promotion even if 99 other cases pass. Distinguish a failure from missing evidence: both can block a required gate, but they call for different remediation. Preserve the failing case ID and release fingerprint with the report.',
 'A budgeted integration job is separate from an offline contract job. Run inexpensive fixture checks on every PR with no provider secrets. Credentialed candidate evaluation uses a trusted environment, a selected test revision, deadlines, request/spend caps and retained artifacts. The full workflow appendix shows the first job and explains the additional candidate boundary.'
],['The manifest fingerprint is 64 hex characters over stable JSON.','critical_failures=1 makes promote=False despite 99/100 quality passes.','Changing only a prompt/source/model version must change the candidate identity.'],
 'Add code/source revisions to the manifest and verify prompt, source and model changes each produce a different fingerprint.', '''
def release_id(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
base={**manifest,'code':'commit-fixture-1','source':'source-v1'}
original=release_id(base)
for field in ['prompt','model','source']:
    changed={**base,field:base[field]+'-changed'}
    assert release_id(changed)!=original
assert release_id(dict(reversed(list(base.items()))))==original
print('practice: prompt/model/source changes invalidate release identity; key order does not')
''',['Use sorted-key serialization rather than repr(dict).','Change one field at a time to isolate its effect.','Reordered dictionary insertion should not change semantic manifest identity.'],
 'If a version change leaves the fingerprint unchanged, that field is omitted from the manifest. If key insertion order changes it, serialization is unstable. This only proves manifest mechanics; the supplied CI chapter explains how it accompanies observed candidate results.')
add(28,'Sessions 3 and 20: concurrent work and branch provenance. A trace is a correlated record of stages, timing and outcomes.',[
 'A span describes one operation with run/span identity, start/end or duration, status and useful revision/usage fields. Include queue wait and retries so “the model was slow” can be distinguished from admission delay. A timeout remains in the trace even when no answer was produced.',
 'The critical path is the dependency path determining wall time. Sequential 20+800+100ms spans sum to 920ms in the baseline. Two 800ms branches starting together instead occupy 800ms, plus orchestration. Record actual timestamps or measured wall time; blindly summing every child span double-counts overlap.',
 'Payload minimization logs what is needed to diagnose behavior without copying private prompts/documents. Choose allowlisted keys and stable error categories, then test with a canary secret in input. Redaction after exporting is too late. Trace correlation and retention/access policy are part of the design, not reasons to log everything.'
],['The three baseline spans are sequential and total 920ms.','provider is marked timeout and retry_wait ends stopped_budget.','The allowlist excludes raw prompts, so the failure record need not disclose source text.'],
 'Compute wall time from overlapping span intervals and project trace data to an allowlist that removes a canary prompt.', '''
spans=[{'start':0,'end':800,'span':'a','prompt':'CANARY-PRIVATE'},
       {'start':0,'end':800,'span':'b','prompt':'CANARY-PRIVATE'},
       {'start':800,'end':900,'span':'merge','prompt':'CANARY-PRIVATE'}]
wall=max(s['end'] for s in spans)-min(s['start'] for s in spans)
assert wall==900 and sum(s['end']-s['start'] for s in spans)==1700
safe=[{k:s[k] for k in ['start','end','span']} for s in spans]
assert 'CANARY-PRIVATE' not in str(safe)
print('practice: parallel wall time900ms versus1700ms span sum; canary excluded before export')
''',['Use the earliest start and latest end for this single contiguous run.','Do not claim this simple envelope computes arbitrary distributed clock-skew corrections.','Build the exported object from allowed fields, then inspect the actual serialized payload.'],
 'If the report says 1700ms wall time, overlapping work was double-counted. If the canary remains in an exported object, the allowlist was applied to display only, not the payload leaving the service.')
add(29,'Session 6: percentiles and all-attempt cost. This lesson compares candidates under a fixed quality floor.',[
 'Accepted-output cost divides all workload spend by outputs meeting the reviewed quality bar. Failed or rejected generations still consume resources, and reviewer time can dominate a cheap API price. Keep monetary units and review-time units separate unless an explicit conversion assumption is stated. Zero accepted outputs means the ratio is undefined.',
 'Tail latency uses a named population and percentile rule. The 20 sorted fixture timings run 100–290ms; nearest-rank p95 selects the 19th value 280ms. Count timeouts separately or apply a stated censored-latency rule; do not quietly remove slow attempts. Warm/cold and cached/uncached measurements should be labeled.',
 'A Pareto comparison considers latency, cost and quality together. A faster/cheaper candidate that violates a mandatory quality floor is ineligible. Compare identical inputs, versions and measurement conditions before declaring an improvement. Choose a policy for eligible candidates and describe when changed review costs or workload would reverse it.'
],['Five of 20 fixture outputs are rejected, leaving 15 accepted.','All 20 cost units remain, giving 20/15≈1.3333 per accepted output.','Nearest-rank p95 is 280ms for all 20 recorded timings.'],
 'Compare a cheap low-quality candidate with an eligible baseline. Filter by quality before ranking useful-output cost; handle zero accepted outputs.', '''
def candidate(name,attempts,accepted,total_cost):
    return {'name':name,'quality':accepted/attempts if attempts else 0,
            'cost_per_accepted':total_cost/accepted if accepted else None}
baseline=candidate('baseline',10,9,9);cheap=candidate('cheap',10,5,2)
eligible=[c for c in [baseline,cheap] if c['quality']>=.9 and c['cost_per_accepted'] is not None]
assert min(eligible,key=lambda c:c['cost_per_accepted'])['name']=='baseline'
assert candidate('failed',10,0,2)['cost_per_accepted'] is None
print('practice: quality floor excluded cheap candidate; zero-acceptance cost remains undefined')
''',['Compute acceptance rate before choosing the cheapest option.','Keep failed-attempt cost in total_cost.','No eligible candidate is a valid revise/stop outcome, not a reason to lower the floor silently.'],
 'If cheap wins, optimization ignored the required acceptance floor. This fixture supplies quality labels and costs; the larger comparison must obtain them from the same reviewed workload and include actual retries/review effort.')
add(30,'Sessions 25–29: reviewed metrics, case coverage, manifests, gates, traces and useful-output economics.',[
 'An unreviewed output is not a quality pass or fail. Of 113 completed outputs,100 reviewed leaves 13 with unknown semantic acceptance. Keep the 7 unavailable attempts too. Report 94/100 reviewed passes as that reviewed population, not 94/120 or a claim that all 120 were judged.',
 'A category report separates normal requests, scope violations, duplicates, stale state, unsupported sources and outages. An aggregate can hide a critical family failure. Retain case IDs for the strongest counterexample and include missing usage/judge observations. Compute family metrics from actual results rather than generating green labels from configured expectations.',
 'The promotion decision references the exact release manifest and mandatory gates. Missing review, a critical failure or an unmet reliability target may block promotion. State the policy first; do not redefine it after seeing results. The capstone integrates the supplied harness with the student’s real pipeline, whereas this small practice isolates correct report arithmetic.'
],['113 completions plus 7 unavailable reconcile to 120 attempts.','100 reviewed is smaller than 113 completed, leaving 13 unreviewed.','One critical failure blocks the release independently of 94 reviewed passes.'],
 'Create a release summary that preserves missing populations, requires complete review, and enforces a predeclared 95% reviewed quality floor.', '''
def release_summary(r,quality_floor=.95):
    if not 0<=quality_floor<=1:raise ValueError('invalid quality floor')
    if r['completed']+r['unavailable']!=r['dataset_cases']:raise ValueError('attempt counts do not reconcile')
    if not 0<=r['quality_passed']<=r['quality_reviewed']<=r['completed']:raise ValueError('review counts inconsistent')
    unreviewed=r['completed']-r['quality_reviewed']
    quality=r['quality_passed']/r['quality_reviewed'] if r['quality_reviewed'] else None
    return {'unreviewed':unreviewed,'unavailable':r['unavailable'],
      'ready':r['critical_failures']==0 and r['unavailable']==0 and unreviewed==0 and quality is not None and quality>=quality_floor}
assert release_summary(report)=={'unreviewed':13,'unavailable':7,'ready':False}
complete={**report,'dataset_cases':100,'completed':100,'unavailable':0,'quality_reviewed':100,'critical_failures':0}
assert not release_summary({**complete,'quality_passed':94})['ready']
assert release_summary({**complete,'quality_passed':95})['ready']
assert not release_summary({**complete,'dataset_cases':0,'completed':0,'quality_reviewed':0,'quality_passed':0})['ready']
try:release_summary({**report,'quality_reviewed':114})
except ValueError:pass
else:raise AssertionError('impossible review count accepted')
print('practice:13 unreviewed and7 unavailable retained;95% quality floor enforced; impossible counts rejected')
''',['Reconcile completion plus unavailability with attempted cases.','Validate reviewed/pass counts before subtracting or dividing.','Treat unreviewed as unknown; never fill it with the observed pass rate.'],
 'If 113 completed outputs become 113 reviewed, the report invented labels. If reviewed exceeds completed, fail report validation instead of publishing an attractive percentage. The full capstone needs actual case-level observations behind these counts.')
add(31,'Basic HTTP and Docker concepts. The complete multi-file appendix introduces service DNS, readiness and persistence through a runnable local lab.',[
 'Runtime configuration supplies credentials and environment after image creation. A Docker image contains application code/dependencies; a secret baked into a layer remains extractable even if later deleted. Use runtime secret injection and keep the database on the private container network. Browser JavaScript must use an HTTP API rather than database credentials.',
 'Dependency readiness answers whether the application can serve its required work now. Query the actual datastore and return unavailable when it is down. A process-alive endpoint can be useful for liveness, but it is not the same claim. A browser cannot resolve the Docker service name db; the same-origin proxy can resolve backend on the internal network.',
 'Durable readback proves a write survived the relevant boundary. Save a synthetic record through the API, replace the backend container, read it again, then rehearse backup restore into an isolated database. A named volume preserves bytes but does not prove a backup restores correctly. Owner authorization is another application check, absent from the deliberately small unauthenticated network lab.'
],['The frontend exposes a browser URL and proxies to backend:8000.','The backend uses db internally and gets its secret at runtime.','The database has no public port and uses persistent storage; these are configuration intentions until exercised.'],
 'Model distinct readiness outcomes for a working and unavailable database, with a stable public error. Then follow the full container appendix for real HTTP/readback behavior.', '''
def dependency_readiness(query):
    try:query()
    except ConnectionError:return {'status':503,'body':{'status':'unavailable'}}
    return {'status':200,'body':{'status':'ready'}}
def unavailable():raise ConnectionError('synthetic secret-bearing database URL')
assert dependency_readiness(lambda:1)['status']==200
failed=dependency_readiness(unavailable)
assert failed['status']==503 and 'URL' not in str(failed)
print('practice: readiness reflects datastore outcome; public failure omits internal connection details')
''',['Invoke the dependency function; do not return a constant healthy status.','Map known dependency failure to a stable public category.','The miniature function tests error mapping, not a real database connection.'],
 'If the down case returns 200, the readiness claim is false. If internal connection details appear, the error mapper leaks configuration. Run the supplied Docker experiment afterward; its small fixture does not include tenant authentication, so implement that in your SaaS rather than claiming the lab proves it.')
add(32,'Session 31: containers, datastore readiness and persistent state. The cloud runbook is a later integration step, not required for this offline task.',[
 'Offered load is everything trying to enter; admitted load passed your limits; completed load actually finished. Keep rejected/failed work in the report. At 240 offered sockets and 12 measured safe sockets per instance,20 instances is an arithmetic lower bound before headroom. A maximum of 10 leaves insufficient configured capacity.',
 'A capacity envelope states workload, context/output sizes, provider/GPU limits and observed latency/quality at different concurrency levels. A platform concurrency setting only caps simultaneous admitted requests; it does not create memory or downstream quota. Step load gradually and stop at the predeclared cost/quality/latency boundary.',
 'Replica-independent state survives another instance serving the next request. Store sessions, checkpoints, quotas and jobs outside a process-global dictionary when they need cross-instance consistency. WebSockets eventually reconnect and may reach another replica. Recovery must authenticate ownership and restore bounded state without replaying uncertain writes.'
],['Ceiling division of 240 by 12 yields 20 required instances at the supplied capacity.','configured_max=10 cannot serve the full offered workload at that measured bound.','Admission or capacity must change; reporting only accepted sockets would hide rejection.'],
 'Implement bounded admission for ten 12-slot instances and report offered/admitted/rejected counts without relabeling rejection as success.', '''
def admit(offered,instances,safe_slots):
    if min(offered,instances,safe_slots)<0:raise ValueError('negative capacity')
    accepted=min(offered,instances*safe_slots)
    return {'offered':offered,'admitted':accepted,'rejected':offered-accepted}
assert admit(240,10,12)=={'offered':240,'admitted':120,'rejected':120}
assert admit(0,10,12)['rejected']==0
assert admit(10,0,12)['admitted']==0
print('practice:240 offered,120 admitted,120 rejected; zero replicas admit none')
''',['Calculate finite capacity before admission.','Maintain offered = admitted + rejected.','Admitted is not completed; completion requires another observed counter.'],
 'If the report says 240 users supported because offered=240, it confuses demand with capacity. The 12-slot figure is supplied fixture data; actual cloud measurements and reconnect tests are separate runbook tasks.')
add(33,'Session 32: capacity envelopes. GiB arithmetic below is illustrative and does not describe any particular model or GPU.',[
 'Resident memory includes weights and serving runtime before user context grows. Quantization changes the model artifact and memory footprint but can also change answer quality. Record model/license/revision, quantization, tokenizer, runtime and hardware so another operator can reproduce a comparison.',
 'KV cache is attention state accumulated for input/output context during inference. More tokens and simultaneous requests generally require more memory, but the actual layout depends on model architecture, runtime, batching and cache management. Reserve runtime/headroom before estimating request slots; measured memory can differ from a worksheet.',
 'Artifact-specific evaluation compares the exact deployed model/runtime on identical labeled tasks. Ollama local streaming and a vLLM serving endpoint have different operational contracts even if a chat interface looks similar. Measure cold load, token lengths, throughput, p95, errors and quality. Fewer billed API calls do not make local GPU power/hardware/operations free.'
],['Subtract 14 weights,3 runtime and 2 headroom from 24 to leave 5 GiB.','At the supplied 1 GiB/request assumption that means five illustrative slots.','The result explicitly says real concurrency still requires measurement.'],
 'Add a context-sensitive memory worksheet: double the supplied per-request KV assumption, test exhausted memory and reject an impossible fixed-memory configuration.', '''
def estimated_slots(total,weights,runtime,safety,kv):
    if kv<=0 or min(total,weights,runtime,safety)<0:raise ValueError('invalid memory budget')
    remaining=total-weights-runtime-safety
    if remaining<0:raise ValueError('fixed allocations exceed device')
    return int(remaining//kv)
assert estimated_slots(24,14,3,2,1)==5
assert estimated_slots(24,14,3,2,2)==2
assert estimated_slots(19,14,3,2,1)==0
try:estimated_slots(18,14,3,2,1)
except ValueError:pass
else:raise AssertionError('overcommitted fixed memory accepted')
print('practice: doubling assumed KV reduces illustrative slots5→2; overcommit rejected')
''',['Subtract fixed allocations before dividing by per-request KV.','Round down: half a request slot is unusable.','A zero result is allowed; a negative remaining budget indicates an invalid deployment plan.'],
 'If doubled context costs leave five slots, KV growth was not included. These are explicit assumptions, not an actual context-memory model; benchmark the selected artifact before setting admission limits.')
add(34,'Sessions 3,22 and 32: concurrency, idempotency and cross-replica state. A token bucket permits a finite burst plus timed refill.',[
 'Admission control checks resources before expensive provider work. A request-rate bucket is distinct from simultaneous worker capacity, a token reservation and a monthly monetary budget. Two cheap short calls and two long generations can have the same request count but very different cost. Keep these limits explicit and report rejection.',
 'An atomic shared quota means all workers update the same allowance as one indivisible operation. Separate local buckets each starting with two tokens can admit four aggregate requests. A durable conditional update or suitable shared-store primitive can enforce a global bound. Choosing shared state is not enough if check and decrement are separate races.',
 'A fallback contract preserves authorization, permitted data location, output shape, deadline and evaluated quality. A failed quota store should follow an explicit fail-closed or bounded degraded policy; unlimited fallback can destroy the budget. Reserve estimated usage before work and reconcile actual usage afterward without double-refunding retried operation keys.'
],['Two requests at time 0 consume the initial burst of two tokens.','The third is rejected until refill supplies one token at time 1.','This baseline bucket is process-local, so it cannot establish a distributed bound.'],
 'Demonstrate shared atomic request reservations with two SQLite connections using one conditional UPDATE. Prove only two aggregate claims succeed.', '''
import sqlite3,tempfile
from pathlib import Path
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'quota.sqlite';first=sqlite3.connect(path);second=sqlite3.connect(path)
    first.execute('CREATE TABLE quota(owner TEXT PRIMARY KEY,remaining INTEGER)')
    with first:first.execute('INSERT INTO quota VALUES(?,?)',('acme',2))
    def reserve(db):
        with db:return db.execute('UPDATE quota SET remaining=remaining-1 WHERE owner=? AND remaining>=1',('acme',)).rowcount==1
    outcomes=[reserve(first),reserve(second),reserve(first),reserve(second)]
    assert outcomes==[True,True,False,False]
    assert first.execute('SELECT remaining FROM quota').fetchone()[0]==0
    first.close();second.close()
print('practice: two connections shared one atomic quota; two aggregate admissions, two rejections')
''',['Use one file and two connections rather than two separate databases.','Make sufficient-balance check and decrement one conditional statement.','This serial two-connection test establishes shared-update behavior, not a distributed load benchmark.'],
 'If all four claims succeed, the connections are not sharing the same quota or the predicate is absent. Add operation-key reservation/refund and real multi-worker failure tests in the integration project; this exercise intentionally isolates atomic admission.')
add(35,'Sessions 29,33 and 34: accepted-output comparison, local model constraints and quotas.',[
 'Route selection maps a request to an allowed execution path. The baseline uses supplied routine/complex labels, so it tests routing logic rather than a difficulty classifier. Unknown tasks go to review. To claim intelligent routing quality, independently label difficulty and compare route choices/output acceptance on held-out requests.',
 'A residency boundary specifies where approved data may be processed. A premium cloud endpoint is not allowed for local-only material merely because a local model failed or ran out of context. Check data policy before selecting an adapter or cache, and keep the same owner/source revisions across paths.',
 'Comparable workloads keep inputs, relevance labels, acceptance standards and measurement conditions fixed across all-local, all-premium and hybrid candidates. Include retries, fallback calls and review effort. A hybrid system can reduce one cost while raising tail latency or errors; a selected route is not itself a measured advantage.'
],['routine uses local, complex uses premium and unknown requires review.','A zero budget rejects even a routine request.','The baseline does not yet enforce data residency, exposing the extension needed next.'],
 'Add local-only residency and remaining-deadline gates before route selection. Verify no premium route is returned for restricted data.', '''
def safe_route(request,budget,remaining_ms,cloud_allowed):
    if budget<=0:return 'budget_exhausted'
    if remaining_ms<=0:return 'deadline_exhausted'
    if request['kind']=='complex' and not cloud_allowed:return 'review'
    return route(request,budget)
complex_request={'kind':'complex','owner':'acme'}
assert safe_route(complex_request,10,100,False)=='review'
assert safe_route(complex_request,10,100,True)=='premium'
assert safe_route(complex_request,10,0,True)=='deadline_exhausted'
assert safe_route(complex_request,0,100,True)=='budget_exhausted'
print('practice: residency/deadline/budget checked before premium routing')
''',['Place data-location checks before the premium adapter call.','Use a visible unavailable/review outcome when no authorized route fits.','Changing the route to review is a policy test, not proof that review work is staffed or fast.'],
 'If restricted input reaches premium, fallback has expanded data access. If an expired deadline still calls a model, admission is too late. The capstone must measure actual route quality and cost rather than use these fixture labels as a classifier.')
add(36,'The final release assembles the five module projects. Use their actual evidence; the local practice below only validates a release-packet checker.',[
 'Release evidence is an inspectable observation tied to the candidate: dataset/manifest IDs, accepted quality, all-attempt spend, latency population, load envelope, owner-isolation results, restart/restore and operational ownership. A checkbox is a claim; the packet needs underlying reports and a reproducible procedure.',
 'An unmet gate can be failed or untested. Represent missing evidence explicitly and refuse to turn a nonempty string like “not tested” into True. Critical gates cannot be overridden by an attractive average or a deployment badge. Give each blocker an owner, reason and next observation; do not label an unknown result as passed.',
 'A scoped readiness claim describes exactly the tested revision, workload and operational conditions. “A synthetic single-tenant prototype passed offline contracts” differs from “thousands of concurrent users.” A fresh operator should reproduce setup, inspect reports, recover state and understand the stop budget without relying on the developer’s memory.'
],['Six supplied gates are true but the load report gate is false.','missing identifies that exact evidence gap.','all(gates.values()) is false, so the prototype cannot make its desired scale claim.'],
 'Implement a three-state release-packet validator. Only literal passed states may release; failed, untested and unknown values must block.', '''
def inspect_packet(packet,required):
    valid={'passed','failed','untested'}
    if any(value not in valid for value in packet.values()):raise ValueError('invalid evidence status')
    return [name for name in required if packet.get(name)!='passed']
required=['quality','load','restore']
packet={'quality':'passed','load':'untested','restore':'passed'}
assert inspect_packet(packet,required)==['load']
assert inspect_packet({'quality':'passed'},required)==['load','restore']
try:inspect_packet({'quality':'yes'},required)
except ValueError:pass
else:raise AssertionError('ambiguous evidence accepted')
print('practice: untested/missing gates block release; ambiguous statuses rejected')
''',['Use an explicit allowed-state vocabulary rather than truthiness.','Check every required field, including absent ones.','The returned blocker list should name the missing observation a fresh operator must obtain.'],
 'If “untested” passes, Python string truthiness has been mistaken for evidence. Passing this checker validates the packet format only; attach and inspect the real module reports before making a release claim.')
assert set(GUIDES)==set(range(1,37))
