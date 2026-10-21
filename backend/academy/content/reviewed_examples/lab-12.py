import subprocess,sys
SCRIPT="import sys; checks={'scope':sys.argv[1]!='broken','citations':True};sys.exit(0 if all(checks.values()) else 1)"
ok=subprocess.run([sys.executable,'-I','-c',SCRIPT,'good'])
bad=subprocess.run([sys.executable,'-I','-c',SCRIPT,'broken'])
assert ok.returncode==0 and bad.returncode==1
print('passing gate exits 0; injected critical failure exits 1')

# Bounded exercise variation
assert bad.returncode!=0 and ok.returncode==0
print("Exercise variation: PASS")
