import subprocess,sys,shutil
assert shutil.which(sys.executable) is not None
ok=subprocess.run([sys.executable,'-I','-c',"print('ready')"],capture_output=True,text=True,check=False)
bad=subprocess.run([sys.executable,'-I','-c',"import sys;print('invalid input',file=sys.stderr);sys.exit(2)"],capture_output=True,text=True,check=False)
assert ok.returncode==0 and ok.stdout.strip()=='ready'
assert bad.returncode==2 and bad.stderr.strip()=='invalid input' and bad.stdout==''
print('tool found; success=0; deliberate failure=2 with separate stderr')

# Bounded exercise variation
result=subprocess.run([sys.executable,'-I','-c','raise SystemExit(3)'],check=False)
assert result.returncode==3
print("Exercise variation: PASS")
