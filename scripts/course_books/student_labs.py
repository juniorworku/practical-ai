"""Complete offline examples, not fragments extracted from unrelated projects.
Each example runs independently with Python 3.12 and its embedded synthetic data.
"""
import textwrap
from pprint import pformat
LABS = {}
def add(key, code, explanation, extension):
    LABS[key] = {'code': textwrap.dedent(code).strip()+'\n', 'explanation': explanation, 'extension': extension}

add('B01', '''
def handle(requested):
    allowed = {'read_policy', 'draft'}
    return {'permitted': sorted(set(requested) & allowed),
            'review': sorted(set(requested) - allowed)}
result = handle(['read_policy', 'draft', 'refund'])
assert result == {'permitted': ['draft', 'read_policy'], 'review': ['refund']}
print(result)
''', 'The requested operations are proposals. Intersection with a fixed application allowlist determines permitted operations; the difference is routed to review. No code here issues a refund. This is a scope baseline, not a natural-language intent detector. A real dispatcher must repeat authorization when an operation executes.', 'Add delete_account and prove it remains in review. Then represent a request with no supporting policy: permitted drafting must still return an unavailable outcome rather than fabricate an answer.')

add('B02', '''
from pathlib import Path
from tempfile import TemporaryDirectory
import json, os
with TemporaryDirectory() as folder:
    root = Path(folder)
    (root / 'app').mkdir()
    (root / 'data').mkdir()
    (root / 'data/policies.json').write_text('[{"id":"returns-v1"}]', encoding='utf-8')
    loader = root / 'app/loader.py'
    loader.write_text('from pathlib import Path\\nimport json\\ndef load():\\n    root = Path(__file__).resolve().parent.parent\\n    return json.loads((root / "data/policies.json").read_text(encoding="utf-8"))\\n', encoding='utf-8')
    import runpy
    original = Path.cwd()
    try:
        os.chdir(root / 'app')
        first = runpy.run_path(str(loader))['load']()
        os.chdir(root.parent)
        second = runpy.run_path(str(loader))['load']()
        assert first == second == [{'id': 'returns-v1'}]
    finally:
        os.chdir(original)
print('two working directories: same fixture')
''', 'The example creates every required file in a temporary project. The loader resolves its own file location, then ascends to the declared project root. Changing the caller’s working directory therefore does not change the fixture path. finally restores the shell location before the temporary directory is removed. This tests paths; dependency isolation still requires the fresh virtual environment exercise.', 'Make the fixture absent and replace an unhelpful traceback with a clear setup failure. Run the file with a new virtual environment from a parent directory; record the interpreter version and command.')

add('B03', '''
cases = [
 {'id':'q1','family':'unopened','split':'development','expected':'answer'},
 {'id':'q2','family':'missing_condition','split':'development','expected':'clarify'},
 {'id':'q3','family':'unavailable','split':'holdout','expected':'abstain'},
]
def used_for_tuning(case):
    return dict(case, split='development', reason='inspected and tuned')
cases[2] = used_for_tuning(cases[2])
assert not any(c['split'] == 'holdout' for c in cases)
assert len({c['id'] for c in cases}) == len(cases)
print([(c['id'], c['split'], c['expected']) for c in cases])
''', 'Each expected label names behavior, not merely a preferred sentence. q2 is answerable after the customer supplies a condition; q3 lacks a policy at all. Relabeling an inspected holdout preserves its history instead of deleting the failure. No score in this example estimates generalization: there is now no untouched set.', 'Write two new holdout families without tuning on them. Explain why paraphrases of q1 in both splits may still leak the same decision pattern.')

add('B04', '''
import json
def validate(raw, known):
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return ['invalid_json']
    if type(data) is not dict or set(data) != {'status','answer','citations'}:
        return ['fields']
    if data['status'] not in ('answer','clarify','abstain') or type(data['answer']) is not str:
        return ['types_or_status']
    cites = data['citations']
    if type(cites) is not list or any(type(x) is not str for x in cites):
        return ['citation_type']
    if len(set(cites)) != len(cites) or any(x not in known for x in cites):
        return ['citation_identity']
    if data['status'] == 'answer' and (not cites or not data['answer'].strip()):
        return ['answer_requires_evidence']
    return []
valid = {'status':'answer','answer':'Unopened items within 14 days.','citations':['returns-v1']}
assert validate(json.dumps(valid), {'returns-v1'}) == []
assert validate('{', {'returns-v1'}) == ['invalid_json']
assert validate(json.dumps(dict(valid, citations=['invented'])), {'returns-v1'}) == ['citation_identity']
unsupported = dict(valid, answer='Opened items are always eligible.')
assert validate(json.dumps(unsupported), {'returns-v1'}) == []
print('structure and identity passed; unsupported claim still requires factual review')
''', 'Parsing, exact keys, types, membership and answer invariants are separate checks with separate failure reasons. The last assertion deliberately passes an unsupported sentence. This proves the limit of validation: reference existence is not evidence that the passage supports a claim. A reviewer or separately evaluated support check must compare the actual wording and policy conditions.', 'Add a status invariant requiring abstentions to have an empty citation list. Test an extra owner_id field, repeated citation, and a well-formed answer that drops an exception; report structural and factual outcomes separately.')

add('B05', '''
def generate(outcomes, deadline=5, max_attempts=3):
    if deadline <= 0 or type(max_attempts) is not int or max_attempts < 1:
        raise ValueError('positive deadline and attempts required')
    elapsed = 0
    for attempt, (status, duration, wait) in enumerate(outcomes[:max_attempts], 1):
        elapsed += duration
        if elapsed >= deadline:
            return ('deadline', attempt, elapsed)
        if status == 200:
            return ('draft', attempt, elapsed)
        if status not in (429, 503):
            return ('permanent_failure', attempt, elapsed)
        if attempt == max_attempts or elapsed + wait >= deadline:
            return ('retry_stopped', attempt, elapsed)
        elapsed += wait
    return ('no_more_fixture_responses', attempt if outcomes else 0, elapsed)
assert generate([(429, 1, 2), (200, 1, 0)]) == ('draft', 2, 4)
assert generate([(403, 1, 0), (200, 1, 0)]) == ('permanent_failure', 1, 1)
assert generate([(503, 2, 4), (200, 1, 0)])[0] == 'retry_stopped'
print('transient retry: 2 calls, 4 simulated seconds; permission failure: 1 call')
''', 'Each tuple is a fake response: status, request duration, requested backoff. The total deadline covers requests and waits, while max_attempts bounds calls. A permanent authorization failure terminates immediately. This does not enforce a socket timeout: a real adapter must pass the remaining deadline to its network client. The example retries read-only generation, not external writes.', 'Add exponential backoff capped by remaining time, then test a response arriving exactly at the deadline. Keep all timing simulated; report no real provider latency or reliability from this fixture.')

