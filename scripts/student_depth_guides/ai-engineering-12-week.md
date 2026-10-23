## Student build walkthrough — a bounded local SaaS release, with honest upgrade boundaries

The earlier voice, mixed-media, workspace and evaluation integration files remain separate runnable projects. This graduation service combines a narrower path: persisted synthetic text → scoped lexical retrieval → one of two scripted routes → reviewable draft → local receipt. The two routes do not call real local or frontier models. Cloud autoscaling, speech quality and GPU throughput need the separately taught deployment/provider experiments; this local service cannot certify them.

### Step 1 — carry the actual taught retrieval invariant into the build

Session 8 now contains the exact `select_context` function used by core.py. Run its published tests first:

```sh
python3.12 -m unittest -v test_core
```

The paragraph fixture deliberately places “Opened items are excluded” after character 350. The old fixed-character split could return the rule while dropping that exclusion. The current implementation keeps reviewed paragraph units intact, retains source ID/position/revision, and refuses a relevant unit that exceeds its 700-character allowance. needs_correction is visible and contains no answer or citations. It is safer than silently slicing an exclusion out of evidence.

The allowance counts evidence characters before join separators, not provider tokens. Owner filtering is the SQL adapter’s job before it calls the pure function. An irrelevant oversized paragraph is excluded by ranking; a relevant oversized paragraph requires a reviewed split. This is a deliberate conservative policy, not an optimal semantic chunker.

### Step 2 — follow storage identity and context through one request

`documents` derives an ID from owner and the exact text digest. Same owner/same bytes return the same identity; another owner cannot reuse that ID to read private content. This local fixture keeps every uploaded document searchable. It does not choose active policy versions or resolve contradictory uploads. Keep one approved policy per source for this scoped release; the ingestion/index-migration lessons teach the explicit activation mechanism needed before expanding that claim.

`ask` fetches only the authenticated owner’s documents, then `select_context` ranks whole units. The route selects routine_fixture or reasoning_fixture from the declared query rule. Both extract source text. The candidate cache key uses canonical JSON containing pipeline version, selected route, query and evidence revisions; it is an identity for a future cache, not an implemented hit or measured savings. Source IDs contain owner in this service. A general cache must also bind trusted owner/permission state explicitly and invalidate on revocation.

### Step 3 — interpret the evaluation denominator correctly

Run check.py, then evaluate.py in a fresh quota window as documented. Its 120 HTTP observations cover ten families with twelve variants each. Labels stay in the harness. A timeout or 429 remains a failed observation, not a row to delete. Four clients measure this bounded local workload; they do not simulate thousands of concurrent users or independent semantic tasks.

Session 29’s runtime studio now calculates cost per accepted result from all attempted work and leaves partial cost unknown. In this capstone, cost_usd and provider token usage remain null because no model is called. A passed mechanical release harness is not a measured faithfulness score. Retain a separate source-support review for any future real adapter and record model/prompt/dataset versions and disagreement.

### Step 4 — use failure evidence to decide the next change

| Failure | Repair at the taught boundary | Do not substitute |
| --- | --- | --- |
| Exception lost from context | Reviewed evidence-unit boundary in session 8 | A valid citation ID alone |
| Another owner sees source text | Owner predicate before retrieval | Post-generation redaction |
| Oversized relevant unit | Review its split or change a measured budget | Silent truncation |
| Identical candidate key after source change | Canonical source revision identity | Calling an unimplemented cache a hit |
| Partial cost reported as complete | Unknown-cost counter and undefined ratio | Zero for unavailable billing |

Student extension: before modifying the retriever, add a policy whose exclusion occurs after the old cut and prove the complete exclusion survives HTTP readback. Then add a relevant oversized unit and require needs_correction. Keep this test corpus separate from evaluate.py’s frozen corpus: injecting an intentionally oversized relevant policy changes the candidate environment. Use a dedicated fresh Compose project/volume for the extension, then run restart, outage and restoration drills on its exact IDs. Do not delete another project’s data to get a clean score.

### Read a failed acceptance report

The HTTP check starts a fresh report before its first request and updates it as checks run. A failed assertion or dependency exception leaves completed=false, the checks observed so far and error_type; it still exits nonzero. A completed=true report means the whole procedure finished. Latency p95 uses nearest rank, ceil(.95*n)-1, over its labeled sample. Do not reuse an older successful report after a new failed run, and do not mistake twelve sequential observations for a capacity benchmark.
