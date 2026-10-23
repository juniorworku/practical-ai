"""Student review repairs: taught runtime mechanisms and project-boundary practice.
The core examples are extracted from the same published capstone functions.
"""
import ast
from pathlib import Path
import subprocess
import sys
import tempfile
from progression import refresh

ROOT=Path(__file__).resolve().parents[1]
CASES=Path(__file__).with_name('student_depth_cases')
CAPS=ROOT/'backend/academy/content/capstones'
STUDIOS={}

def function(slug,file,name):
    source=(CAPS/slug/file).read_text()
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    return ast.get_source_segment(source,node)+'\n'

def add(slug,key,title,prerequisite,steps,code,task,patch,hints,diagnosis,question,right,wrong1,wrong2):
    assert len(steps)==4 and len(hints)==3
    STUDIOS[slug,key]=dict(title=title,prerequisite=prerequisite,steps=steps,code=code,
                         task=task,patch=patch,hints=hints,diagnosis=diagnosis,
                         question=question,right=right,wrongs=[wrong1,wrong2])

add('ai-agent-bootcamp','05','From retry arithmetic to an actual asynchronous deadline',
'Sessions 2 and 4: run a Python file, inspect exceptions and distinguish a draft from success. This studio introduces async syntax explicitly; no asynchronous SDK is required.',[
('Read a coroutine as a paused operation', 'An async def function returns a coroutine. Calling it alone does not run its body. await runs that operation and lets the event loop schedule other waiting work. asyncio.run creates the loop for this one-file script. Here transport is a function supplied by the caller: a real HTTP adapter and this fixture can expose the same awaitable interface. A synchronous blocking HTTP client inside transport would prevent timely cancellation; choose an asynchronous client for real I/O.'),
('Classify before deciding to retry', 'Transient and Permanent are separate exception types. Only Transient is caught inside the retry loop. A permanent credential failure therefore escapes immediately; it cannot turn into an invented draft or another paid attempt. The function returns only the actual transport result. Attempts bound calls, while the exponential delay bounds repeated pressure. Never apply this read-only policy to a write whose remote result is uncertain.'),
('Put the deadline around the entire operation', 'asyncio.timeout surrounds both await transport() and await sleep(). Its budget includes waiting and backoff, rather than restarting for every attempt. When the budget expires, cancellation reaches the blocked coroutine; its finally block runs before TimeoutError reaches the caller. Events record that execution entered and cleanup happened. The test does not assert an exact 20ms observation, because scheduler delays vary; it asserts the required cleanup state.'),
('Keep tests and performance claims separate', 'Predict two calls for the transient-then-success case, an escaping Permanent for bad credentials, and an observed TimeoutError plus cleanup for a transport that never completes. The events avoid depending on a guessed sleep to prove that work started. These tests exercise actual event-loop cancellation, but no provider, network latency or model quality. The capstone timeout mode is still explicit failure injection, not a measured provider timeout.')],
(CASES/'bootcamp_deadline.py').read_text(),
'Add a transport that always raises Transient. Permit exactly two attempts and prove the second failure escapes rather than returning a draft. Retain the cleanup and permanent-error tests.',
'''async def exhausted_check():
    calls=0
    async def unavailable():
        nonlocal calls
        calls+=1
        raise Transient('still unavailable')
    try:
        await generate(unavailable,attempts=2)
    except Transient:
        pass
    else:
        raise AssertionError('exhaustion became success')
    assert calls==2
asyncio.run(exhausted_check())
print('variation: exactly 2 calls; exhausted failure retained')''',
['Count calls in the transport, not in the assertion.','Catch the final Transient outside generate; keep the allowed attempt count at two.','Assert both the count and the exception path; a printed error alone does not prove bounded work.'],
'An unawaited-coroutine warning means the function was called without await or asyncio.run. More than two calls means the bound is wrong. A TimeoutError in the exhaustion test means your deliberately tiny deadline, rather than attempt exhaustion, ended it; keep the generous .2-second fixture budget. Real client connection/read/write limits must also respect the overall budget.',
'A transient read fails twice with attempts=2. What is the correct result?',
('Two calls and a propagated failure; no successful draft.','The fixed attempt bound terminates the retry path, and failure remains visible.'),
('Return an empty successful draft after the second failure.','That hides the dependency failure and destroys the distinction between no evidence and failed generation.'),
('Reset the overall deadline and keep trying.','That violates both the call bound and the user-visible total budget.'))

