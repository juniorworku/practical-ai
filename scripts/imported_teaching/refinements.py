from .specs import SPECS
# The exercise must require a meaningful executable change, not assert True or inspect a function's existence.
s=SPECS['lesson-21'];s['task']='Start a second local server and make a real request to /another-missing-path, verifying a 404 and its JSON error body.';s['patch']='''server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever);thread.start()
try:
    try: urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/another-missing-path')
    except urllib.error.HTTPError as error:
        assert error.code==404 and json.load(error)=={'error':'not_found'}
    else: raise AssertionError('unknown path succeeded')
finally: server.shutdown();thread.join();server.server_close()'''
s=SPECS['lesson-25'];s['task']='Add a fresh transaction test: fail ingestion halfway, retry successfully and replay once; verify exactly one document and one chunk.';s['patch']='''with sqlite3.connect(':memory:') as retry_db:
    retry_db.executescript('CREATE TABLE docs(id TEXT PRIMARY KEY); CREATE TABLE chunks(doc TEXT UNIQUE,text TEXT);')
    def retry_ingest(key,fail=False):
        with retry_db:
            inserted=retry_db.execute('INSERT OR IGNORE INTO docs VALUES (?)',(key,)).rowcount
            if inserted:
                if fail: raise RuntimeError('before chunk write')
                retry_db.execute('INSERT INTO chunks VALUES (?,?)',(key,'14 days'))
    try: retry_ingest('a',True)
    except RuntimeError: pass
    assert retry_db.execute('SELECT count(*) FROM docs').fetchone()[0]==0
    retry_ingest('a');retry_ingest('a')
    assert retry_db.execute('SELECT count(*) FROM docs').fetchone()[0]==1
    assert retry_db.execute('SELECT count(*) FROM chunks').fetchone()[0]==1'''
s=SPECS['lesson-57'];s['task']='Restore another fixture with two policy revisions into a fresh database and compare both IDs and text, not just row counts.';s['patch']='''source=sqlite3.connect(':memory:');restored=sqlite3.connect(':memory:')
try:
    source.execute('CREATE TABLE policy(id TEXT PRIMARY KEY,text TEXT)')
    source.executemany('INSERT INTO policy VALUES (?,?)',[('v1','14 days'),('v2','7 days')]);source.commit()
    source.backup(restored)
    expected=[('v1','14 days'),('v2','7 days')]
    assert restored.execute('SELECT id,text FROM policy ORDER BY id').fetchall()==expected
finally: source.close();restored.close()'''
s=SPECS['lesson-69'];s['task']='Implement an ownership-checking checkpoint loader and demonstrate it rejects a second owner before returning state.';s['patch']='''def resume_checkpoint(saved,authenticated_owner):
    if saved.get('owner')!=authenticated_owner: raise PermissionError('checkpoint owner')
    if saved.get('version')!=1: raise ValueError('checkpoint version')
    return saved['next']
assert resume_checkpoint(loaded,'one')=='verify'
try: resume_checkpoint(loaded,'two')
except PermissionError: pass
else: raise AssertionError('cross-owner checkpoint returned')'''
s=SPECS['lab-06'];s['task']='Add a separately persisted job fixture and verify a worker commits transformed content and ready together before reporting completion.';s['patch']='''with sqlite3.connect(':memory:') as variation_db:
    variation_db.execute('CREATE TABLE job(id TEXT PRIMARY KEY,state TEXT,chunk TEXT)')
    variation_db.execute("INSERT INTO job VALUES ('b','accepted',NULL)")
    with variation_db:
        variation_db.execute('UPDATE job SET state=?,chunk=? WHERE id=?',('ready','UNUSED ONLY','b'))
    assert variation_db.execute('SELECT state,chunk FROM job').fetchone()==('ready','UNUSED ONLY')'''
# Keep the same connection lifetime and transaction semantics in the complete runnable references.
import re
for s in SPECS.values():
    for field in ['code','patch']:
        text=s[field]
        if 'with sqlite3.connect(' in text:
            text=re.sub(r'with sqlite3.connect\((.*?)\) as (\w+):',r'with closing(sqlite3.connect(\1)) as \2, \2:',text)
            text='from contextlib import closing\n'+text
        s[field]=text
