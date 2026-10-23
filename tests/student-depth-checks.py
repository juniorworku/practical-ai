"""The learner's acceptance runner must preserve failed evidence, not just success."""
import importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for slug in ['ai-agent-bootcamp','ai-workshops','ai-engineering-12-week']:
    spec=importlib.util.spec_from_file_location('check',ROOT/'backend/academy/content/capstones'/slug/'check.py')
    check=importlib.util.module_from_spec(spec);spec.loader.exec_module(check)
    with tempfile.TemporaryDirectory() as folder:
        output=Path(folder)/'observed.json';output.write_text('{"completed":true,"old":"do not retain"}')
        check.call=lambda *args,**kwargs:(200,{'ready':False})
        try:check.check('http://fixture.invalid','fixture',output)
        except AssertionError:pass
        else:raise AssertionError('failed readiness reported success')
        report=json.loads(output.read_text())
        assert report['completed'] is False and report['error_type']=='AssertionError'
        assert report['checks']==[{'case':'database_readiness','passed':False}]
        assert 'old' not in report
        def unavailable(*args,**kwargs):raise OSError('fixture unavailable')
        check.call=unavailable
        try:check.check('http://fixture.invalid','fixture',output)
        except OSError:pass
        else:raise AssertionError('dependency failure hidden')
        assert json.loads(output.read_text())['error_type']=='OSError'
print('PASS:3 published acceptance runners retain assertion and dependency failures, replacing stale success')
