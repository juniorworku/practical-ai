"""A resumable student workflow using actual commands and source-bound evidence."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def owned(root,name):
 root=root.resolve();path=root/name
 if path.is_symlink() or not path.resolve().is_relative_to(root):raise ValueError('path_not_owned')
 return path

def initialize(root):
 root=root.resolve();root.mkdir(parents=True,exist_ok=True)
 source=owned(root,'exercise.py');instructions=owned(root,'instructions.json')
 if source.exists() or instructions.exists():raise FileExistsError('existing workspace; inspect rather than overwrite')
 instructions.write_text(json.dumps({'permitted_file':'exercise.py','command':'current Python -I exercise.py','network':'none','instruction':'predict two source IDs, keep original unchanged, then assert an empty capacity'}))
 source.write_text("def select(ids,capacity):\n    if type(capacity) is not int or capacity<0: raise ValueError('capacity')\n    return ids[:capacity]\nids=['p1','p2','p3']\nassert select(ids,2)==['p1','p2']\nassert select(ids,0)==[]\nassert len(ids)==3\nprint('two sources selected; empty capacity; original retained')\n")
 return {'workspace':str(root),'source':'exercise.py','next':'inspect instructions, predict output, then run'}

def run(root):
 root=root.resolve();source=owned(root,'exercise.py');instructions=owned(root,'instructions.json');evidence=owned(root,'evidence.json')
 policy=json.loads(instructions.read_text())
 if policy['permitted_file']!='exercise.py' or policy['network']!='none' or policy['command']!='current Python -I exercise.py':raise ValueError('instruction_permission_changed')
 # No shell, arbitrary command, package activation or real agent authorization.
 # This fixed trusted exercise runs as your OS user; -I is not a security sandbox.
 started=time.perf_counter()
 try:
  result=subprocess.run([sys.executable,'-I',str(source)],cwd=root,capture_output=True,text=True,timeout=3)
  state={'exit_code':result.returncode,'stdout':result.stdout[:2000],'stderr':result.stderr[:2000],'timed_out':False}
 except subprocess.TimeoutExpired:state={'exit_code':None,'stdout':'','stderr':'timeout','timed_out':True}
 state.update(source_hash=digest(source),instruction_hash=digest(instructions),elapsed_ms=round((time.perf_counter()-started)*1000,3),command=[sys.executable,'-I','exercise.py'],workspace=str(root))
 evidence.write_text(json.dumps(state,indent=2));return state

def resume(root):
 root=root.resolve();state=json.loads(owned(root,'evidence.json').read_text())
 if state['workspace']!=str(root) or state['source_hash']!=digest(owned(root,'exercise.py')) or state['instruction_hash']!=digest(owned(root,'instructions.json')):raise ValueError('stale_evidence_rerun_required')
 note={'observed_exit':state['exit_code'],'source_hash':state['source_hash'],'instruction_hash':state['instruction_hash'],'next_action':'add a negative-capacity counterexample' if state['exit_code']==0 else 'diagnose failing command before continuing','evidence_status':'passed_local_checks' if state['exit_code']==0 else 'failed_or_timed_out'}
 text=json.dumps(note,indent=2)
 if len(text)>1000:raise ValueError('note_context_limit')
 owned(root,'resume.json').write_text(text);return note
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['init','run','resume']);parser.add_argument('workspace',type=Path);args=parser.parse_args()
 try:
  result={'init':initialize,'run':run,'resume':resume}[args.action](args.workspace);print(json.dumps(result,indent=2))
  if args.action=='run' and result.get('exit_code')!=0:raise SystemExit(1)
 except (ValueError,FileNotFoundError,FileExistsError) as error:print(str(error),file=sys.stderr);raise SystemExit(2)
