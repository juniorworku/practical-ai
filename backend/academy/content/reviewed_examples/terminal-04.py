import tempfile,subprocess,sys,importlib.util
from pathlib import Path
SOURCE="""def quote():
    return '14 days'
if __name__ == '__main__':
    print(quote())
"""
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'policy.py';path.write_text(SOURCE)
    run=subprocess.run([sys.executable,'-I',str(path)],capture_output=True,text=True,check=True)
    assert run.stdout.strip()=='14 days'
    spec=importlib.util.spec_from_file_location('policy_exercise',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.quote()=='14 days'
print('entry point executed; module imported without starting an application')

# Bounded exercise variation
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'policy.py';path.write_text(SOURCE.replace('14 days','7 days'))
    result=subprocess.run([sys.executable,'-I',str(path)],capture_output=True,text=True,check=True)
    assert result.stdout.strip()=='7 days'
print("Exercise variation: PASS")