add('B06', '''
def pack(window, fixed, reserve, passages):
    budget = window - sum(fixed.values()) - reserve
    if budget < 0:
        raise ValueError('instructions and output exceed context window')
    selected, omitted = [], []
    for passage in passages:
        if passage['tokens_including_metadata'] <= budget:
            selected.append(passage['id'])
            budget -= passage['tokens_including_metadata']
        else:
            omitted.append(passage['id'])
    return selected, omitted, budget
passages = [{'id':'returns-rule-and-exception','tokens_including_metadata':180},
            {'id':'shipping','tokens_including_metadata':150},
            {'id':'contact','tokens_including_metadata':90}]
result = pack(1000, {'system':180,'tools':120,'history':240}, 200, passages)
assert result == (['returns-rule-and-exception'], ['shipping','contact'], 80)
print(result)
''', 'The available retrieval budget is 1000 − 180 − 120 − 240 − 200 = 260. Selecting the 180-token policy leaves 80, insufficient for either later passage. Whole passages preserve exceptions and metadata. These are supplied token counts, not a tokenizer: actual model-specific counts must be measured before a live request. Ordering is a relevance assumption, not an optimal packing algorithm.', 'Increase instructions by 100. Predict which complete passages now fit and verify the result. Compare relevance-first selection with maximizing passage count; identify a case where more passages gives a worse answer.')

add('B07', '''
import hashlib
versions, active = {}, {}
def ingest(document, revision, text):
    key = (document, revision)
    fingerprint=hashlib.sha256(text.encode()).hexdigest()
    if key in versions:
        if versions[key]['digest']!=fingerprint:raise ValueError('revision_content_conflict')
        return key
    versions[key] = {'text':text, 'digest':fingerprint, 'indexed':False}
    return key
def activate(key):
    if not versions[key]['indexed']:
        return False
    active[key[0]] = key
    return True
v1 = ingest('returns','v1','Unopened items: 14 days.')
versions[v1]['indexed'] = True
assert activate(v1)
v2 = ingest('returns','v2','Unopened items: 21 days.')
assert not activate(v2) and active['returns'] == v1
versions[v2]['indexed'] = True
assert activate(v2) and versions[v1]['text'].endswith('14 days.')
print('v1 retained; v2 activated only after indexing')
''', 'The hash identifies exact source bytes; it does not prove correctness or effective date. The active pointer changes only after the new revision is ready. Keeping v1 enables historical references and recovery. This in-memory demonstration shows the lifecycle invariant; production activation must also check evaluation/effective dates and commit its pointer atomically in durable storage.', 'Add a failed-parse state and an effective date. Prove a failed or future revision does not replace current policy. Do not silently use today’s policy to answer a historical-date question.')

add('B08', '''
import re
def retrieve(query, passages, k):
    words = set(re.findall(r'[a-z]+', query.lower()))
    ranked = [(len(words & set(re.findall(r'[a-z]+', p['text'].lower()))), p) for p in passages]
    ranked.sort(key=lambda pair: (-pair[0], pair[1]['id']))
    return [p['id'] for score,p in ranked if score > 0][:k]
passages = [{'id':'returns-2','text':'Return an unopened item within 14 days. Opened items excluded.'},
            {'id':'shipping-1','text':'Shipping takes five working days.'}]
assert retrieve('return unopened item', passages, 1) == ['returns-2']
assert retrieve('astronomy', passages, 3) == []
assert retrieve('delivery', passages, 3) == []
ranked, gold = ['shipping-1','returns-2'], {'returns-2'}
recall_at_1 = len(set(ranked[:1]) & gold) / len(gold)
recall_at_2 = len(set(ranked[:2]) & gold) / len(gold)
assert (recall_at_1, recall_at_2) == (0, 1)
print('recall@1=0; recall@2=1; lexical delivery/shipping mismatch remains')
''', 'Set overlap is a deliberately simple baseline. Filtering zero scores prevents unrelated passages being treated as evidence. Sorting by ID resolves ties reproducibly. The second experiment uses fixed ranked IDs to distinguish ranking metrics from generation quality: finding a passage within k does not prove the answer uses it. The baseline misses synonyms and ignores negation.', 'Add three labeled queries, including a synonym and a no-source question. Compare recall at one and two while preserving whole rule-plus-exception chunks. Record empty-gold cases separately rather than dividing by zero.')

add('B09', '''
def decide(condition, source, claim):
    if source is None:
        return 'abstain'
    if condition is None:
        return 'clarify'
    # A human-prepared fixture label, not automated semantic entailment.
    support_labels = {('unopened','Unopened within 14 days'):True,
                      ('opened','Opened items qualify'):False,
                      ('opened','Opened items are excluded'):True}
    return 'draft_for_review' if support_labels.get((condition,claim),False) else 'revise_or_abstain'
policy = 'Only unopened items within 14 days; opened items excluded.'
assert decide(None, policy, '') == 'clarify'
assert decide('unopened', None, '') == 'abstain'
assert decide('opened', policy, 'Opened items qualify') == 'revise_or_abstain'
assert decide('opened', policy, 'Opened items are excluded') == 'draft_for_review'
assert decide('unopened', policy, 'Unopened within 14 days') == 'draft_for_review'
print('missing applicability: clarify; missing source: abstain; contradicted claim: revise')
''', 'The order matters: no policy means unavailable evidence; a known policy with missing item condition needs clarification. The support table is explicitly manually labeled. It teaches expected behavior without pretending string membership can solve entailment. A live model must be evaluated on claim support, exception preservation, and applicability independently of citation ID checks.', 'Add an enterprise policy with a different scope. Write a counterexample where both source IDs exist but the wrong account policy is used. Explain how scope selection fails before generation begins.')

add('B10', '''
POLICIES = {'p1': {'owner':'acme', 'text':'Unopened: 14 days.'}}
def dispatch(actor, name, arguments):
    if name != 'lookup_policy':
        return {'error':'unknown_tool'}
    if type(arguments) is not dict or set(arguments) != {'policy_id'} or type(arguments['policy_id']) is not str:
        return {'error':'invalid_arguments'}
    record = POLICIES.get(arguments['policy_id'])
    if record is None or record['owner'] != actor:
        return {'error':'not_found'}
    return {'id':arguments['policy_id'], 'text':record['text']}
assert dispatch('acme','lookup_policy',{'policy_id':'p1'})['id'] == 'p1'
assert dispatch('other','lookup_policy',{'policy_id':'p1'}) == {'error':'not_found'}
assert dispatch('acme','lookup_policy',{'policy_id':'p1','owner':'other'}) == {'error':'invalid_arguments'}
assert dispatch('acme','send_files',{}) == {'error':'unknown_tool'}
print('authorized lookup passed; cross-owner, injected identity and unknown tool blocked')
''', 'actor is supplied by the application’s authenticated context, never copied from model arguments. Exact argument keys reject an injected identity. The tool returns only allowed fields, and an inaccessible record uses the same public error as an absent one. The example omits HTTP authentication on purpose; later API work must establish actor before calling this dispatcher.', 'Add a second allowed read-only operation with a different schema. Test an allowed name with an unauthorized ID, not only an obviously forbidden tool name. Keep the actor separate from request JSON.')

add('B11', '''
def run(decisions, max_steps=3):
    trace = [];state='start'
    allowed={'start':{'retrieve','abstain'},'evidence':{'retrieve','answer','abstain'}}
    for action in decisions:
        if len(trace) >= max_steps:
            return {'status':'step_limit','trace':trace}
        if action not in allowed[state]:
            return {'status':'failed','trace':trace + ['rejected:'+action]}
        trace.append(action)
        if action=='retrieve':state='evidence'
        if action in {'answer','abstain'}:
            return {'status':action,'trace':trace}
    return {'status':'needs_context','trace':trace}
assert run(['retrieve']*3 + ['answer'])['status'] == 'step_limit'
assert run(['retrieve','answer'])['trace'] == ['retrieve','answer']
assert run(['retrieve','delete'])['status'] == 'failed'
assert run([])['status'] == 'needs_context'
assert run(['answer'])['status']=='failed'
print('terminal states: answer, abstain, step_limit, failed; no fabricated success')
''', 'The decision list replaces a model so control flow can be inspected deterministically. The runtime checks the step budget before executing another proposal. Only an allowed terminal action ends successfully. This example bounds steps but not time, tokens, or tool exceptions; those must be added explicitly rather than inferred from a finite loop.', 'Wrap a fake retriever that raises an exception and record a failed tool observation. Add an overall simulated deadline, then test a loop that exhausts time before its step limit.')

