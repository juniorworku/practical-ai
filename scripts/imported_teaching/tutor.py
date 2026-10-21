from .specs import SPECS

def tutor(n,title,term,explanation,trace,code,task,patch,diagnosis):
    SPECS[f'terminal-{n:02}']=dict(title=title,term=term,explanation=explanation,trace=trace,code=code.strip(),task=task,patch=patch.strip(),diagnosis=diagnosis)
tutor(1,'Create and inspect an isolated learning workspace','Working directory and path ownership',
'The working directory is the base for relative paths. A command that writes exercises/answer.py acts inside whichever folder the process actually uses. Begin in a new scratch directory, inspect its absolute path and create only your own files. Keep application databases and credentials out of this workspace. A temporary directory makes this example repeatable without assuming a particular Downloads folder.',
'The code creates a fresh workspace, writes one exercise file and lists its relative path. It never changes your app or depends on a missing downloadable tutor ZIP.',
'''
import tempfile
from pathlib import Path
with tempfile.TemporaryDirectory(prefix='tutor-student-') as folder:
    root=Path(folder).resolve();exercises=root/'exercises';exercises.mkdir()
    (exercises/'answer.py').write_text("print('hello learner')\\n")
    names=sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())
    assert names==['exercises/answer.py']
    assert (exercises/'answer.py').resolve().is_relative_to(root)
print('workspace contains only exercises/answer.py; app untouched')
''','Add a notes file inside the same temporary workspace and verify it stays below the workspace root.',
"# Repeat with a fresh workspace so the earlier temporary directory need not exist.\nwith tempfile.TemporaryDirectory(prefix='tutor-notes-') as folder:\n    root=Path(folder).resolve();note=root/'NOTES.md';note.write_text('next: test one boundary')\n    assert note.resolve().is_relative_to(root) and note.read_text().startswith('next:')",
'If a relative path points inside the app, stop and inspect the working directory before writing. The Terminal Tutor command box is stateless simulation; it cannot create this real file. Run this example in your own terminal.')
tutor(2,'Verify tools, permissions and process exits','Executable discovery and exit status',
'Finding an executable, running its version command and trusting it with file access are separate checks. Use an explicit executable path when launching a known interpreter. Capture exit status, stdout and stderr independently: an error message on stderr does not by itself define success. A tutor can explain commands without being authorized to run them. No external coding agent is required for these lessons.',
'The example launches the current Python interpreter with a successful program and a deliberately failing one. The failure prints to stderr and exits two; the caller inspects the code rather than guessing from text.',
'''
import subprocess,sys,shutil
assert shutil.which(sys.executable) is not None
ok=subprocess.run([sys.executable,'-I','-c',"print('ready')"],capture_output=True,text=True,check=False)
bad=subprocess.run([sys.executable,'-I','-c',"import sys;print('invalid input',file=sys.stderr);sys.exit(2)"],capture_output=True,text=True,check=False)
assert ok.returncode==0 and ok.stdout.strip()=='ready'
assert bad.returncode==2 and bad.stderr.strip()=='invalid input' and bad.stdout==''
print('tool found; success=0; deliberate failure=2 with separate stderr')
''','Launch another process exiting three and verify the caller does not report it as successful.',
"result=subprocess.run([sys.executable,'-I','-c','raise SystemExit(3)'],check=False)\nassert result.returncode==3",
'A working version command proves the executable starts, not that a tutor loaded instructions or that it may read private files. Inspect the installed host permissions separately if you choose to use one; this course does not install or authenticate it.')
tutor(3,'Learn one concept, predict, then implement','Prediction before execution',
'A useful tutoring loop teaches one mechanism, asks you to predict a result, then lets you implement a bounded change. Here slicing keeps the first n evidence records without changing the original list. Python [:0] is empty; a negative n would mean drop items from the end, which is not a valid capacity policy. Validate capacity before slicing.',
'The selector returns the first two source IDs and leaves the original three-item list intact. A negative capacity raises instead of silently taking all but the last item.',
'''
def select(ids,capacity):
    if type(capacity) is not int or capacity<0: raise ValueError('capacity')
    return ids[:capacity]
ids=['p1','p2','p3']
assert select(ids,2)==['p1','p2'] and ids==['p1','p2','p3']
try: select(ids,-1)
except ValueError: pass
else: raise AssertionError('negative capacity accepted')
print('bounded evidence selection; original input preserved')
''','Predict and then test zero capacity and a capacity larger than the input length.',
"assert select(ids,0)==[]\nassert select(ids,10)==ids and select(ids,10) is not ids",
'If you cannot explain the negative case, return to slice semantics before adding an AI API. Ask a human or optional tutor for the smallest hint, not a full replacement implementation.')
tutor(4,'Read, run and change a complete local example','Entry point, inputs and side effects',
'Before running unfamiliar code, identify its entry point, dependencies, file writes and network calls. An entry guard runs main only when the file is executed directly. Importing a module should not start a server or send a model request. The following complete module has a pure quote function and a guarded CLI entry point.',
'The temporary module is executed as a subprocess and prints a synthetic policy. It is then imported and inspected without running its main function. No checkout or external source is needed.',
'''
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
''','Change the policy string in a fresh module to 7 days and verify direct execution prints the new value.',
"with tempfile.TemporaryDirectory() as folder:\n    path=Path(folder)/'policy.py';path.write_text(SOURCE.replace('14 days','7 days'))\n    result=subprocess.run([sys.executable,'-I',str(path)],capture_output=True,text=True,check=True)\n    assert result.stdout.strip()=='7 days'",
'If the old output remains, check which file and interpreter you executed before editing the test. A successful import does not exercise a guarded CLI path, and a successful CLI does not test HTTP behavior.')
tutor(5,'Recall, reproduce and debug with small hints','A counterexample reveals the boundary',
'Recall requires producing an explanation before seeing it. Debugging begins with a reproducible counterexample, not a guessed patch. A citation must belong to the evidence actually retrieved; a nonempty string is insufficient. Predict the buggy result, run it, then repair membership while preserving the successful case.',
'The buggy validator accepts invented because it only tests truthiness. The repaired validator checks exact membership and rejects that counterexample.',
'''
def buggy(citation,allowed): return bool(citation)
assert buggy('invented',{'p1'})  # Reproduces the defect; not desired behavior.
def valid(citation,allowed): return citation in allowed
assert valid('p1',{'p1'})
assert not valid('invented',{'p1'})
assert not valid('',{'p1'})
print('defect reproduced; membership repair passes positive and counterexample')
''','Add a second allowed source and verify it passes without allowing an unrelated source.',
"assert valid('p2',{'p1','p2'})\nassert not valid('p3',{'p1','p2'})",
'If you remove the invented-source assertion, the bug has been hidden rather than fixed. Use the three staged hints to inspect input, compare the invariant and finally examine the membership operation.')
tutor(6,'Distinguish agents, tools and protocols','Proposal versus execution',
'An agent proposes a next action. A tool is an application capability with a validated interface. A protocol carries discovery and calls between processes. They are separate deliverables: an in-memory function is not an MCP server. Start with a single read-only tool and prove denied calls cannot execute before studying the transport.',
'The proposal is dispatched through a fixed search allowlist. A write proposal is rejected and the call log retains only the permitted search.',
'''
calls=[]
def execute(name,query):
    if name!='search': raise ValueError('denied')
    if type(query) is not str or not query.strip(): raise ValueError('query')
    calls.append(name);return ['p1'] if query=='refund' else []
assert execute('search','refund')==['p1']
try: execute('delete','all')
except ValueError: pass
else: raise AssertionError('unsafe call executed')
assert calls==['search']
print('read-only application tool exercised; no protocol claim')
''','Run a supported search with no matching evidence and verify it returns an empty result, not an error or fabricated source.',
"assert execute('search','warranty')==[] and calls==['search','search']",
'A no-match result is a valid tool outcome; a denied operation is an authorization failure. Keep their trace categories distinct. Optional protocol study belongs after this application boundary is understood.')
tutor(7,'Inspect instruction packages before activation','Reference files are not active permissions',
'An instruction package contains text and possibly referenced resources. Merely downloading or reading it does not prove a host discovered or executed it. Inspect the manifest and relative resource paths, reject traversal outside the package and keep activation separate from review. These are course data, not instructions this application executes.',
'The package inspector resolves a resource below its own root and rejects ../escape.txt before reading it. It does not install a skill or alter any host configuration.',
'''
from pathlib import Path
import tempfile
def resource(root,name):
    resolved=(root/name).resolve()
    if not resolved.is_relative_to(root.resolve()): raise ValueError('outside package')
    return resolved.read_text()
with tempfile.TemporaryDirectory() as folder:
    root=Path(folder);(root/'guide.txt').write_text('teach one concept, then wait')
    assert resource(root,'guide.txt').startswith('teach one concept')
    try: resource(root,'../escape.txt')
    except ValueError: pass
    else: raise AssertionError('package boundary escaped')
print('referenced file inspected; traversal denied; nothing activated')
''','Test an absolute path outside the package and verify it is rejected without trying to read it.',
"with tempfile.TemporaryDirectory() as folder:\n    root=Path(folder)\n    try: resource(root,Path(folder).parent/'not-in-package.txt')\n    except ValueError: pass\n    else: raise AssertionError('absolute escape accepted')",
'Containment review prevents this simple path escape; it is not a sandbox for running unknown code and has filesystem race limitations. Host discovery must be observed in that host separately, not inferred from a copied directory.')
tutor(8,'Resume with evidence and a small context','Session state and retrieval practice',
'End a session with the source revision, artifact, observed result and one unresolved question. On resuming, first recall the mechanism without opening the solution, then verify files still match the saved revision. Keep a short context rather than dumping the whole project into an assistant. Local notes and academy progress are separate stores.',
'The session note stores a digest of the exercised code. It matches the original source and becomes stale when the source changes, signaling that cached guidance needs review.',
'''
import hashlib,json
def digest(text): return hashlib.sha256(text.encode()).hexdigest()
source="print('14 days')"
note={'lesson':'terminal-08','artifact':'policy.py','revision':digest(source),'observed':'14 days','revisit':'what happens without evidence?'}
loaded=json.loads(json.dumps(note))
assert loaded['revision']==digest(source)
assert loaded['revision']!=digest("print('7 days')")
assert len(json.dumps(loaded))<1000
print('small session note preserved; changed source invalidates saved revision')
''','Add a next-action field and keep the note under 1000 characters; explain what must be rerun after the source changes.',
"loaded['next']='rerun supported and missing-evidence cases';assert len(json.dumps(loaded))<1000",
'A saved note is evidence of what you recorded, not proof the code still passes. Re-run the targeted assertions after a revision change and keep failed observations instead of updating the note to assumed success.')