add('ai-agent-bootcamp','14','Prove approval rollback before wiring the HTTP route',
'Session 12 supplies exact-payload approval and a scoped operation key; session 14 introduces transactions. SQL placeholders, uniqueness and connection closure are explained here.',[
('Model two records with one invariant', 'drafts stores the reviewable text and state. effects stores the local outbox receipt under a primary key. The invariant is that an approved draft has exactly one matching local effect. A unique key blocks duplicate receipts, but does not by itself keep the draft status consistent. This studio uses one connection to make transaction behavior easy to inspect; the final PostgreSQL implementation additionally locks the selected owner-scoped row.'),
('Separate committed setup from the operation', 'The initial draft is committed before approve runs. Otherwise an injected exception could roll back fixture creation and make a test pass for the wrong reason. with db commits its block on success and rolls it back on an escaping exception. It does not close the SQLite connection: closing handles that separately. SQL ? placeholders bind values rather than interpolating reviewed text into executable SQL.'),
('Inject failure between the two writes', 'approve inserts the receipt, then fail=True raises before updating the draft. The exception escapes the transaction block, rolling back the inserted receipt. Predict zero effects and needs_review. A later normal call commits both writes. Replaying the same ID uses INSERT OR IGNORE and returns the same receipt. This demonstrates local atomicity and replay, not arbitrary distributed concurrency or external delivery.'),
('Carry the invariant into PostgreSQL', 'In the final app, trusted server identity supplies owner and reviewer role. SELECT FOR UPDATE must execute inside transaction.atomic and include the owner predicate. Compare the submitted version and digest to the locked payload before creating the receipt. A database rollback can remove a local outbox row; it cannot unsend a remote message. An uncertain remote result requires reconciliation, not a second unqualified send.')],
(CASES/'bootcamp_approval.py').read_text(),
'Create a new committed draft d2. Try approving it as another owner and with changed reviewed text. Prove both attempts leave its state needs_review and produce no effect.',
'''with closing(sqlite3.connect(':memory:')) as db:
    db.executescript('CREATE TABLE drafts(id TEXT PRIMARY KEY,owner TEXT,text TEXT,state TEXT);CREATE TABLE effects(id TEXT PRIMARY KEY,text TEXT);')
    db.execute('INSERT INTO drafts VALUES (?,?,?,?)',('d2','one','unopened only','needs_review'));db.commit()
    for owner,text in [('two','unopened only'),('one','opened allowed')]:
        try:approve(db,owner,'d2',text)
        except (PermissionError,ValueError):pass
        else:raise AssertionError('unreviewed payload accepted')
    assert db.execute('SELECT count(*) FROM effects').fetchone()[0]==0
    assert db.execute('SELECT state FROM drafts').fetchone()[0]=='needs_review'
print('variation: wrong owner and changed text caused no effect')''',
['Commit d2 before injecting the failures.','Use the same d2 ID for both negative attempts.','Read both tables after failure; catching an exception alone is not the invariant.'],
'If d2 disappears, setup was not committed before the tested transaction. If an effect remains, a write escaped the transaction. This miniature function assumes its owner argument came from trusted identity; HTTP reviewer authorization is in the complete capstone, not simulated by accepting an arbitrary role in JSON.',
'An exception occurs after inserting a local receipt but before updating the draft, inside one transaction. What should readback show?',
('No receipt and an unchanged needs_review draft.','The transaction rolls back both the attempted local effect and its status change.'),
('A receipt is acceptable because the exception was logged.','Logging does not repair split state; the receipt must roll back with this transaction.'),
('A database rollback also cancels any message already sent remotely.','The database controls its own writes, not another service’s side effects.'))

