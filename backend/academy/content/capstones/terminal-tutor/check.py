"""Fresh-process evidence, failure, stale-source and ownership checks."""
import json,subprocess,sys,tempfile
from pathlib import Path
TUTOR=Path(__file__).with_name('tutor.py').resolve()
def cli(action,root):return subprocess.run([sys.executable,str(TUTOR),action,str(root)],text=True,capture_output=True)
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder)/'scratch'
 assert cli('init',root).returncode==0
 assert cli('init',root).returncode==2
 ran=cli('run',root);assert ran.returncode==0 and json.loads(ran.stdout)['exit_code']==0
 resumed=cli('resume',root);assert resumed.returncode==0 and json.loads(resumed.stdout)['evidence_status']=='passed_local_checks'
 source=root/'exercise.py';original=source.read_text();source.write_text(original+'\nassert False, "deliberate student defect"\n')
 stale=cli('resume',root);assert stale.returncode==2 and 'stale_evidence' in stale.stderr
 failed=cli('run',root);assert json.loads(failed.stdout)['exit_code']!=0
 assert json.loads(cli('resume',root).stdout)['evidence_status']=='failed_or_timed_out'
 source.write_text('while True: pass\n')
 timed=cli('run',root);assert timed.returncode==1 and json.loads(timed.stdout)['timed_out']
 assert json.loads(cli('resume',root).stdout)['evidence_status']=='failed_or_timed_out'
 source.write_text(original);assert cli('run',root).returncode==0
 source.unlink();outside=Path(folder)/'outside.py';outside.write_text("print('outside synthetic fixture')\n");source.symlink_to(outside)
 assert cli('run',root).returncode==2
 source.unlink();source.write_text(original)
 policy=root/'instructions.json';data=json.loads(policy.read_text());data['permitted_file']='../private.py';policy.write_text(json.dumps(data))
 assert cli('run',root).returncode==2
 assert cli('resume',root).returncode==2
 assert len((root/'resume.json').read_text())<1000
print('PASS: new workspace, fresh interpreter, observed exit/output, resumption, stale source rejection, retained failure, actual timeout, denied symlink and denied instruction expansion; no external tutor or hidden shell required')