add('B12', '''
import hashlib, json
def digest(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
payload = {'owner':'acme','recipient':'local-reviewer','content':'Policy draft','revision':2}
approval = {'digest':digest(payload),'actor':'lead','expires':10}
ledger, effects = {}, []
def execute(data, now, actor_active=True, lose_response=False, actor='lead'):
    if actor!=approval['actor'] or not actor_active or now >= approval['expires'] or digest(data) != approval['digest']:
        return 'needs_review'
    key = data['owner']+':a7:r'+str(data['revision'])
    if key in ledger:
        return 'reconcile_existing' if ledger[key]=='uncertain' else 'already_committed'
    ledger[key] = 'claimed'
    effects.append((key,dict(data)))  # Local fake destination; no external send.
    ledger[key] = 'uncertain' if lose_response else 'committed'
    return ledger[key]
assert execute(dict(payload, recipient='changed'),1) == 'needs_review'
assert execute(payload,1,actor_active=False) == 'needs_review'
assert execute(payload,10) == 'needs_review'
assert execute(payload,1,actor='other')=='needs_review'
assert execute(payload,1,lose_response=True) == 'uncertain'
assert execute(payload,2) == 'reconcile_existing' and len(effects)==1
print('one fake effect; lost response remains uncertain until reconciled')
''', 'The digest binds effect fields to the reviewed payload. Expiry and actor authority are checked again before execution. The fake destination records an effect before losing the response, so a retry must reconcile the same key rather than send again. This single-process dictionary does not provide an atomic multi-worker claim or crash durability. A database constraint/transaction and destination-specific idempotency are required for those claims.', 'Replace the in-memory ledger with SQLite and a unique scoped key. Use two connections to attempt a claim, then restart after an uncertain result. Do not treat a local unique key as proof of exactly-once remote delivery.')

add('B13', '''
# Application boundary only: no web server or real identity provider.
TOKENS = {'test-acme':'acme'}
def post_draft(token, body, provider):
    actor = TOKENS.get(token)
    if actor is None:
        return 401, {'error':'authentication_required'}
    if type(body) is not dict or set(body) != {'question'} or type(body['question']) is not str:
        return 400, {'error':'invalid_fields'}
    question = body['question'].strip()
    if not question or len(question)>500:
        return 400, {'error':'invalid_question'}
    draft = {'owner':actor,'question':question,'status':'pending'}
    try:
        draft['answer'] = provider(question)
        draft['status'] = 'needs_review'
    except TimeoutError:
        draft['status'] = 'generation_failed'
        return 503, {'error':'provider_unavailable','draft':draft}
    return 201, draft
assert post_draft('bad',{},lambda q:'x')[0] == 401
assert post_draft('test-acme',{'question':''},lambda q:'x')[0] == 400
assert post_draft('test-acme',{'question':'Returns?'},lambda q:'14-day unopened policy')[0] == 201
def unavailable(question):
    raise TimeoutError('synthetic private provider details')
status, result = post_draft('test-acme',{'question':'Returns?'},unavailable)
assert status == 503 and result['draft']['question']=='Returns?'
assert 'synthetic private' not in str(result)
print('401 authentication; 400 input; 201 draft; 503 recoverable provider failure')
''', 'Authentication precedes validation. Exact fields reject client-supplied ownership. Failure returns a stable category and retains the question, without exposing raw exception text. The returned draft is not durable yet: the persistence lesson adds that boundary. 503 here means synchronous generation failed; it is not a promise that a background job will finish.', 'Implement this contract in your own DRF endpoint using request.user, a serializer and a saved draft. Capture actual HTTP requests for the four statuses. The fixed TOKENS fixture must never become production authentication.')

add('B14', '''
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as folder:
    path = Path(folder)/'drafts.sqlite'
    db = sqlite3.connect(path)
    db.executescript('CREATE TABLE drafts(owner TEXT, key TEXT, version INT, body TEXT, UNIQUE(owner,key)); CREATE TABLE audit(event TEXT);')
    with db:
        db.execute('INSERT INTO drafts VALUES(?,?,?,?)',('acme','d1',4,'original'))
    def save(owner, key, version, text, fail=False):
        try:
            with db:
                changed = db.execute('UPDATE drafts SET body=?,version=version+1 WHERE owner=? AND key=? AND version=?',(text,owner,key,version)).rowcount
                if changed != 1:
                    return 'conflict_or_inaccessible'
                if fail:
                    raise RuntimeError('audit failed')
                db.execute('INSERT INTO audit VALUES(?)',('saved',))
        except RuntimeError:
            return 'rolled_back'
        return 'saved'
    assert save('acme','d1',4,'correction') == 'saved'
    assert save('acme','d1',4,'stale') == 'conflict_or_inaccessible'
    assert save('other','d1',5,'attack') == 'conflict_or_inaccessible'
    assert save('acme','d1',5,'partial',True) == 'rolled_back'
    db.close()
    db = sqlite3.connect(path)
    assert db.execute('SELECT version,body FROM drafts').fetchone() == (5,'correction')
    assert db.execute('SELECT count(*) FROM audit').fetchone()[0] == 1
    db.close()
print('version 5 survives reopen; stale, cross-owner and partial saves rejected')
''', 'The UPDATE compares owner, key and expected version in the same database statement. A successful write increments the version. The audit insertion and update share a transaction; raising before audit completion rolls both back. Reopening the file proves server-side file persistence rather than a variable retaining data. SQLite teaches the invariant locally; PostgreSQL concurrency behavior must be tested in your actual app.', 'Add a unique scoped action key and race two independent connections. Record the exact conflict behavior. Simulate a remote send after commit and explain why rolling back this transaction cannot unsend it.')

add('B15', '''
def view(state, question, error=None):
    labels = {'idle':'Ask a policy question','loading':'Generating draft',
              'review':'Draft needs review','clarify':'More information needed',
              'abstain':'No supporting policy','failed':'Generation failed'}
    if state not in labels:
        raise ValueError('unknown UI state')
    return {'label':labels[state], 'question':question,
            'retry':state=='failed', 'export_enabled':False,
            'busy':state=='loading', 'error':error if state=='failed' else None}
question = 'Can I return this item?'
assert view('loading',question)['busy']
failed = view('failed',question,'Please retry; your question is retained.')
assert failed['question']==question and failed['retry'] and not failed['busy']
assert not view('review',question)['export_enabled']
print('loading, review and failure remain distinct; input retained; export unapproved')
''', 'This is a view-state contract, not a rendered React interface. It separates machine completion from human approval, always retains the input, and exposes an explicit retry affordance after failure. Disabling export here models a draft-only release; a future reviewed export needs a separate approved revision. State assertions cannot establish keyboard usability or whether labels make sense to people.', 'Render these states in your interface with an associated input label, status announcement and focusable retry button. Disconnect the API after submission. Use keyboard only, then ask a peer to explain the draft status without hints; save both observations.')