workshop_code=(CAPS/'ai-workshops/core.py').read_text()+'''
text='Supplier: Studio\\nQuantity: 2\\nUnit price: 10.00\\nCurrency: USD'
result=process(text,'fixture',[])
assert result['record']['total']=='20.00'
assert result['field_evidence']['quantity'][0]['line']==2
conflict=process(text+'\\nQuantity: 9','fixture',[])
assert conflict['status']=='needs_correction'
assert [s['value'] for s in conflict['field_evidence']['quantity']]==['2','9']
print('USD20.00 traced to input lines; conflicting quantity retained for correction')
'''
add('ai-workshops','02','Trace normalized fields back to the submitted document',
'Studio 1 session 1: required fields, unknown values and evidence spans. The parser is a deterministic baseline over a four-line synthetic request.',[
('Keep source evidence before normalizing', 'enumerate(..., 1) assigns human-readable line numbers. split(":", 1) separates only the first colon, so a supplier name containing a colon stays intact. Each field retains the complete raw line and the trimmed value. The normalized record is useful for computation; the source span is needed to inspect whether that value was actually present. A line number is meaningful only alongside this exact submitted text, retained in the final API draft.'),
('Treat duplicates as ambiguity, not last-write wins', 'Two Quantity lines are not permission to choose the last one. evidence stores both spans; fields keeps the first value only for diagnostics, and issues forces needs_correction. No record is emitted from that branch. Even two identical repeated values are flagged, because this fixed schema permits one occurrence. A schema that supports repeated line items needs a different declared contract and evaluation cases.'),
('Validate before doing arithmetic', 'The schema requires exactly Supplier, Quantity, Unit price and Currency. Quantity must be an ASCII integer from 1 to 1000. Unit price must have exactly two decimal places and supported currency is USD. Decimal constructs an exact base-ten amount from the validated string; float can introduce binary rounding error. Missing price, NaN and negative quantities route to correction rather than becoming zero, guesses or a purchase order.'),
('Trace the success and correction branches', 'For Quantity 2 and Unit price 10.00, predict total 20.00 and line 2 as the quantity source. Add Quantity 9 on line 5: both spans survive, but text is null and status needs_correction. Confirmation is a later workflow step, not an extraction accuracy claim. In the final capstone, field_evidence and original input are saved with the same draft; a local reviewer checks them before approval. No OCR, model call or real order occurs.')],
workshop_code,
'Change the supplier to Studio: East, add a duplicate Unit price line, and verify supplier punctuation survives while both price spans remain visible and no reviewable record is produced.',
'''changed=text.replace('Supplier: Studio','Supplier: Studio: East')+'\\nUnit price: 11.00'
row=process(changed,'fixture',[])
assert row['field_evidence']['supplier'][0]['value']=='Studio: East'
assert [s['line'] for s in row['field_evidence']['unit price']]==[3,5]
assert row['status']=='needs_correction' and row['text'] is None and 'record' not in row
print('variation: supplier colon preserved; duplicate prices require correction')''',
['Split each line at only the first colon.','Inspect the evidence list, not just the last parsed value.','Assert no record is returned on the duplicate branch.'],
'If Studio: East becomes East, the split discarded source content. If only one price span survives, storage overwrote evidence. If needs_review appears with duplicate prices, the validation branch was bypassed. This proves line-level provenance for the exact fixture, not semantic extraction accuracy on arbitrary PDFs.',
'The request contains Unit price: 10.00 and later Unit price: 11.00. What should extraction return?',
('needs_correction with both source spans and no computed record.','The schema allows one price; retaining the conflict lets the student or reviewer resolve it explicitly.'),
('Use 11.00 because the last value is newest.','Position in this document is not a revision or authority rule.'),
('Average the prices to avoid interrupting the workflow.','That invents a value the source never supplied.'))

add('ai-workshops','11','Count missing predictions in a per-class routing report',
'Sessions 10–11: a fixed taxonomy, uncertainty route, confusion matrix and per-class recall. A dictionary maps stable case IDs to the actual predictions.',[
('Define the unit before calculating', 'One row is one attempted case with one independently assigned gold route. Stable IDs join the predictions to that case table. Duplicate case IDs are invalid; extra prediction IDs are invalid because they would change the population. This fixture uses billing and technical, with review as an allowed fallback. Missing predictions are retained, not silently removed by iterating only returned results.'),
('Construct counts from actual decisions', 'The matrix key is (gold, prediction). Every attempted case increments one cell. A missing result becomes review and also increments the separate missing count, preserving the difference between an intentional uncertainty route and a failed response. An unknown label is a schema error rather than an invented new category. In a real service, capture whether the missing response was a timeout, parsing failure or unavailable dependency.'),
('Calculate recall using the gold population', 'For billing, one correct prediction out of two gold billing rows gives .5 recall; the misrouted billing row remains in the denominator. Technical also has one correct out of two, even though one prediction is absent. A class with no gold cases has undefined recall, represented by None, rather than a perfect 1.0. This small report is not a calibrated confidence estimate or an estimate of real customer traffic.'),
('Compare changes without hiding regressions', 'The result is 2 correct of 4 attempted, with one missing prediction. Before changing a rule, freeze this table and add a separate development case. Compare each class as well as total correct. Routing every uncertain case to review may reduce false automatic routes while increasing human workload. Record both consequences; a lower automated error count alone does not establish a better operational system.')],
(CASES/'workshops_metrics.py').read_text(),
'Evaluate a candidate that routes every case to billing. Prove overall correctness stays 2/4 while technical recall becomes zero; then verify an unexpected prediction ID is rejected.',
'''candidate=report(cases,{row['id']:'billing' for row in cases})
assert candidate['correct']==2 and candidate['attempted']==4
assert candidate['recall']=={'billing':1.0,'technical':0.0}
try:report(cases,{'unknown':'billing'})
except ValueError:pass
else:raise AssertionError('unmatched prediction counted')
print('variation: unchanged 2/4 aggregate hides zero technical recall')''',
['Create predictions from each existing case ID.','Use gold technical rows for the technical denominator.','Compare both per-class values and total correct, then test an unmatched ID separately.'],
'If the all-billing candidate improves total correct, cases or labels changed. If technical recall is undefined, you incorrectly used predicted rather than gold population. A missing output and an explicit review decision share the fallback cell here but retain a separate missing counter.',
'An all-billing candidate still gets 2 of 4 cases correct. Is that sufficient to keep it?',
('No: technical recall fell to zero despite the unchanged aggregate.','Per-class outcomes expose a regression hidden by total accuracy.'),
('Yes: equal overall accuracy means equivalent behavior.','The same total can conceal complete failure on one class.'),
('Drop technical cases so the score matches the intended route.','Removing a failed population changes the question and hides the defect.'))

