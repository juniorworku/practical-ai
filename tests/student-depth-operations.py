"""Build the four inline capstones on fresh volumes, away from existing apps."""
import concurrent.futures,json,os,re,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SLUGS={'ai-agent-bootcamp':('bootcamp',8311),'ai-workshops':('workshops',8312),
       'ai-engineering-12-week':('engineering',8314),'genai-accelerator':('accelerator',8315)}
programs=[p for path in ['backend/academy/starter_curriculum.json','backend/academy/content/reviewed_workshop.json'] for p in json.loads((ROOT/path).read_text()) if p['slug'] in SLUGS]
report=[]
def http(port,path,token=None,data=None):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    request=urllib.request.Request(f'http://127.0.0.1:{port}'+path,headers=headers,data=json.dumps(data).encode() if data is not None else None)
    try:
        with urllib.request.urlopen(request,timeout=8) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as error:return error.code,json.load(error)
def wait(port,path):
    deadline=time.monotonic()+50
    while time.monotonic()<deadline:
        try:
            if http(port,path)[0]==200:return
        except (OSError,ValueError):pass
        time.sleep(.3)
    raise AssertionError('readiness did not recover')
for program in programs:
    slug=program['slug'];kind,port=SLUGS[slug];project='academy-depth-'+kind
    final=next(l['resources']['learning'] for l in program['lessons'] if l['resources']['learning'].get('capstone'))
    chapter=next(c['body'] for c in final['chapters'] if c['id']=='capstone-build')
    with tempfile.TemporaryDirectory(prefix=project+'-') as folder:
        folder=Path(folder)
        for name in final['capstone']['files']:
            if name=='README.md':continue
            code=re.findall(r'^### '+re.escape(name)+r'\n\n```[^\n]+\n(.*?)^```',chapter,re.M|re.S)[0]
            path=folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(code)
        # Only the host binding differs from the published project. Existing
        # learner services on 821x and academy/workshop data are untouched.
        (folder/'review-ports.yaml').write_text(f'services:\n  api:\n    ports: !override ["127.0.0.1:{port}:{8010 if kind=="accelerator" else 8000}"]\n')
        command=['docker','compose','-p',project,'-f','compose.yaml','-f','review-ports.yaml']
        def compose(*args,input=None):
            result=subprocess.run([*command,*args],cwd=folder,input=input,capture_output=True,timeout=300)
            if result.returncode:raise RuntimeError(result.stderr.decode()[-2500:])
            return result.stdout
        def run(*args,env=None):
            result=subprocess.run([sys.executable,*args],cwd=folder,capture_output=True,text=True,env={**os.environ,**(env or {})},timeout=90)
            if result.returncode:raise AssertionError(result.stdout+'\n'+result.stderr)
            return result.stdout
        try:
            print('BUILD inline files on fresh volume:',slug,flush=True)
            compose('up','-d','--build','--wait')
            if kind!='accelerator':
                run('check.py','--base',f'http://127.0.0.1:{port}','--kind',kind,'--output','observed.json')
                observed=json.loads((folder/'observed.json').read_text());assert observed['completed']
                path='/api/records/'+observed['draft_id']+'/';token='student-one';health='/api/health/'
                if kind=='engineering':
                    run('evaluate.py',env={'CAPSTONE_URL':f'http://127.0.0.1:{port}'})
                    evaluation=json.loads((folder/'evaluation-observed.json').read_text());assert evaluation['passed']==120
                    source='Refunds within 14 days. '+'Policy detail. '*23+'Opened items are excluded.'
                    assert http(port,'/api/documents/',token,{'source':'long-policy','text':source})[0]==201
                    result=http(port,'/api/ask/',token,{'input':'refunds'})[1]
                    assert 'Opened items are excluded.' in result['text']
                    assert http(port,'/api/documents/',token,{'source':'oversize','text':'Refunds '+'x'*700})[0]==201
                    result=http(port,'/api/ask/',token,{'input':'refunds'})[1]
                    assert result['status']=='needs_correction' and result['text'] is None
                if kind=='workshops':
                    text='Supplier: Studio\nQuantity: 2\nUnit price: 10.00\nCurrency: USD\nQuantity: 9'
                    result=http(port,'/api/ask/',token,{'input':text})[1]
                    assert result['status']=='needs_correction'
                    assert [s['line'] for s in result['field_evidence']['quantity']]==[2,5]
                database='capstone';query='SELECT id,owner,kind,payload FROM records ORDER BY id'
                checks=len(observed['checks'])
            else:
                output=run('check.py',env={'LAB_URL':f'http://127.0.0.1:{port}'})
                observed=json.loads(output);path='/documents/'+observed['document_id'];token='demo-one';health='/health'
                run('check_agent.py',env={'CAPSTONE_URL':f'http://127.0.0.1:{port}'})
                agent=json.loads((folder/'observed-agent.json').read_text());assert all(agent['checks'].values())
                assert 'Unused items only' in observed['grounded_fixture']['answer']
                database='accelerator_lab';query='SELECT id,org,state,digest,text FROM documents ORDER BY id; SELECT document_id,position,text FROM chunks ORDER BY document_id,position'
                checks=agent['checks']
            before=http(port,path,token);assert before[0]==200
            compose('up','-d','--force-recreate','--wait','api')
            assert http(port,path,token)==before
            compose('stop','db')
            try:assert http(port,health)[0]==503
            finally:compose('start','db')
            wait(port,health);assert http(port,path,token)==before
            dump=compose('exec','-T','db','pg_dump','-U','learner','-d',database,'-Fc')
            restored='student_depth_restore'
            compose('exec','-T','db','createdb','-U','learner',restored)
            compose('exec','-T','db','pg_restore','-U','learner','-d',restored,input=dump)
            original=compose('exec','-T','db','psql','-U','learner','-d',database,'-At','-c',query)
            copy=compose('exec','-T','db','psql','-U','learner','-d',restored,'-At','-c',query)
            assert original==copy and original
            report.append({'program':slug,'inline_build':True,'fresh_database':True,'acceptance_checks':checks,
                           'recreated_api_same_id':True,'db_outage_503':True,'db_recovered_same_id':True,'pg_restore_exact_rows':True,
                           'extra_checks':'120-case actual HTTP evaluation and exception/overflow' if kind=='engineering' else 'duplicate evidence spans' if kind=='workshops' else 'actual persisted HTTP and MCP with exception retained' if kind=='accelerator' else 'bounded proposals and concurrent local approval'})
            print('PASS end-to-end, replacement, outage and restore:',slug,flush=True)
        finally:
            compose('down','--volumes','--remove-orphans')
(ROOT/'docs/student-depth-operations.json').write_text(json.dumps(report,indent=2)+'\n')