add('B16', '''
# Expected labels stay outside candidate requests.
def candidate(request):
    if request['scope']!='acme':return 'answer'  # Deliberate defect to detect.
    if not request['has_source']:return 'abstain'
    return 'answer'  # Deliberate missing-condition defect.
cases=[{'category':'normal','input':{'scope':'acme','has_source':True,'condition':'unopened'},'expected':'answer'},
       {'category':'ambiguous','input':{'scope':'acme','has_source':True,'condition':None},'expected':'clarify'},
       {'category':'missing','input':{'scope':'acme','has_source':False,'condition':'unopened'},'expected':'abstain'},
       {'category':'security','input':{'scope':'other','has_source':True,'condition':'unopened'},'expected':'deny'}]
counts={};critical=[]
for case in cases:
    actual=candidate(dict(case['input']))
    row=counts.setdefault(case['category'],[0,0]);row[0]+=int(actual==case['expected']);row[1]+=1
    if case['category']=='security' and actual!=case['expected']:critical.append(case['category'])
passed=sum(a for a,b in counts.values())
assert passed==2 and len(cases)==4 and critical==['security']
print({'passed':passed,'total':len(cases),'categories':counts,'promote':False})
''', 'Each row has category, expected behavior and observed behavior. Every case contributes to its denominator, including incorrect answers and unavailable outcomes. The security failure independently blocks promotion even if an aggregate threshold passes. The expected labels are fixture judgments; scoring real factual support requires a rubric and a reviewer, not exact string comparison alone.', 'Add separate retrieval and claim-support columns, plus one provider-unavailable result. Show how a candidate improves the overall fraction while regressing on the missing-evidence category; retain both reports.')

add('B17', '''
records = {'p1':{'owner':'acme','text':'Return unopened within 14 days.'},
           'private':{'owner':'other','text':'CANARY-OTHER-SECRET'}}
def lookup(actor, identifier):
    record = records.get(identifier)
    return record['text'] if record and record['owner']==actor else 'inaccessible'
def dispatch(actor, proposed):
    name, identifier = proposed
    if name != 'lookup':
        return 'tool_denied'
    return lookup(actor,identifier)
# These are adversarial model proposals, not commands executed by this file.
results = [dispatch('acme',p) for p in [('send_files','all'),('lookup','private'),('lookup','p1')]]
assert results == ['tool_denied','inaccessible','Return unopened within 14 days.']
assert 'CANARY-OTHER-SECRET' not in str(results)
print('forbidden operation and allowed-tool cross-owner attack both denied')
''', 'Testing only forbidden tool names misses attacks that abuse an allowed lookup with an unauthorized ID. The ownership check remains inside the tool regardless of what the retrieved document says. Synthetic proposals test enforcement, not whether a particular model resists instructions; those are distinct evaluations. This narrow example cannot establish that every output channel or logging path is safe.', 'Write five malicious synthetic passages, then manually or through a controlled fake adapter record their proposed actions. Test both action permissions and canary disclosure in outputs/logs. Document a residual risk that the allowlist alone does not solve.')

add('B18', '''
from math import ceil
runs = [{'ms':100,'cost':2,'accepted':True}, {'ms':120,'cost':3,'accepted':True},
        {'ms':160,'cost':4,'accepted':False}, {'ms':900,'cost':5,'accepted':False}]
latencies = sorted(r['ms'] for r in runs)
accepted = sum(r['accepted'] for r in runs)
unit_cost = sum(r['cost'] for r in runs)/accepted if accepted else None
p95 = latencies[ceil(.95*len(latencies))-1]
assert unit_cost==7 and p95==900
print({'accepted':accepted,'attempts':len(runs),'cost_per_accepted':unit_cost,'p95_ms':p95,'usage_kind':'simulated'})
''', 'All four attempts consume the illustrative 14 cost units, but only two accepted drafts supply the useful-output denominator. Nearest-rank p95 selects ceil(.95 × 4) = 4, so the slowest fixture is reported. With four rows this tail estimate is very unstable; no provider speed or price is measured. If acceptance is zero, cost per accepted output is undefined, not zero.', 'Add a retry that costs 2 units without another accepted draft; recompute the unit cost. Design a trace schema containing run ID, outcome and timings but no raw question or credentials. Test redaction with a synthetic canary.')

add('B20', '''
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as folder:
    root = Path(folder)
    source = sqlite3.connect(root/'source.sqlite')
    source.execute('CREATE TABLE drafts(id TEXT PRIMARY KEY, body TEXT)')
    source.execute('INSERT INTO drafts VALUES(?,?)',('d7','reviewed policy draft'))
    source.commit()
    backup = sqlite3.connect(root/'backup.sqlite')
    source.backup(backup)
    backup.close()
    restore = sqlite3.connect(root/'restore.sqlite')
    backup = sqlite3.connect(root/'backup.sqlite')
    backup.backup(restore)
    assert restore.execute('SELECT id,body FROM drafts').fetchall() == [('d7','reviewed policy draft')]
    assert source.execute('SELECT count(*) FROM drafts').fetchone()[0] == 1
    for connection in (source,backup,restore): connection.close()
print('isolated restore verified by representative content; live source unchanged')
''', 'SQLite’s backup API copies a consistent database into another file. A second copy restores it into an isolated target; comparing a representative body checks more than row counts. The original remains unchanged. This is a local recovery mechanism, not a PostgreSQL backup recipe. A production runbook also needs backup age, access, retention, restoration time and acceptable data loss.', 'In your own isolated PostgreSQL Compose project, take a logical backup and restore into a separate database. Compare IDs and representative content before any promotion. Do not run destructive recovery steps against the academy database.')

add('B21', '''
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as folder:
    path = Path(folder)/'jobs.sqlite'
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY,state TEXT,version INT)')
    db.execute('INSERT INTO jobs VALUES(?,?,?)',('j1','waiting_review',2))
    db.commit(); db.close()
    db = sqlite3.connect(path)
    def resume(expected):
        with db:
            return db.execute("UPDATE jobs SET state='ready',version=version+1 WHERE id='j1' AND state='waiting_review' AND version=?",(expected,)).rowcount
    assert resume(2)==1 and resume(2)==0
    assert db.execute('SELECT state,version FROM jobs').fetchone()==('ready',3)
    db.close()
print('resume survives reopen; duplicate version-2 transition has zero effect')
''', 'The persisted waiting state survives closing the connection. A conditional transition consumes a particular version once, so replaying the same review cannot advance it twice. This solves one requirement—durable review resumption—without introducing multiple agents. It does not make a subsequent external send atomic; that still requires the effect ledger from the approval lesson.', 'Compare this state machine with the earlier bounded loop. Interrupt before and after the conditional update and explain which work may be repeated. Add two independent connections to verify your actual database’s contention behavior.')

