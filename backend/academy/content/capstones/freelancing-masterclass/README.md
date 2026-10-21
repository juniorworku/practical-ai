# Complete simulated client engagement

The capstone is a coherent client delivery, not a claim that a real client signed off. Use Python 3.12; no third-party package, model account or another program is needed. The client/ files are complete synthetic artifacts, and engagement.py actually runs their pilot and recovery checks.

## Build the engagement in order

1. Read baseline.json: 40 items × (8−5) minutes − 30 maintenance minutes = 90 projected minutes/week. These are fictional assumptions; they are not observed ROI. Match the buyer and workflow to the discovery and baseline lessons 1–3.
2. Compare offer.json and scope.json from lessons 4–6. Every promise must be in scope and have an acceptance ID. Automatic publication, real hosting and factual client acceptance are explicitly excluded. A fixed estimate is not permission to expand scope.
3. Read data-policy.json and requests.csv from lessons 7–9. Only id, source and text are approved. policy-v1 permits a verbatim source draft. An empty source or unapproved revision routes to needs_source; no model fills the gap.
4. acceptance.json fixes expected outcomes before the pilot runs. engagement.py opens a fresh SQLite file, writes drafts, closes it and reads back independently. It compares actual statuses and text with those unchanged cases. A passed schema or exact string is mechanical evidence, not general semantic review.
5. changes.json and support.json carry lessons 10–15 forward: reject an automatic-publication scope change, name manual fallback and assign maintenance/retention responsibility. The script creates a real backup, restores into a distinct file and compares rows through fresh connections. It does not simply trust a supplied recovery=true flag.
6. The report, client-email.md and case-study.md carry lessons 16–18 into the same client identity. They distinguish local checks, illustrative projections and unperformed human acceptance. Do not replace untested fields with passed to make the handover look complete. The generated email is a local file; nothing is sent.

## Run the delivered pilot and its counterexamples

From this directory:

```sh
python3 engagement.py --inputs client --output my-delivery
python3 check.py
```

Use a fresh output folder for each run; existing pilot databases are preserved rather than overwritten. Expected: scoped_local_handover true, client_acceptance not_performed; check.py prints actual pilot/acceptance/restore success and blocks four changed inputs. Inspect my-delivery/acceptance-report.json, client-email.md, case-study.md and restored.sqlite3. The source artifact hashes bind the report to the files you actually ran.

## Transfer and useful feedback

Change the buyer, source and baseline consistently across the client packet. Write the new acceptance cases before running the pilot. Deliberately add an unsupported promise and confirm it blocks handover; then restore the scoped offer. A failing expected label means the candidate disagrees with the fixed contract; it is not permission to rewrite labels after observing output. A human still needs to review factual usefulness, client authority and real deployment acceptance before any real engagement. Submit both the failed output and the scoped correction. Latency/restore duration are measured locally, costs stay unknown, and source/retention boundaries are explicit.