# Product-side operation contracts, not inference about a proposal's name.
s=SPECS['lab-15'];s['code']=s['code'].replace("evidence=[];trace=[]","evidence=[];trace=[];searched=False").replace("evidence=[{'id':'p1'", "searched=True\n            evidence=[{'id':'p1'").replace("elif action['name']=='finish':\n            if not evidence", "elif action['name']=='finish':\n            if not searched: return 'premature_finish',trace\n            if not evidence")
s['patch']+="\nassert run('refund',lambda q,e:{'name':'finish','id':'p1'})[0]=='premature_finish'"
SPECS['lesson-85']['title']='Connect a provider through a validated decision adapter'
# Empty evidence after a completed search must differ from 'no search has happened'.
s=SPECS['lab-15']
s['explanation']='Integrate a step budget, a validated read-only tool and source membership. Keep a history of observations: an empty history means no search occurred, while a history containing an empty search result means retrieval ran and found no support. The decision function can then finish with abstention rather than searching forever. The harness owns evidence, copies observations before handing them to an adapter and rejects a premature finish. This complete standard-library harness is scripted, not a live model.'
s['trace']='The normal run records one search observation and finishes with a known citation. The unknown topic records an empty search observation and then abstains. A malicious adapter proposing delete is denied before execution; a finish before any search is premature.'
s['code']='''from copy import deepcopy
def run(question,decide,max_steps=3):
    observations=[];trace=[]
    for step in range(max_steps):
        action=decide(question,tuple(deepcopy(observations)));trace.append(action['name'])
        if action['name']=='search':
            if type(action.get('query')) is not str or not action['query'].strip(): return 'invalid_arguments',trace
            evidence=[{'id':'p1','text':'14 days'}] if action['query']=='refund' else []
            observations.append(evidence)
        elif action['name']=='finish':
            if not observations: return 'premature_finish',trace
            evidence=observations[-1]
            if not evidence: return 'abstained',trace
            return ('completed' if action.get('id') in {e['id'] for e in evidence} else 'unsupported_citation'),trace
        else: return 'denied_action',trace
    return 'step_budget',trace

def scripted(question,observations):
    if not observations: return {'name':'search','query':question}
    hits=observations[-1]
    return {'name':'finish','id':hits[0]['id'] if hits else None}
assert run('refund',scripted)==('completed',['search','finish'])
assert run('warranty',scripted)==('abstained',['search','finish'])
assert run('refund',scripted,1)[0]=='step_budget'
assert run('refund',lambda q,o:{'name':'delete'})[0]=='denied_action'
print('scripted agent completed, abstained on empty search and denied unknown authority')'''
s['patch']='''def invented(question,observations):
    return {'name':'finish','id':'fake'} if observations else {'name':'search','query':question}
assert run('refund',invented)[0]=='unsupported_citation'
assert run('refund',lambda q,o:{'name':'finish','id':'p1'})[0]=='premature_finish'
def tamper(question,observations):
    if not observations: return {'name':'search','query':question}
    observations[-1].append({'id':'fake','text':'invented'})
    return {'name':'finish','id':'fake'}
assert run('refund',tamper)[0]=='unsupported_citation' '''
s['diagnosis']='If an unsupported topic keeps searching until step_budget, inspect whether the adapter can distinguish no search from an empty result. If a finish succeeds with a fabricated source, inspect evidence ownership and citation membership. Copy mutable observations before adapter calls; a shallow outer tuple alone does not isolate nested lists. These deterministic fixtures still do not evaluate a real model or transport deadline.'
s=SPECS['lab-15']
s['code']=s['code'].replace("    observations=[];trace=[]", "    if type(max_steps) is not int or not 1<=max_steps<=20: raise ValueError('step budget')\n    if type(question) is not str or not 3<=len(question)<=200: raise ValueError('question')\n    observations=[];trace=[]")
s['code']=s['code'].replace("        action=decide(question,tuple(deepcopy(observations)));trace.append(action['name'])", "        try: action=decide(question,tuple(deepcopy(observations)))\n        except TimeoutError: return 'provider_timeout',trace\n        if type(action) is not dict or type(action.get('name')) is not str: return 'invalid_decision',trace\n        trace.append(action['name'])")
s['code']=s['code'].replace("            if type(action.get('query')) is not str or not action['query'].strip(): return 'invalid_arguments',trace", "            if set(action)!={'name','query'} or type(action['query']) is not str or not 3<=len(action['query'].strip())<=200: return 'invalid_arguments',trace")
s['code']=s['code'].replace("        elif action['name']=='finish':\n            if not observations", "        elif action['name']=='finish':\n            if set(action)!={'name','id'} or not (action['id'] is None or type(action['id']) is str and 1<=len(action['id'])<=100): return 'invalid_arguments',trace\n            if not observations")
s['patch']+="\nassert run('refund',lambda q,o:None)[0]=='invalid_decision'\ndef timeout(q,o): raise TimeoutError('fixture')\nassert run('refund',timeout)[0]=='provider_timeout'\n"