add('B22', '''
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path
POLICY = {'id':'returns-v1','text':'Only unopened items within 14 days; opened items excluded.'}
def draft(condition, provider):
    if condition is None: return {'status':'clarify','citations':[]}
    if condition not in {'unopened','opened'}: return {'status':'abstain','citations':[]}
    try: answer = provider(POLICY['text'])
    except TimeoutError: return {'status':'generation_failed','citations':[]}
    return {'status':'needs_review','answer':answer,'citations':[POLICY['id']]}
def offline(text): return text  # Deterministic fake provider, not a trained model.
with TemporaryDirectory() as folder:
    path=Path(folder)/'runs.sqlite'
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE runs(id TEXT,owner TEXT,status TEXT,source TEXT)')
    result=draft('unopened',offline)
    with db: db.execute('INSERT INTO runs VALUES(?,?,?,?)',('r1','acme',result['status'],result['citations'][0]))
    db.close(); db=sqlite3.connect(path)
    assert db.execute('SELECT source FROM runs WHERE id=? AND owner=?',('r1','acme')).fetchone()==('returns-v1',)
    assert db.execute('SELECT source FROM runs WHERE id=? AND owner=?',('r1','other')).fetchone() is None
    assert draft(None,offline)['status']=='clarify'
    assert draft('commercial-contract',offline)['status']=='abstain'
    assert draft('opened',offline)['status']=='needs_review'
    def unavailable(text): raise TimeoutError()
    assert draft('unopened',unavailable)['status']=='generation_failed'
    db.close()
print('offline application slice: draft, clarify, abstain, failure, durable scoped readback')
''', 'This deliberately small application-layer slice connects policy selection, fake drafting, an explicit status, a source revision and durable owner-scoped readback. It is not a UI/API capstone by itself. The hard-coded condition supports only this synthetic policy, not free-text eligibility reasoning. It gives you a known baseline to connect to your own actual browser and DRF endpoint.', 'Connect this behavior to your own UI and API, then replay all five paths through HTTP. Store the original question and full result in your actual schema. Distinguish observed browser behavior from this application-layer test.')

add('B23', '''
review = [('supported',7),('correct_abstention',2),('unsupported_answer',1)]
total = sum(n for _,n in review)
critical = dict(review)['unsupported_answer']
assert total==10 and critical==1
report = {'dataset':'unseen-v1','candidate':'demo-r3','total':total,
          'supported':7,'correct_abstention':2,'critical_false_answers':critical,
          'promotion':'blocked pending review' if critical else 'review gates'}
assert report['promotion']=='blocked pending review'
print(report)
''', 'The 9/10 superficially correct outcomes cannot erase the unsupported answer. Category counts preserve the nature of that failure. Candidate and dataset IDs make the result traceable. These are simulated reviewer labels, not actual measurements of your capstone; copy the report structure, not its scores. Once you tune on these cases, they are development evidence.', 'Have a peer label one genuinely unfamiliar case and record disagreement before resolving it against policy text. Fix two findings, rerun the affected cases, and add fresh untouched cases for any new generalization claim.')

add('B24', '''
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json
with TemporaryDirectory() as folder:
    root=Path(folder)
    files={'README.txt':'Run python3 demo.py. Fake provider; no live calls.',
           'demo.py':'print("read-only offline demo")\\n','policies.json':'[{"id":"returns-v1"}]'}
    for name,text in files.items(): (root/name).write_text(text,encoding='utf-8')
    manifest={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}
    (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    assert all((root/name).is_file() for name in manifest)
    (root/'policies.json').write_text('[]',encoding='utf-8')
    changed=[name for name,digest in manifest.items() if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest]
    assert changed==['policies.json']
print('manifest detects changed fixture; hashes identify files, not teaching quality')
''', 'The manifest binds a release to exact setup and fixture bytes, helping a recipient detect drift. It cannot show the instructions are understandable or complete; that requires a fresh setup performed by another person. A hash also does not establish trustworthiness. Keep the release scope, failure evidence, access-removal steps and known gaps next to this manifest.', 'Have a peer follow only your README from a clean folder. Record every intervention you needed to make. Add a backlog item with an observable acceptance check for each missing assumption.')

add('W01', '''
source = 'Order 2 seats at 12.50 each.'
record = {'quantity':2,'unit_price':'12.50','currency':None,'due_date':None,
          'evidence':{'quantity':'2 seats','unit_price':'12.50 each'},
          'review_reasons':['currency absent','due date absent']}
assert all(span in source for span in record['evidence'].values())
assert record['currency'] is None and record['due_date'] is None
assert record['review_reasons']
print(record)
''', 'The record is manually labeled, not extracted by a model. It establishes a schema and an answer sheet before automation. Evidence spans point to exact text; nullable values represent absent facts rather than zero or a guessed default. Span membership is only a first check: an old quoted price may also occur in the source without being the current price.', 'Add a conflicting amendment and retain both spans with their roles. Create ten labeled requests including zero, missing, unreadable and contradictory values. Do not turn a required key into a requirement to invent a value.')

add('W02', '''
from decimal import Decimal, InvalidOperation
import re
def money(raw):
    if type(raw) is not str or not re.fullmatch(r'[0-9]+[.][0-9]{2}',raw):
        raise ValueError('use an explicit nonnegative decimal with two places')
    number=Decimal(raw)
    if not number.is_finite(): raise ValueError('nonfinite')
    return number
def validate(record):
    errors=[]
    q=record.get('quantity')
    if type(q) is not int or q<=0: errors.append('quantity:invalid')
    try: price,total=money(record.get('unit_price')),money(record.get('total'))
    except (ValueError,TypeError,InvalidOperation): return errors+['amount:invalid']
    if not errors and price*q != total: errors.append('total:mismatch')
    if record.get('currency') not in {'USD','EUR'}: errors.append('currency:review')
    return errors
valid={'quantity':2,'unit_price':'12.50','total':'25.00','currency':'USD'}
assert validate(valid)==[]
assert validate(dict(valid,total='24.00'))==['total:mismatch']
assert 'quantity:invalid' in validate(dict(valid,quantity=True))
for value in ['-1.00','NaN','1,25',None]:
    assert 'amount:invalid' in validate(dict(valid,unit_price=value))
print('valid record accepted; mismatched total, boolean quantity and ambiguous amounts rejected')
''', 'Decimal preserves exact decimal arithmetic for the deliberately narrow supported format. Exact type checks reject Python booleans, which otherwise behave like integers. Validation reports an inconsistency but never rewrites the source to make arithmetic agree. Unsupported formats stop for review; the two-currency allowlist is an exercise boundary, not a global currency catalog.', 'Add a documented normalizer for one additional known source format while preserving its raw value. Test negative quantity, missing currency, infinity and a conflicting total. Keep normalization errors distinct from business-rule errors.')

add('W03', '''
# Manually labeled record correctness and gate outcomes for the same four inputs.
rows = [
 {'id':'d1','correct_fields':3,'fields':3,'record_correct':True,'accepted':True,'review_minutes':1},
 {'id':'d2','correct_fields':2,'fields':3,'record_correct':False,'accepted':True,'review_minutes':1},
 {'id':'d3','correct_fields':2,'fields':3,'record_correct':False,'accepted':False,'review_minutes':4},
 {'id':'d4','correct_fields':3,'fields':3,'record_correct':True,'accepted':False,'review_minutes':3},
]
field_accuracy=sum(r['correct_fields'] for r in rows)/sum(r['fields'] for r in rows)
false_accepted=sum(r['accepted'] and not r['record_correct'] for r in rows)
accepted=sum(r['accepted'] for r in rows)
assert false_accepted==1 and accepted==2
print({'field_accuracy':round(field_accuracy,3),'false_accepted':false_accepted,
       'accepted':accepted,'records':len(rows),'review_minutes':sum(r['review_minutes'] for r in rows)})
''', 'Field accuracy is 10/12, but one of two accepted records is wrong. The accepted-error fraction is 1/2; the population false-acceptance fraction is 1/4. Always name the denominator. The correctly extracted d4 still costs review time because the gate is conservative. These trade-offs require observed review work, not only parser response time.', 'Score a second version on the identical four IDs. Include a critical payment reference that is wrong despite other correct fields. Compare accepted errors and review minutes; state which error cost would change your readiness rule.')

