import subprocess,sys
executed=[]
for name,code in [('unit',0),('evaluation',1),('build',0)]:
    result=subprocess.run([sys.executable,'-c',f'raise SystemExit({code})'],check=False)
    executed.append(name)
    if result.returncode: break
assert executed==['unit','evaluation']
print('evaluation failure propagated; build did not execute')

# Bounded exercise variation
passed=[]
for name in ['unit','evaluation','build']:
    subprocess.run([sys.executable,'-c','raise SystemExit(0)'],check=True);passed.append(name)
assert passed[-1]=='build'
print("Exercise variation: PASS")
