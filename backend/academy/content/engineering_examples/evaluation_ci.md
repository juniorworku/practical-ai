## Put repeatable checks into CI

Save the complete evaluation_suite.py from session 26 at the root of your own test repository. Save the following workflow as `.github/workflows/evaluation.yaml`. This job has no provider credentials and runs on pull requests. It executes the deterministic contract baseline to check the harness and expected labels, then retains the report even when a check fails. A green job is a harness regression result; it does not certify the candidate model, semantic quality, deployment or scale.

```yaml
name: Evaluation contract regression
on: [push, pull_request]
permissions:
  contents: read
jobs:
  contract-checks:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: Execute concrete contract cases
        run: python evaluation_suite.py --output fixture-report.json
      - name: Retain case-level evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: contract-evidence
          path: fixture-report.json
          retention-days: 7
```

Record the tested action revisions and pin immutable commit SHAs in your production workflow. Never expose provider or connector secrets to untrusted pull-request code. Add a negative regression test that deliberately changes one critical expected decision: the harness must return a nonzero exit status, retain the failed case and make CI fail. A suite that always turns green cannot establish its gate behavior.

## Candidate evaluation is a separate controlled job

For the actual application, use the harness's HTTP target mode against an authenticated test revision. Start a synthetic application in the job or select a private test deployment by immutable release ID. Keep model/prompt/parser/context/dataset/judge revisions in the report artifact. Set the target token from a protected CI environment, authorize the endpoint and enforce an overall spend/request/deadline limit at the application before running. The harness's four-request semaphore bounds simultaneous attempts, not provider tokens or spend.

Use the exact same held-out cases for baseline and candidate. The required response contract appears in session 26; expected labels stay outside the request. HTTP timeouts, wrong schemas, owner errors and unapproved effects remain failures. Check the intended release ID before interpreting results; evaluating a previous server revision cannot validate a new commit.

The automated report starts with zero semantic reviews. Add a versioned review artifact mapping case IDs to claim-level support, relevance and reviewer/judge disagreement. Mechanical pass rate, reviewed acceptance, critical failures, latency percentiles and all-attempt spend are separate release fields. Block promotion on a critical failure or missing mandatory evidence rather than averaging it away. Retain the old candidate manifest so rollback and subsequent comparison refer to the exact same system.

## Your change and failure experiment

Wire your application's real adapter into the candidate job. Inject a denied-owner request and a timeout, verify the job fails, then restore correct behavior and rerun. Change only the prompt revision and verify the release fingerprint changes. Explain why the offline workflow can run on every PR while credentialed semantic evaluation needs a separately bounded, trusted environment. Keep untested production claims out of the release decision.