# The discovery lab must practice its advertised boundary, not repeat the
# parallel-branch join from lesson 77. A real SDK execution follows inline.
SPECS['lab-19'].update(
 term='Discover a read-only contract before dispatch',
 explanation='Discovery describes a capability; it does not authorize every advertised operation. Start with a host-owned allowlist, inspect the discovered name and input contract, then validate each call independently. The pure Python specimen isolates these application rules. The complete MCP server/client chapter then runs actual initialization, discovery and calls over stdio; this dictionary registry alone is not an MCP transport.',
 trace='The host discovers search_policies with one bounded string argument. It accepts the known schema, returns the scoped synthetic policy for refund, returns an empty success for an unrelated topic, and rejects write tools or invalid arguments before execution.',
 code='''
ALLOWED={'search_policies'}
EXPECTED={'type':'object','required':['query'],'additionalProperties':False,
          'properties':{'query':{'type':'string','minLength':3,'maxLength':200}}}
CATALOG=[{'name':'search_policies','inputSchema':EXPECTED}]
POLICY={'id':'policy-1','text':'Refund window is 30 days','owner':'demo'}
def discover(catalog):
    accepted={}
    for tool in catalog:
        if tool.get('name') in ALLOWED and tool.get('inputSchema')==EXPECTED:
            accepted[tool['name']]=tool
    return accepted
def call(capabilities,name,arguments):
    if name not in ALLOWED or name not in capabilities: raise PermissionError('tool denied')
    if type(arguments) is not dict or set(arguments)!={'query'}: raise ValueError('arguments')
    query=arguments['query']
    if type(query) is not str or not 3<=len(query.strip())<=200: raise ValueError('query')
    return {'isError':False,'sources':[dict(POLICY)] if 'refund' in query.lower() else []}
known=discover(CATALOG)
assert set(known)=={'search_policies'}
assert call(known,'search_policies',{'query':'refund'})['sources'][0]['id']=='policy-1'
assert call(known,'search_policies',{'query':'warranty'})=={'isError':False,'sources':[]}
for name,args in [('delete',{'query':'refund'}),('search_policies',{'query':' '}),('search_policies',{'query':'refund','owner':'other'})]:
    try: call(known,name,args)
    except (ValueError,PermissionError): pass
    else: raise AssertionError('unsafe call executed')
assert discover([{'name':'search_policies','inputSchema':{'type':'string'}}])=={}
print('read-only discovery contract checked; calls validated; empty success distinguished')
'''.strip(),
 task='Advertise a delete tool beside the valid search tool and prove discovery cannot expand the host allowlist; the denied call must still fail.',
 patch="advertised=CATALOG+[{'name':'delete','inputSchema':EXPECTED}]\nassert set(discover(advertised))=={'search_policies'}\ntry: call(discover(advertised),'delete',{'query':'refund'})\nexcept PermissionError: pass\nelse: raise AssertionError('discovery granted write authority')\nassert ALLOWED=={'search_policies'}",
 diagnosis='The registry checks application contracts only. Run the complete embedded MCP client to observe real initialize/list_tools/call_tool/resource/error/shutdown behavior. A discovered description cannot grant write permission, an empty successful search is not a transport error, and source membership still does not establish semantic support for arbitrary answers.'
)