add('W04', '''
from datetime import date, timedelta
transcript=[{'id':'s1','kind':'suggestion','owner':'Sam','text':'Maybe Sam can review'},
            {'id':'s2','kind':'accept','owner':'Sam','text':'I will review on Friday'},
            {'id':'s3','kind':'retract','owner':'Sam','text':'I cannot; leave owner unresolved'}]
def register(events):
    result={'owner':None,'state':'unconfirmed','evidence':[]}
    for event in events:
        result['evidence'].append(event['id'])
        if event['kind']=='accept': result.update(owner=event['owner'],state='confirmed_in_transcript')
        if event['kind']=='retract': result.update(owner=None,state='unconfirmed')
    return result
result=register(transcript)
assert result['owner'] is None and result['evidence']==['s1','s2','s3']
meeting=date(2026,10,20)
# Explicit exercise convention: next occurrence, including today.
friday=meeting+timedelta(days=(4-meeting.weekday())%7)
assert friday.isoformat()=='2026-10-23'
print({'register':result,'anchored_friday':friday.isoformat()})
''', 'The events are human annotations, not an NLP parser. Applying them in order preserves the later retraction; extracting only the first name would invent ownership. Transcript commitment is distinct from later application confirmation. Relative dates need an anchor and an explicit convention: “next Friday” can have multiple interpretations, so ask when the convention is uncertain.', 'Add a reassignment accepted by a second participant. Preserve the superseded statement and unresolved date. Prepare three annotated transcripts before implementing any extraction model.')

add('W05', '''
import csv, io
register={}
def ingest(transcript, action, owner):
    key=(transcript,action)
    if key not in register: register[key]={'id':action,'owner':owner,'version':1,'confirmed':None}
    return register[key]
def edit(row, expected, owner):
    if row['version']!=expected: return 'conflict'
    row.update(owner=owner,version=expected+1,confirmed=None)
    return 'saved'
row=ingest('m3-v1','a2','Amina')
assert ingest('m3-v1','a2','Amina') is row
assert edit(row,1,'David')=='saved'
row['confirmed']=row['version']
assert edit(row,1,'Sam')=='conflict'
buffer=io.StringIO(); writer=csv.writer(buffer); writer.writerow(['id','owner','version'])
for value in register.values():
    if value['confirmed']==value['version']: writer.writerow([value['id'],value['owner'],value['version']])
assert list(csv.reader(io.StringIO(buffer.getvalue())))[1]==['a2','David','2']
assert edit(row,2,'Amina')=='saved' and row['confirmed'] is None
print('one action; revision 2 exported; revision 3 requires confirmation')
''', 'Stable transcript/action identity deduplicates replay of the same annotated action. An edit consumes an expected version and clears confirmation. Export includes only the exact confirmed version. The in-memory store demonstrates transition semantics, not durability or concurrent safety. A new transcript revision requires reconciliation of action identity; simply generating a new key could create duplicate commitments.', 'Store the register and correction history durably. Reprocess an amended transcript and show which existing actions need review. Demonstrate that a stale confirmation cannot confirm a newly edited version.')

add('W06', '''
# Expected annotations identify the particular action and blocking condition.
reference={'publish':{'owner':'Sam','due':'2026-10-23','dependency':'legal review complete'},
           'archive':{'owner':None,'due':None,'dependency':None}}
summary={'publish':{'owner':'David','due':'2026-10-24','dependency':None},
         'email':{'owner':'Amina','due':None,'dependency':None}}
missing=set(reference)-set(summary)
unsupported=set(summary)-set(reference)
lost_dependencies=[key for key in reference.keys() & summary.keys()
                   if reference[key]['dependency']!=summary[key]['dependency']]
owner_errors=sorted(key for key in reference.keys() & summary.keys() if reference[key]['owner']!=summary[key]['owner'])
date_errors=sorted(key for key in reference.keys() & summary.keys() if reference[key]['due']!=summary[key]['due'])
assert missing=={'archive'} and unsupported=={'email'} and lost_dependencies==['publish']
assert owner_errors==date_errors==['publish']
print({'omitted':sorted(missing),'false_commitments':sorted(unsupported),
       'dependency_failures':lost_dependencies,'owner_errors':owner_errors,'date_errors':date_errors})
''', 'The fluent summary has five independently observable defects: an omitted action, an invented action, a lost dependency, a changed owner and a wrong date. The expected Sam/23 October assignment becomes David/24 October in the draft; correcting readability alone cannot fix either error. Separate counts explain the risk better than one “summary quality” number. The comparison assumes manually reconciled action IDs; a language model’s different phrasing must be mapped by a reviewer before this exact-key scoring is meaningful.', 'Prepare 12 checks across your three transcript revisions. Include a cancellation, an unresolved owner and a date correction. Compare two summaries against those same annotations and record source lookups and correction time.')

add('W07', '''
criteria={'offline':'must run with network disabled','utf8':'must preserve accented text','license':'must have documented permitted use'}
evidence=[{'id':'e1','criterion':'offline','kind':'marketing','value':'yes','scope':'advertised'},
          {'id':'e2','criterion':'offline','kind':'technical_note','value':'requires remote API','scope':'default mode'}]
def assessment(criterion):
    rows=[r for r in evidence if r['criterion']==criterion]
    values={r['value'] for r in rows}
    if not rows: return 'unknown'
    return 'conflict_requires_resolution' if len(values)>1 else 'documented_claim_needs_scope_check'
assert assessment('offline')=='conflict_requires_resolution'
assert assessment('license')=='unknown'
print({'offline':assessment('offline'),'license':assessment('license')})
''', 'Criteria are defined before collecting favorable pages. Two differing source statements remain visible; the program cannot resolve scope merely by counting votes. No license evidence means unknown, not permitted. These are synthetic source notes. Real notebook rows also need publisher, exact document version, access date and a short supporting excerpt or observation.', 'Add an observed offline run with environment and command. Decide whether it resolves the documentation conflict or only tests one mode. Add two criteria that would genuinely change your choice.')

add('W08', '''
notes={'e1':{'claim':'A reads UTF-8 locally','kind':'documented_feature'},
       'e2':{'claim':'A passed 4 of 5 fixture inputs','kind':'observed_test'}}
def references_exist(ids):
    return bool(ids) and len(ids)==len(set(ids)) and all(i in notes for i in ids)
assert references_exist(['e1'])
assert not references_exist(['missing'])
assert not references_exist(['e1','e1'])
# Deliberate limit: identity checking cannot establish support for this sentence.
claim='A is more accurate than B everywhere'
assert references_exist(['e1'])
review={'claim':claim,'citations':['e1'],'support':'fail','reason':'feature evidence is not comparative accuracy evidence'}
assert review['support']=='fail'
print(review)
''', 'Reference validation catches missing or duplicate IDs, while human support review checks what those IDs actually establish. e1 supports local UTF-8 behavior; e2 supports a scoped observation on five fixtures. Neither establishes universal comparative accuracy. Keep documented capability and measured behavior in separate columns rather than blending them into a confidence percentage.', 'Write 15 atomic claim records, then annotate one supported and one overreaching synthesis statement for each criterion. Insert a source instruction to hide a negative result and verify the evidence table retains that result.')

