## Student build walkthrough — extraction evidence to confirmed purchase draft

This capstone implements one selected studio, document extraction. It does not silently require deploying the other four portfolio workflows. Studio 1 session 2 now supplies the exact parser and its line-provenance studio; session 11 supplies a separate per-class routing report for the triage studio. Do not substitute routing accuracy for extraction acceptance.

### Step 1 — reproduce the source-to-field calculation

Before starting Docker, run:

```sh
python3.12 -m unittest -v test_core
```

The parser enumerates lines from 1, splits each at the first colon, stores raw source spans in `field_evidence`, and trims the value for validation. For the four-line fixture, quantity is supported by line 2, unit price by line 3, and Decimal('10.00') multiplied by 2 produces '20.00'. This is exact arithmetic after validation, not model extraction or an inferred purchase price.

Add a second Quantity line. Predict needs_correction, both line spans retained, no computed record and no reviewable answer. The duplicate cannot overwrite the first value and become a successful record. A colon in a supplier name must survive because splitting occurs only once. If your code loses that punctuation, repair parsing rather than editing the source fixture.

### Step 2 — read the two different review boundaries

A needs_correction record tells the student to repair ambiguous or invalid input. It is not approvable. A needs_review record has passed this schema but still requires human confirmation. Schema validation cannot prove the request was authorized by a real business or that the supplier is legitimate. The teaching identities and inputs are synthetic; there is no external purchase action.

The HTTP route stores the original input, normalized record, field evidence, issue codes and status in one draft payload. On readback, compare `field_evidence` with that exact input, not a subsequently edited document. Correcting the source means submitting another request and reviewing its new ID. This simple capstone does not implement an editable revision editor or automatic linkage between those IDs.

### Step 3 — inspect actual HTTP failure and approval behavior

Run the documented Compose and check.py commands. Missing fields and invalid quantities are domain results with needs_correction; malformed HTTP shape is 400; missing identity is 401; a student trying to approve is 403; stale or changed approval is 409. Database dependency failure is 503. These statuses guide different learner actions, rather than one generic “something went wrong” response.

The approver confirms the normalized text, citation and source-version digest returned by the server. The unchanged stored input and spans remain available for inspection. The local receipt records approval only; external_delivery=false. An effect row is not proof that a supplier received anything.

### Step 4 — retain a small evidence table before extending

| Input variation | Expected parser result | What to inspect |
| --- | --- | --- |
| Four valid fields, quantity 2, price 10.00 | needs_review, total 20.00 | Line 2/3 evidence and exact Decimal total |
| Missing price | needs_correction | Missing-field issue, no invented zero |
| Two conflicting price lines | needs_correction | Both raw spans, no computed record |
| Negative quantity or NaN price | needs_correction | Validation before arithmetic |
| Extra Owner line | needs_correction | Exact declared schema, no client authority |

For a useful extension, add a second supported currency only after defining its schema and test cases. Do not add currency conversion rates or a provider call as an unexplained requirement. Keep both field correctness and whole-record acceptance in your report: three correct fields and one wrong price must not become a fully accepted purchase draft. Measure reviewer workload separately from parser latency. Retain failures, restart readback and the restore comparison alongside your final portfolio case study.

### Read a failed acceptance report

The HTTP check starts a fresh report before its first request and updates it as checks run. A failed assertion or dependency exception leaves completed=false, the checks observed so far and error_type; it still exits nonzero. A completed=true report means the whole procedure finished. Latency p95 uses nearest rank, ceil(.95*n)-1, over its labeled sample. Do not reuse an older successful report after a new failed run, and do not mistake twelve sequential observations for a capacity benchmark.