engineering_code='import re\n'+function('ai-engineering-12-week','core.py','select_context')+'''
text='Refunds within 14 days. '+'Policy detail. '*23+'Opened items are excluded.'
document={'id':'one:policy','revision':'r1','text':text}
selected,used=select_context('refunds',[document])
assert len(text)>350 and selected[0][1].endswith('Opened items are excluded.')
assert used==len(text)
print('rule and exception preserved together; budget counts complete evidence units')
'''
add('ai-engineering-12-week','08','Carry rule-and-exception units into the actual retriever',
'Sessions 7–8: immutable document identities, source locators and chunk budgets. Inputs here are already owner-filtered; the final HTTP adapter performs that filter in SQL.',[
('Choose a boundary that has an explicit meaning', 'This corpus treats a blank-line-separated paragraph as one reviewed evidence unit. Splitting every 350 characters can leave a refund rule in one chunk and its exclusion in the next. The query may match only the rule, silently dropping the exclusion. Paragraphs are not universally semantic: the source author or ingestion review must ensure dependent conditions stay together. The example deliberately makes its exception appear beyond the old 350-character cut.'),
('Rank without losing provenance', 'Each candidate retains document ID, paragraph position and immutable revision alongside its text. A regex produces lowercase word sets; overlap supplies a transparent lexical score. Stable ID tie-breaking makes repeated fixture runs reproducible. This is not an embedding model or an applicability classifier. Owner filtering must happen before private text reaches this function; adding a scope check after answer construction is too late.'),
('Refuse a split you have not taught the system to make safely', 'The 700-character allowance is an explicit evidence budget, not a token limit. A relevant paragraph larger than the allowance raises a reviewed-split error. The final service translates that into needs_correction with no answer or citations. It conservatively refuses even if another smaller passage fits, because silently dropping a relevant exception could mislead. Review the unit or change a measured model-specific budget; do not slice its first 700 characters to make the check pass.'),
('Keep context selection distinct from answer quality', 'Whole units are admitted until the character allowance is exhausted. The return value includes selected IDs/text/revisions and actual selected character count. This protects the chosen boundary but cannot prove the selected policy applies to the user. The final extractive fixture labels its model and leaves token usage unknown. Its candidate cache key serializes query, pipeline, route and evidence revisions canonically; no cache is implemented and cache_hit remains false.')],
engineering_code,
'Add a 701-plus-character relevant paragraph and require a reviewed-split failure. Add a separate irrelevant oversized paragraph and prove it does not displace the supported evidence.',
'''oversized={'id':'one:large','revision':'r1','text':'Refunds '+'x'*700}
try:select_context('refunds',[oversized])
except ValueError:pass
else:raise AssertionError('relevant evidence silently truncated')
irrelevant={**oversized,'text':'wallpaper '+'x'*700}
again,count=select_context('refunds',[document,irrelevant])
assert again==selected and count==used
print('variation: oversized relevant unit refused; irrelevant unit excluded before packing')''',
['Apply relevance before testing a unit against the context budget.','A relevant oversized unit must fail, rather than return a truncated success.','Compare selected IDs and exact text; a passing character count alone can hide lost exceptions.'],
'If the exception disappears, inspect the splitting boundary before tuning ranking. If an irrelevant large paragraph triggers a split failure, budget validation occurred before relevance filtering. This fixture assumes reviewed paragraphs; arbitrary source documents need parser/locator review and separate answer-support evaluation.',
'A relevant paragraph is larger than the evidence budget and contains a nearby exclusion. What should this implementation do?',
('Request a reviewed split and return no answer yet.','It has no safe automatic split rule for the dependent condition.'),
('Keep the first 700 characters and cite the document.','A valid ID cannot repair an omitted exception.'),
('Call the 700-character limit a measured token count.','Character units are not a model-specific tokenizer observation.'))