add('W09', '''
fixtures={'d1':'café','d2':'two lines\\nremain','d3':''}
def parser_a(text): return text
def parser_b(text):
    if not text: raise ValueError('empty unsupported')
    return text.replace('é','e')
results={}
for name, parser in [('A',parser_a),('B',parser_b)]:
    rows=[]
    for identifier,text in fixtures.items():
        try:
            output=parser(text)
            rows.append({'id':identifier,'ran':True,'exact':output==text})
        except ValueError:
            rows.append({'id':identifier,'ran':False,'exact':False})
    results[name]=rows
assert sum(r['exact'] for r in results['A'])==3
assert sum(r['exact'] for r in results['B'])==1
assert len(results['B'])==3
print({name:{'exact':sum(r['exact'] for r in rows),'total':len(rows)} for name,rows in results.items()})
''', 'These are toy parser functions, not benchmarks of named products. Both see identical inputs and exact-preservation scoring. B changes the accented character and fails empty input; its failed run stays in the denominator. Exact equality is useful for this preservation criterion, but would be wrong if approved normalization were intended. Define that choice before running.', 'Expand to five representative inputs and compare real feasible candidates with pinned versions. Record timing separately from correctness, then apply offline operation as a hard constraint before weighted ranking. Do not copy these toy scores into a product recommendation.')

add('W10', '''
def classify(tags):
    # tags are manually annotated features, not a language-understanding system.
    topics=set(tags) & {'billing','shipping','account','product','other'}
    urgency='urgent' if 'compromise' in tags else 'normal'
    route=next(iter(topics)) if len(topics)==1 else 'review'
    return {'topics':sorted(topics),'urgency':urgency,'suggested_queue':route}
assert classify({'billing','account'})['suggested_queue']=='review'
assert classify({'account','compromise','polite'})['urgency']=='urgent'
assert classify(set())['suggested_queue']=='review'
print(classify({'billing','account','polite'}))
''', 'The input is an annotated feature set so the handling policy can be evaluated before NLP. Topic answers what kind of work; urgency answers its consequence and time sensitivity. Multiple material topics route to review instead of arbitrarily discarding one. A keyword detector added later will have its own errors and cannot inherit the correctness of these manually supplied tags.', 'Label 30 messages independently for topic, urgency and next allowed action. Include a polite compromise report, a negated keyword and a genuinely ambiguous message. Resolve annotation disagreements before comparing classifiers.')

add('W11', '''
labels=['billing','technical','review']
expected=['billing','billing','technical','technical']
predicted=['billing','technical','technical','urgent-refund-approved']
predicted=[p if p in labels else 'review' for p in predicted]
matrix={a:{b:0 for b in labels} for a in labels}
for gold,pred in zip(expected,predicted): matrix[gold][pred]+=1
metrics={}
for label in labels:
    tp=matrix[label][label]
    actual=sum(matrix[label].values())
    called=sum(matrix[row][label] for row in labels)
    metrics[label]={'recall':tp/actual if actual else None,'precision':tp/called if called else None,
                    'actual':actual,'predicted':called}
assert metrics['billing']['recall']==.5
assert metrics['technical']['precision']==.5
assert metrics['review']['recall'] is None
print({'matrix_rows_expected':matrix,'metrics':metrics})
''', 'Rows are expected classes; columns are predicted classes. Billing recall is one correct billing prediction out of two billing inputs. Technical precision is one correct technical prediction out of two technical predictions. No expected review cases means review recall is undefined, represented by None rather than a misleading perfect score. The unknown model label falls back to review and cannot authorize a refund.', 'Run a majority-only baseline on an imbalanced 30-message dataset. Report per-class support alongside precision and recall. Explain which direction of error needs a review policy change rather than another prompt patch.')

add('W12', '''
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as folder:
    path=Path(folder)/'queue.sqlite'; db=sqlite3.connect(path)
    db.executescript('CREATE TABLE items(id TEXT PRIMARY KEY, message TEXT, topic TEXT, version INT); CREATE TABLE deliveries(id TEXT); CREATE TABLE corrections(id TEXT, old TEXT, new TEXT);')
    def receive(identifier,message):
        with db:
            db.execute('INSERT INTO deliveries VALUES(?)',(identifier,))
            db.execute("INSERT OR IGNORE INTO items VALUES(?,?,?,1)",(identifier,message,'unresolved'))
    receive('t4','charged twice'); receive('t4','charged twice')
    def correct(identifier,version,topic):
        with db:
            old=db.execute('SELECT topic FROM items WHERE id=? AND version=?',(identifier,version)).fetchone()
            if old is None: return 'conflict'
            changed=db.execute('UPDATE items SET topic=?,version=version+1 WHERE id=? AND version=?',(topic,identifier,version)).rowcount
            if changed!=1: return 'conflict'
            db.execute('INSERT INTO corrections VALUES(?,?,?)',(identifier,old[0],topic))
        return 'saved'
    assert correct('t4',1,'billing')=='saved' and correct('t4',1,'technical')=='conflict'
    db.close(); db=sqlite3.connect(path)
    assert db.execute('SELECT count(*) FROM items').fetchone()[0]==1
    assert db.execute('SELECT count(*) FROM deliveries').fetchone()[0]==2
    assert db.execute('SELECT old,new FROM corrections').fetchone()==('unresolved','billing')
    db.close()
print('two deliveries, one durable work item, one correction; stale review blocked')
''', 'Receipt and classification are separated: inputs enter unresolved even when a classifier is unavailable. Every delivery is recorded, while a stable input ID deduplicates work. The transaction records correction history alongside the current state. This single-reviewer prototype has no user authentication; add reviewer scope before exposing it over HTTP. A reused event ID with different content also requires explicit conflict handling.', 'Receive an event while the fake classifier raises an error; reopen the database and prove the original message remains queued. Add a content digest so a repeated ID with changed text raises a conflict instead of silently losing the change.')

add('W13', '''
facts={'f1':'CSV export','f2':'local drafts','f3':'human review before export'}
outline=[{'sentence':'Keep drafts locally.','facts':['f2']},
         {'sentence':'Review a draft, then export CSV.','facts':['f1','f3']}]
assert all(all(i in facts for i in line['facts']) for line in outline)
unsupported={'sentence':'Guaranteed jobs for every graduate.','facts':[]}
assert not unsupported['facts']
print({'audience':'first-time instructor','task':'review and export a draft',
       'outline':outline,'excluded':unsupported['sentence']})
''', 'The brief starts with a reader’s task, then maps draft claims to approved facts. Fact IDs provide traceability, not automated truth: a sentence can cite f1 while still inventing cloud sync. A reviewer must compare the sentence with the actual fact text. The unsupported employment promise is excluded rather than softened into another unmeasured result.', 'Write ten permitted fact IDs and an outline that enables a real task. Ask for a fabricated testimonial in a test brief and record the rejection. Do not classify unsupported statistics as creative tone.')

