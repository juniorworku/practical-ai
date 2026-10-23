"""Complete primary variations and the failure experiments assigned with them."""
from pathlib import Path
EXAMPLES=Path(__file__).resolve().parent/'python_ai_examples'
def solution(number):
    code=(EXAMPLES/f'{number:02}.py').read_text()
    if number==1:
        code=code.replace("        if not isinstance(self.query", "        if self.owner not in {'team-a','team-b'}:\n            raise ValueError('unknown owner')\n        if not isinstance(self.query")
        code+='''
for owner, query in [('outsider','refund'), ('team-a',[]), ('team-a','x'*2001), ('team-a','   ')]:
    try: Request(owner,query)
    except ValueError: pass
    else: raise AssertionError('invalid request accepted')
assert len(Request('team-a','x'*2000).query)==2000
'''
    elif number==2:
        code=code.replace('def records(chunks, max_line=200):','def records(chunks, max_line=200):\n    count=0').replace('                yield json.loads(line)','                count+=1\n                if count>2: raise ValueError("record count exceeded")\n                yield json.loads(line)')
        code+='''
for chunks, message in [([b'{}\\n{}\\n{}\\n'],'record count exceeded'),
                        ([b'{"x":1}'],'truncated stream'),
                        ([b'{broken}\\n'],'Expecting property'),
                        ([b'x'*201+b'\\n'],'line budget exceeded')]:
    try: list(records(chunks))
    except ValueError as error: assert message in str(error), str(error)
    else: raise AssertionError('invalid stream accepted')
'''
    elif number==3:
        code=code.replace('    queue = asyncio.Queue', "    if type(workers) is not int or not 1 <= workers <= 4: raise ValueError('worker bound')\n    queue = asyncio.Queue")
        code+='''
async def extension():
    output, peak = await map_bounded(list(range(100)),workers=3)
    assert output==[n*2 for n in range(100)] and peak<=3
    for workers in [0,5,True]:
        try: await map_bounded([1],workers)
        except ValueError: pass
        else: raise AssertionError('bad worker bound')
    entered=asyncio.Event(); active=0
    async def failing(value):
        nonlocal active
        if value==1:
            await entered.wait()
            raise ValueError('selected input')
        active+=1; entered.set()
        try: await asyncio.Event().wait()
        finally: active-=1
    try: await map_bounded(list(range(100)),workers=3,operation=failing)
    except ExceptionGroup as group:
        assert any(isinstance(e,ValueError) for e in group.exceptions)
    else: raise AssertionError('consumer failure hidden')
    assert active==0, 'a sibling survived TaskGroup exit'
asyncio.run(extension())
'''
    elif number==4:
        code+='''
async def extension():
    calls=[];cleaned=asyncio.Event()
    async def attempt(index):
        calls.append(index)
        if index==1: return 'retryable outcome'
        try: await asyncio.Event().wait()
        finally: cleaned.set()
    try:
        async with asyncio.timeout(.1):
            await attempt(1)
            await attempt(2)
    except TimeoutError:
        assert calls==[1,2] and cleaned.is_set()
    else: raise AssertionError('overall deadline absent')
    parent_cleaned=asyncio.Event();started=asyncio.Event()
    async def dependency():
        started.set()
        try: await asyncio.Event().wait()
        finally: parent_cleaned.set()
    task=asyncio.create_task(dependency())
    await started.wait();task.cancel()
    try: await task
    except asyncio.CancelledError: assert parent_cleaned.is_set()
    else: raise AssertionError('cancellation swallowed')
asyncio.run(extension())
'''
    elif number==5:
        code+='''
class Empty:
    async def answer(self,query,evidence):return Reply('',evidence['id'],None,None)
try: asyncio.run(application(Empty()))
except ProviderError: print('Empty provider result rejected')
else: raise AssertionError('empty response accepted')
assert asyncio.run(application(Fake())).input_tokens is None
'''
    elif number==6:
        code+='''
async def extension():
    calls=0
    async def unavailable():
        nonlocal calls
        calls+=1
        raise TransientRead('still unavailable')
    try: await retry_read(unavailable)
    except TransientRead: assert calls==3
    else: raise AssertionError('exhaustion became success')
    attempts=0
    async def unauthorized():
        nonlocal attempts
        attempts+=1
        raise PermissionError('denied')
    try: await retry_read(unauthorized)
    except PermissionError: assert attempts==1
    else: raise AssertionError('authorization became success')
asyncio.run(extension())
'''
    elif number==7:
        code+='''
rows.append({'id':'a0','owner':'a','text':'Refund window: 21 days.'})
assert [r['id'] for r in retrieve('a','refund window',rows)]==['a0','a1']
assert all(r['owner']=='a' for r in retrieve('a','refund window',rows))
# Two relevant policies are a conflict requiring a version policy or review;
# stable ordering alone does not determine which policy is authoritative.
'''
    elif number==8:
        code=code.replace('prompt_version, query):',"prompt_version, query, schema='schema-v1'):").replace('prompt_version, query]\n','prompt_version, query, schema]\n')
        code+='''
assert key('a','fixture-v1','source-v1','prompt-v1','refund?',schema='schema-v2') not in cache
assert key('a','fixture-v1','source-v1','prompt-v1','refund?',schema='schema-v1') in cache
# Counterexample: omitting source_version gives the same identity after a change.
def broken_key(owner,query):return (owner,query)
assert broken_key('a','refund?')==broken_key('a','refund?')
assert key('a','fixture-v1','source-v1','prompt-v1','refund?')!=key('a','fixture-v1','source-v2','prompt-v1','refund?')
'''
    elif number==9:
        code+='''
with tempfile.TemporaryDirectory() as folder:
    db=sqlite3.connect(Path(folder)/'rollback.sqlite3')
    try:
        db.execute('CREATE TABLE cache(owner TEXT, key TEXT, result TEXT, PRIMARY KEY(owner,key))')
        with db:db.execute('INSERT INTO cache VALUES(?,?,?)',('a','v1','original'))
        try:
            with db:db.execute('INSERT INTO cache VALUES(?,?,?)',('a','v1','replacement'))
        except sqlite3.IntegrityError:pass
        else:raise AssertionError('duplicate accepted')
        try:
            with db:
                db.execute('INSERT INTO cache VALUES(?,?,?)',('a','v2','uncommitted'))
                raise RuntimeError('synthetic failure')
        except RuntimeError:pass
        assert db.execute('SELECT result FROM cache').fetchall()==[('original',)]
    finally:db.close()
'''
    elif number==10:
        code=code.replace("('empty',None,None)]", "('empty',None,None),('unsupported',None,None)]").replace('== .75','== .8')
        code+='''
repaired=[(name,expected,expected if name=='isolation' else observed) for name,expected,observed in cases]
assert sum(expected==observed for _,expected,observed in repaired)/len(repaired)==1.0
assert [expected for _,expected,_ in repaired]==[expected for _,expected,_ in cases]
'''
    elif number==11:
        code=code.replace('import urllib.request','import urllib.request\nimport urllib.error').replace("    print('HTTP readiness contract:',result)","""    print('HTTP readiness contract:',result)
    try:urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/missing',timeout=2)
    except urllib.error.HTTPError as error:
        assert error.code==404
        error.close()
    else:raise AssertionError('unknown route accepted')""")
        code+='''
# Rebind the exact old port after close and serve nothing: the client must time out.
# A bound but non-listening socket also prevents another process from taking it.
import socket
with socket.socket() as stopped:
    stopped.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    stopped.bind(('127.0.0.1',server.server_port))
    try:urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/health',timeout=.2)
    except urllib.error.URLError:print('Stopped dependency correctly unavailable')
    else:raise AssertionError('stopped service reported ready')
'''
    else:
        code+='''
assert release_scope(Evidence(True,True,False,False,False))=='blocked'
# Build the complete project, then run test_pipeline.py, test_http.py and
# test_evaluate.py. This gate fixture alone is not a capstone implementation.
'''
    return code