add('ai-engineering-12-week','29','Compute useful-output economics from the actual attempted population',
'Sessions 25–28: versioned cases, independent acceptance decisions and trace observations. Decimal is introduced here for exact supplied dollar amounts.',[
('Keep one record per attempted request', 'Each record has a unique ID, measured end-to-end elapsed time, reviewed accepted boolean and cost observation. A request that retries then fails still consumes elapsed time and cost. Aggregate its attempts once into this request record; do not count the same retry again as another request. A successful HTTP response is not an accepted answer. Acceptance comes from the declared mechanical gates plus separately recorded semantic review.'),
('Preserve unknown rather than substitute zero', 'Decimal(".01") represents an exact decimal input; building it from a binary float can preserve unwanted rounding. Summation retains all known costs, including failed work. None means unavailable cost, not free work. If any request cost is unknown, cost_per_accepted is None while known_cost and unknown_cost_rows remain visible. If nothing is accepted, the ratio is also undefined, rather than infinity or zero being silently promoted as a measured number.'),
('Label the latency population and quantile rule', 'Sort elapsed times for all attempts, including failed outcomes. Nearest-rank p95 uses ceil(.95*n)-1 as the zero-based index. For 20ms success and 900ms failed work, p95 is 900ms. Two observations are far too few to estimate production tails, but they expose the accounting error of dropping failures. A completed-only latency report can be useful if separately labeled alongside reliability and the all-attempt denominator.'),
('Use quality floors before comparing cheaper routes', 'The supplied success costs .01 and failed work costs .03, yielding .04 per accepted result, not .01. Compare candidates on identical labeled cases and context allocations. A cheaper route that violates an ownership invariant or fails the accepted-quality floor cannot be selected solely by lower average cost. This arithmetic does not estimate GPU throughput, provider prices or future traffic; replace supplied observations with actual versioned measurements.')],
(CASES/'engineering_economics.py').read_text(),
'Add a zero-acceptance run and a run with one unknown failed-request cost. Verify neither reports a numeric cost per accepted result, and reject a NaN elapsed observation.',
'''assert summarize([{**rows[0],'accepted':False}])['cost_per_accepted_usd'] is None
partial=summarize([rows[0],{**rows[1],'cost_usd':None}])
assert partial['known_cost_usd']==Decimal('.01') and partial['unknown_cost_rows']==1
assert partial['cost_per_accepted_usd'] is None
try:summarize([{**rows[0],'elapsed_ms':float('nan')}])
except ValueError:pass
else:raise AssertionError('nonfinite time accepted')
print('variation: zero acceptance and partial cost stay undefined; NaN time rejected')''',
['Keep the failed request in rows even when its cost is unknown.','Separate the known subtotal from a complete total.','NaN comparisons are unusual: require a finite nonnegative elapsed value, not merely elapsed < 0.'],
'If partial cost yields .01 per accepted result, unknown work was treated as zero. If a zero-acceptance run returns zero cost per accepted result, an undefined ratio was hidden. The tiny supplied dataset checks accounting; it is not a production latency benchmark or current pricing source.',
'One accepted result costs .01, and a failed request costs .03. What is cost per accepted result?',
('USD .04, counting all attempted work.','The denominator is accepted results, while the numerator includes failed work.'),
('USD .01 because only the accepted request counts.','That discards the cost spent producing no accepted result.'),
('USD .02 because there were two requests.','That is cost per attempted request, a different metric.'))