add('W14', '''
# Explicit sentence IDs let a reviewer reject a specific unsupported assertion.
initial=['Choose your draft.','Guaranteed jobs.','Export CSV.']
allowed={'Choose your draft.','Review its source facts.','Export CSV.'}
required={'Choose your draft.','Review its source facts.','Export CSV.'}
def rubric(draft):
    return {'unsupported':[s for s in draft if s not in allowed],
            'missing':sorted(required-set(draft))}
def revise(draft):
    retained=[s for s in draft if s in allowed]
    if 'Review its source facts.' not in retained:
        retained.insert(1,'Review its source facts.')
    return retained
versions=[initial]
for _ in range(2):
    findings=rubric(versions[-1])
    if not any(findings.values()): break
    versions.append(revise(versions[-1]))
assert len(versions)==2 and rubric(versions[-1])=={'unsupported':[],'missing':[]}
assert versions[0]==initial
print({'before':rubric(initial),'after':rubric(versions[-1]),'revisions':len(versions)-1})
''', 'This is a closed-set, deterministic rubric over known sentences, not a general factuality detector. It finds two different defects: an unsupported promise and a missing review step. One revision removes the first and restores the second while preserving the original for comparison. The loop has a bound and a success condition; a real reviewer still checks readability and task completion.', 'Add an unresolved factual dispute that the allowed set cannot settle. Stop after two rounds and route to a human instead of declaring success. Test whether a shorter draft that drops the review step passes style but fails task completeness.')

add('W15', '''
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib, json
def digest(text): return hashlib.sha256(text.encode()).hexdigest()
with TemporaryDirectory() as folder:
    root=Path(folder); audit=[]
    approval={'digest':digest('Reviewed draft A'),'destination':'preview.txt'}
    def publish(text,destination):
        if digest(text)!=approval['digest'] or destination!=approval['destination']:
            return 'needs_review'
        target=root/destination
        if target.exists() and target.read_text()==text: return 'already_published'
        target.write_text(text,encoding='utf-8')
        audit.append({'event':'published','digest':digest(text)})
        return 'published'
    assert publish('Edited B','preview.txt')=='needs_review'
    assert publish('Reviewed draft A','other.txt')=='needs_review'
    assert publish('Reviewed draft A','preview.txt')=='published'
    assert publish('Reviewed draft A','preview.txt')=='already_published'
    (root/'preview.txt').unlink(); audit.append({'event':'withdrawn','digest':approval['digest']})
    assert [row['event'] for row in audit]==['published','withdrawn']
print('exact content and destination approved; duplicate suppressed; withdrawal recorded locally')
''', 'Approval covers both bytes and destination. An edited date changes the digest and needs review. Repeating the same approved content is recognized instead of producing another publication record. Withdrawal removes only the local mock artifact and retains an audit event. This example has no real external publisher, durable authorization store or concurrent workers; do not infer those capabilities.', 'Persist the manifest and audit in your application. Keep a previous approved version, withdraw a mistaken revision and restore only a specifically approved version. Record the difference between retraction and erasing publication history.')

add('W16', '''
scenarios=[
 {'id':'normal','path':['input','draft','review','save','export']},
 {'id':'missing','path':['input','needs_review','save']},
 {'id':'failure','path':['input','generation_failed','retry']},
 {'id':'reload','path':['read_saved','show_reviewed_version']},
 {'id':'other_owner','path':['authenticate','deny_read']},
]
included={'text_input','draft_table','revision_save','reviewed_csv'}
excluded={'live_recording','calendar_send','OCR'}
assert not (included & excluded)
assert len({s['id'] for s in scenarios})==5
assert any('generation_failed' in s['path'] for s in scenarios)
print({'selected':'meeting action register','scenarios':[s['id'] for s in scenarios],
       'manual':'transcript annotation','fake':'extraction adapter','real':'local save and CSV'})
''', 'The scope names a complete student-visible path and five acceptance scenarios. Dependency labels identify what is manually annotated, fake, or actually implemented; they prevent a prototype from masquerading as live transcription. Listing scenarios is planning evidence, not proof they passed. The next session must collect observations through the actual UI and server.', 'Turn each path into Given/When/Then with fixture ID, actor, exact observable result and evidence file. Defer an integration that does not improve any of these five scenarios and explain its cost to completing the slice.')

add('W17', '''
import sqlite3
from tempfile import TemporaryDirectory
from pathlib import Path
with TemporaryDirectory() as folder:
    path=Path(folder)/'actions.sqlite'; db=sqlite3.connect(path)
    db.execute('CREATE TABLE actions(id TEXT PRIMARY KEY,owner TEXT,due TEXT,version INT)')
    with db: db.execute('INSERT INTO actions VALUES(?,?,?,?)',('a2','acme','2026-10-23',2))
    def save(actor, expected, due):
        with db:
            changed=db.execute('UPDATE actions SET due=?,version=version+1 WHERE id=? AND owner=? AND version=?',(due,'a2',actor,expected)).rowcount
        return 200 if changed else 409
    assert save('acme',2,'2026-10-24')==200
    assert save('acme',2,'2026-10-25')==409
    db.close(); db=sqlite3.connect(path)
    assert db.execute('SELECT due,version FROM actions WHERE id=? AND owner=?',('a2','acme')).fetchone()==('2026-10-24',3)
    assert db.execute('SELECT due FROM actions WHERE id=? AND owner=?',('a2','other')).fetchone() is None
    db.close()
print('durable due-date correction; stale save rejected; cross-owner read absent')
''', 'The store contract connects scoped identity, revision-aware write and durable readback. Reopening the database is stronger than reading a React variable, but still does not test HTTP or a browser. The 409 return is an application simulation; your real API must distinguish inaccessible IDs without leaking existence and convert true stale edits into a documented conflict response.', 'Wire these invariants into your own browser-to-API path. Change a due date, reload, restart the service and read it again. Stop the API during a save and verify retained input plus an error, never a false “saved” label.')

add('W18', '''
projects=['extraction','meeting','research','triage','content','app']
required={'input','output','evaluation','failure','limitation','setup'}
portfolio={name:{field:'evidence/'+name+'/'+field for field in required} for name in projects}
del portfolio['research']['failure']
gaps={name:sorted(required-set(records)) for name,records in portfolio.items() if required-set(records)}
assert gaps=={'research':['failure']}
print({'coverage_gaps':gaps,'claim':'synthetic prototypes; no client results established'})
''', 'The index checks presence of named evidence references, not whether those files exist or support the claim. The missing research failure is an honest gap that should narrow the portfolio claim until supplied. Each project needs a concrete input and limitation, and the integrated app needs fresh setup evidence. The final review must open the referenced files and reproduce a representative path.', 'Replace placeholder paths with real files from all six studios. Ask a peer to reproduce the weakest project. Record a failed example and the correction it motivated; do not replace it with a success-only screenshot.')

from .container_lab import FILES
# The printed manifest is deterministic; Docker is a separate explicit exercise.
add('B19', '''
from pathlib import Path
import json
FILES = ''' + pformat(FILES,sort_dicts=False,width=90) + '''
root=Path('container-lab')
for name,text in FILES.items():
    path=root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_text(encoding='utf-8')!=text:
        raise RuntimeError('Refusing to overwrite edited file: '+name)
    path.write_text(text,encoding='utf-8')
print('Created complete container-lab: '+', '.join(sorted(FILES)))
''', 'This file creates every source file for a small DRF/PostgreSQL/Nginx experiment. Inspect the generated files before building. The deliberately plain browser page isolates network and persistence concepts; it is not a replacement for your capstone React interface. The database port stays private, the browser uses relative /api URLs, and Nginx resolves backend on the container network. A PostgreSQL SELECT backs readiness. Named volume lab-data preserves records. Credentials enter at runtime. This unauthenticated, loopback-only synthetic lab uses table creation in the handler solely to remain self-contained; your capstone must use authenticated owner scopes and Django migrations.', 'Run the Docker procedure below, save a unique synthetic draft, replace the backend container and read it again. Then stop the database and check that /api/health/ returns 503. Record HTTP status and actual record ID; creating files or building an image alone does not pass the exercise.')
