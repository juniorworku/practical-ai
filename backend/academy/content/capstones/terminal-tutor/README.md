# Complete evidence-bound Terminal Tutor project

Use Python 3.12 and a terminal. No external coding agent, cloud account or other program is required. This capstone assembles the workspace, process, counterexample, permission and resumption lessons into three real commands.

## Understand the state before execution

1. init creates a scratch folder, a complete exercise.py and an inspectable instructions.json. It refuses to overwrite an existing exercise. Read the files before running them. The exercise uses the selection function and assertions taught in guides 3–5.
2. owned rejects a symlinked child or a child resolving outside the selected folder. Path ownership checks do not make arbitrary Python safe. Run only this inspected exercise under your own account; -I isolates Python import configuration and is not an OS sandbox.
3. run launches the current Python interpreter with -I, one exact script path and no shell. It captures stdout, stderr, exit status and a three-second deadline. Failure is preserved in evidence.json and the command exits nonzero. The script records SHA-256 hashes of the actual source and instruction package, as taught by the source revision and package-inspection concepts.
4. resume reads the evidence in a new process. It compares source, instructions and workspace before trusting that evidence. Changed source or permissions require a rerun. A passing execution produces a small next-action note; a failed execution produces a diagnosis action, not a success claim. The note is capped at 1000 characters; it contains only synthetic task evidence.
5. The fixed instructions permit the exercise file only. They are teaching configuration, not host security enforcement. No arbitrary shell command, network grant or external agent installation is implemented by this tutor.

## Build, run and resume

Copy tutor.py and check.py from the inline course. From their directory:

```sh
python3 tutor.py init my-scratch
python3 tutor.py run my-scratch
python3 tutor.py resume my-scratch
python3 check.py
```

Expected: the generated exercise prints two sources selected; empty capacity; original retained. Evidence reports exit_code 0. A separately launched resume reports passed_local_checks and a next action. check.py tests new processes, stale source, retained assertion failure and denied instruction expansion.

## Student extension and feedback

Add a negative-capacity test to my-scratch/exercise.py. Before rerunning, resume must reject stale evidence. Run the new file, inspect its real exit code and resume again. Introduce an assert False temporarily: run must exit nonzero and resume must say failed_or_timed_out. Repair the assertion without deleting the original failed transcript. If you see old output, inspect the absolute workspace, source hash and interpreter before changing your expected answer. Submit the changed code, observed evidence and bounded resume note. Execution time is measured locally; model cost is unknown/not applicable and no live tutoring quality has been evaluated.