accelerator_code=function('genai-accelerator','agent.py','valid_evidence')+'''
reply={'mode':'lexical_fixture','answer':'14 days','citations':['doc:0'],'context_chars':7,'usage_tokens':None}
assert valid_evidence(reply,'doc')
assert not valid_evidence({**reply,'answer':None},'doc')
assert valid_evidence({**reply,'answer':None,'citations':[],'context_chars':0},'doc')
print('supported envelope and empty success accepted; contradictory answer/citations rejected')
'''
add('genai-accelerator','lesson-13','Validate relationships between fields, not only field types',
'Lessons 9 and 12: a provider adapter result, exact request shape, Python types and exceptions. This response contract is the one used later by the independent ingestion/agent capstone.',[
('Write the complete transport contract', 'The fixture response has exactly mode, answer, citations, context_chars and usage_tokens. The mode is lexical_fixture and usage is None because no model is called. Reject extra fields and non-object JSON before accessing .get or indexing. A list can be valid JSON but not a valid application response. This is intentionally a narrow versioned fixture schema; a provider with a different envelope needs an explicit adapter, not a permissive fallback.'),
('Validate identities and scalar types', 'A citation begins with the exact trusted document ID plus a colon, followed by an ASCII numeric chunk position. The trusted ID is supplied by the host, not taken from the response. Repeated IDs are rejected so they cannot inflate evidence counts. Python bool is a subclass of int, so type(size) is int deliberately excludes True as a character count. Unknown provider usage remains unavailable; the fixture does not invent token counts.'),
('Teach the success and empty-result invariants', 'A supported result needs nonblank text, nonempty unique citations and positive bounded evidence size. The API joins whole chunks with one space: answer length must equal context_chars plus one separator per additional chunk. An empty successful search has answer=None, citations=[] and context_chars=0. Mixing null text with citations or text with no citations is invalid_evidence, not a legitimate abstention. A transport or JSON failure is service_unavailable; it must not become an empty search.'),
('Stop at the validation boundary', 'A known citation and internally consistent sizes do not prove the prose is supported. A fabricated seven-character answer could still pass these mechanical checks; semantic support needs its own comparison to the actual source. Later, the agent stores only validated evidence, distinguishes no search from an empty search, and finishes within its step budget. A wrong envelope is rejected before the finish action can consume it.')],
accelerator_code,
'Test a duplicated citation, another document’s citation, a boolean character count, and an answer with no citations. Preserve the valid empty-search case as a separate success.',
'''for bad in [
    {**reply,'citations':['doc:0','doc:0']},
    {**reply,'citations':['other:0']},
    {**reply,'context_chars':True},
    {**reply,'citations':[]}]:
    assert not valid_evidence(bad,'doc')
empty={**reply,'answer':None,'citations':[],'context_chars':0}
assert valid_evidence(empty,'doc')
print('variation: four malformed envelopes rejected; empty success preserved')''',
['Check exact top-level shape before reading nested fields.','A repeated ID is not additional support, and True is not an observed size.','Test empty success separately; do not reject every empty retrieval as a service outage.'],
'An AttributeError on a list response means shape validation ran too late. Completion with null text and citations means cross-field validation is incomplete. Rejecting the legitimate empty fixture confuses lack of evidence with a failed dependency. None of these mechanical checks establishes arbitrary prose entailment.',
'The API returns answer=None with citations=["doc:0"]. How should the later agent classify it?',
('invalid_evidence; stop before completion.','The envelope contradicts its own supported/empty-result invariants.'),
('completed because the citation is known.','Citation membership cannot supply missing answer text.'),
('abstained because the answer is null.','A legitimate empty search must also have no citations and zero selected context.'))

add('genai-accelerator','lesson-25','Recover the commit-to-queue gap without inventing completion',
'Lessons 15 and 23–25: accepted versus ready state, relational uniqueness and transaction commit. The small fixture uses SQLite to inspect state; the complete operational case uses PostgreSQL, Redis and Celery.',[
('Identify the two systems and the gap', 'The database owns accepted jobs, while the queue schedules work. accept commits the row before calling enqueue. If the broker is unavailable afterward, the committed row survives. Returning retry_required with its ID tells the caller what happened; returning ready would fabricate work, and pretending nothing was stored could create duplicate uploads. A single database transaction cannot atomically include an arbitrary broker call.'),
('Make identity conflicts observable', 'The same scoped identity must always refer to the same input. Look up the stored text before INSERT OR IGNORE. Reusing d1 with changed content raises an identity conflict instead of silently leaving old bytes under a supposedly new submission. The complete API derives the identity from owner and digest rather than trusting a client label. A retry should target the existing accepted ID, not manufacture a fresh record.'),
('Commit transformed state with its ready marker', 'consume reads the accepted row, inserts its transformed chunk and updates state to ready in the same transaction. An exception rolls both writes back. A duplicate delivery sees ready and returns without another chunk. This fixture is single-connection and sequential; PostgreSQL’s FOR UPDATE plus its unique constraint is required for the final multiple-worker boundary. closing closes the connection separately from the transaction context.'),
('Choose the next guarantee deliberately', 'After an offline enqueue, predict one accepted row and zero chunks. Requeue the same ID once the broker is back, consume it twice, then expect one chunk and ready. Explicit requeue is a recovery mechanism, not guaranteed automatic delivery. An outbox stored in the same transaction plus a retried dispatcher can close the durable delivery gap, but requires its own leasing, duplicate-delivery and backlog tests. Do not claim that extension is implemented here.')],
(CASES/'accelerator_delivery.py').read_text(),
'Reuse d1 with changed content and prove it raises an identity conflict while preserving the original text, ready state and single chunk. Do not weaken the duplicate-delivery checks.',
'''with closing(sqlite3.connect(':memory:')) as db:
    db.executescript('CREATE TABLE jobs(id TEXT PRIMARY KEY,text TEXT,state TEXT);CREATE TABLE chunks(job TEXT UNIQUE,text TEXT);')
    queued=[];accept(db,'d1','unused items only',queued.append);consume(db,'d1')
    try:accept(db,'d1','opened items allowed',queued.append)
    except ValueError:pass
    else:raise AssertionError('changed content reused identity')
    assert db.execute('SELECT text,state FROM jobs').fetchone()==('unused items only','ready')
    assert db.execute('SELECT count(*) FROM chunks').fetchone()[0]==1 and queued==['d1']
print('variation: identity conflict retained original committed work')''',
['Check the stored text before enqueueing or ignoring a duplicate insert.','The changed input must not reach queued.append.','Read text, state and chunk count after the failure; preserving only the row count is insufficient.'],
'If two deliveries create two chunks, inspect the unique key and ready check. If queue failure removes the accepted row, your transaction includes the wrong boundary. If changed content returns success under d1, INSERT OR IGNORE hid a conflict. For concurrent production workers use the published PostgreSQL lock/transaction path, not this sequential SQLite teaching model.',
'The database commit succeeds but enqueue fails. What should the API expose?',
('An accepted document ID and recoverable delivery failure.','The caller can inspect and requeue the same persisted work without fabricating readiness.'),
('ready because the source row exists.','Existence is not completed parsing or indexing.'),
('No document exists, so the client must create a new upload.','That contradicts the committed row and can multiply work.'))

context_code=function('genai-accelerator','evidence.py','select_document')+'''
chunks=[{'position':0,'text':'Refunds within 14 days'},
        {'position':1,'text':'Unused items only'}]
selected,used=select_document(chunks,'refunds')
assert selected==chunks and used==39
assert select_document(chunks,'wallpaper')==([],0)
print('matched policy retains its unmatched exception; unknown topic has no evidence')
'''
add('genai-accelerator','lesson-16','Do not drop an unmatched policy exception from context',
'Lessons 13 and 16: response invariants and whole-passage context budgets. This is a conservative context adapter for the final small-policy capstone, not a general document search engine.',[
('Find the dependency that lexical matching misses','A source can say “Refunds within 14 days” in one sentence and “Unused items only” in another. A refund query matches the first sentence but not the second. Returning only matched sentences drops an applicability condition even when every citation ID is valid. Chunking and context selection must preserve the dependency before generation, rather than expecting a prompt to reconstruct unseen evidence.'),
('Choose an explicit bounded policy','For this small synthetic-policy service, any matching sentence selects the entire authorized document. No match still returns an empty result. The source has already been owner-filtered by the API. This trades extra context for preserving source conditions; it is deliberately unsuitable for arbitrarily long documents. It does not detect all cross-document conflicts or prove which policy applies to a customer.'),
('Refuse overflow rather than slice meaning','Sum the text lengths of all selected sentence chunks before returning them. If they exceed 1000 characters, raise context_review_required. The HTTP adapter exposes 409; the agent treats a non-success response as unavailable, not empty evidence. A later safe reviewed split can replace this coarse policy, but has to preserve source locators and exception dependencies. A character allowance is not a provider token measurement.'),
('Compare the two populations honestly','Predict both chunks and 39 selected characters for the worked policy, but no chunks for wallpaper. Separators added when joining the answer are accounted separately by the response validator from lesson 13. Record increased context size when comparing this complete-document baseline with sentence selection. The fixture protects omission of conditions within this document; semantic answer support and real-model cost remain separate observations.')],
context_code,
'Add a long unmatched exception to a document containing a matching refund rule. Require context_review_required instead of a partial answer; preserve the no-match abstention case.',
'''large=chunks+[{'position':2,'text':'x'*1000}]
try:select_document(large,'refunds')
except ValueError as error:assert str(error)=='context_review_required'
else:raise AssertionError('dependent context silently dropped')
assert select_document(large,'wallpaper')==([],0)
print('variation: oversized matched document requires review; no-match remains empty')''',
['Once this document matches, count all its chunks, not just matched ones.','Check the error path before an answer can be assembled.','Use a separate unknown-topic query to prove overflow is not confused with missing evidence.'],
'If only the refund sentence survives, the old sentence-selection rule remains. If long relevant context returns an empty success, a failed budget check has become false abstention. Inspect the HTTP 409 and agent unavailable path separately from actual empty retrieval.',
'A refund sentence matches, but its unmatched exclusion makes the complete document exceed the budget. What should this capstone do?',
('Return context_review_required; do not produce a partial answer.','The selected document cannot fit while retaining its dependent conditions.'),
('Omit the unmatched exclusion and cite the first sentence.','That can turn a conditional rule into an unsupported unconditional answer.'),
('Return a successful empty search because the text is too long.','That confuses known evidence that cannot fit with evidence that does not exist.'))

def prepare_capstones():
    start='<!-- student-depth:start -->';end='<!-- student-depth:end -->'
    for guide in Path(__file__).with_name('student_depth_guides').glob('*.md'):
        path=CAPS/guide.stem/'README.md';original=path.read_text()
        if start in original:
            before,rest=original.split(start,1);_,after=rest.split(end,1)
            original=before.rstrip()+'\n\n'+after.lstrip()
        else:
            original=original.split('## Student build walkthrough —',1)[0].rstrip()+'\n'
        anchor='## Build from a fresh folder' if '## Build from a fresh folder' in original else '## Run the complete example'
        before,after=original.split(anchor,1)
        path.write_text(before.rstrip()+'\n\n'+start+'\n'+guide.read_text().strip()+'\n'+end+'\n\n'+anchor+after)


def execute(code):
    with tempfile.TemporaryDirectory(prefix='academy-depth-example-') as folder:
        file=Path(folder)/'example.py';file.write_text(code)
        result=subprocess.run([sys.executable,'-I',str(file)],cwd=folder,text=True,capture_output=True,timeout=10)
        if result.returncode:raise RuntimeError(result.stderr)
        return result.stdout.strip()

def fence(language,text):return '```'+language+'\n'+text.strip()+'\n```'

def apply(programs):
    for program in programs:
        for row in program['lessons']:
            key=row['source_id'].rsplit(':',1)[-1]
            studio=STUDIOS.get((program['slug'],key))
            if not studio:continue
            learning=row['resources']['learning'];chapter_id='runtime-studio'
            code=studio['code'];solution=code+'\n# Complete exercise variation\n'+studio['patch']+'\n'
            body='## Before this studio\n\n'+studio['prerequisite']+'\n\n'
            body+='\n\n'.join('## Step '+str(i+1)+' · '+title+'\n\n'+text for i,(title,text) in enumerate(studio['steps']))
            body+='\n\n## Complete worked example\n\nSave this entire block as example.py in a fresh directory. Run `python3.12 -I example.py` with assertions enabled. All imports are included; no account, provider call or other course is required.\n\n'+fence('python',code)+'\n\n## Expected observation\n\n'+fence('text',execute(code))
            body+='\n\n## Try the aligned variation\n\n'+studio['task']+'\n\nKeep the demonstrated assertions and record your prediction, actual result and one failing case before revealing the reference.\n\n## Staged hints\n\n'+'\n\n'.join(str(i+1)+'. '+hint for i,hint in enumerate(studio['hints']))
            body+='\n\n## Complete variation reference\n\nAfter your own attempt, save this complete block as solution.py and run `python3.12 -I solution.py`. It contains the original example as well as the variation.\n\n'+fence('python',solution)+'\n\n## Expected variation observation\n\n'+fence('text',execute(solution))+'\n\n## Diagnose and explain\n\n'+studio['diagnosis']
            chapter=dict(id=chapter_id,title=studio['title'],kind='Guided runtime studio',body=body)
            chapters=learning['chapters'];at=next(i for i,c in enumerate(chapters) if c['id'] in {'case-study','project'})
            chapters.insert(at,chapter)
            learning['exercise']['steps'].append('Complete the runtime studio variation: '+studio['task']+' Its complete reference and diagnosis are in the studio chapter.')
            learning['exercise']['material']+='\n\n## Runtime studio practice\n\n'+studio['task']+' Read the four teaching steps and full example before attempting it; compare with the complete studio reference afterward.'
            criterion='Runtime studio: '+studio['task']+' Retain the positive and negative observations and explain the verification boundary.'
            learning['task']['criteria'].append(criterion)
            learning['exercise']['material']+='\n\n'+criterion
            choices=[studio['right'],*studio['wrongs']];shift=len(row['title'])%3;choices=choices[shift:]+choices[:shift]
            correct=next(chr(97+i) for i,c in enumerate(choices) if c==studio['right'])
            learning['quiz'].append(dict(id='runtime-studio',prompt=studio['question'],review_chapter=chapter_id,correct=correct,
                options=[dict(id=chr(97+i),text=text) for i,(text,_) in enumerate(choices)],
                explanation=studio['right'][1],option_feedback={chr(97+i):feedback+' Revisit the worked example and its counterexample in the runtime studio.' for i,(_,feedback) in enumerate(choices)}))
            learning['flashcards'].append(dict(id='runtime-studio',front=studio['question'],back=studio['right'][0]+' '+studio['right'][1]))
            learning['questions'].append(dict(id='runtime-studio',prompt=studio['task'],guidance=studio['diagnosis']))
            row['minutes']+=30
            refresh(row)
