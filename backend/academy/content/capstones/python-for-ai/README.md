# Python for AI — bounded knowledge service

This is a single-process, read-only local teaching deployment. The default provider extracts an authorized synthetic policy; it is a fixture, not a trained model. No academy module, real client data or paid API key is required. Use Python 3.12. The only installed dependency is HTTPX, used by the optional provider adapter and its offline mock-transport tests.

## 1. Assemble and test from a fresh directory

Save all the named files from this chapter together. Do not copy the academy repository or its database. On macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -v
python evaluate.py --repeats 20 --output evaluation-observed.json
```

Expected: every test passes; the evaluator records 120 local observations, source_accuracy 1.0, no failed/critical cases, measured p50/p95 and gate_passed true. Provider-call counts distinguish cold from cached answers. Token counts, monetary cost and semantic quality remain unknown/unmeasured. The tiny repeated workload is not representative production load. Keep the generated report out of source fixtures.

Tests deliberately create invalid provider responses, denied owners, outages and timeouts. Those tests pass only when the service rejects them correctly. For example, test_provider_fault_is_502_not_bad_client_input expects 502; test_invalid_provider_never_cached checks storage remains empty. A green test line does not mean no failure was exercised.

## 2. Run the real HTTP service

Generate two independent synthetic credentials. This environment variable belongs in your shell or an ignored local file, never in source control or a screenshot. Loading a .env file is not automatic in this standalone project.

```bash
umask 077
python -c 'import json,secrets; print("export STUDENT_KEYS="+repr(json.dumps({secrets.token_urlsafe(32):"team-a",secrets.token_urlsafe(32):"team-b"})))' > .env
source .env
export STATE_PATH=state/cache.sqlite3
python server.py
```

The restrictive umask makes the newly created .env private to your account. Add .env, .venv, state/ and observed reports to your own .gitignore before committing. The published .dockerignore also excludes them from the image. Keep that terminal running. In a second terminal in the same fresh project directory, explicitly load the same local configuration:

```bash
source .venv/bin/activate
source .env
python probe.py
```

Expected: ready true with provider_checked false, authorized refund source a-refunds-v1, an unknown query abstaining, a repeat cache hit, team-b denied access to the refund evidence, invalid identity 401 and an extra owner field 400. No raw key is printed. The original probe inputs remain in probe.py if a dependency fails; correct the dependency before deliberately repeating a safe read. Do not interpret an unavailable call as a completed answer.

Stop the server with Ctrl-C and restart it with the same STATE_PATH and credentials. Run probe.py again. Its first_request_cached must now be true for a previously committed result. Keep the restart transcript and this output together; a cache hit without a recorded replacement is not restart evidence. Avoid repeatedly exhausting the ten-request-per-owner minute window; 429 is an intentional limit.

## 3. Build and replace a container

Docker uses a separate port from the academy (8080) and workshop. Ensure your own capstone port 8094 is available. Save the published .dockerignore too: it excludes local credentials, virtual environments, state databases and observed reports from COPY . . so those files do not enter the image. These commands operate only on this student project:

```bash
docker build -t python-ai-capstone .
docker run -d --name python-ai-capstone-demo -p 127.0.0.1:8094:8094 --env STUDENT_KEYS --mount source=python-ai-state,target=/state python-ai-capstone
python probe.py
docker rm -f python-ai-capstone-demo
docker run -d --name python-ai-capstone-demo -p 127.0.0.1:8094:8094 --env STUDENT_KEYS --mount source=python-ai-state,target=/state python-ai-capstone
python probe.py
docker exec python-ai-capstone-demo python -m unittest discover -v
docker exec python-ai-capstone-demo python evaluate.py --repeats 20 --output /tmp/evaluation-observed.json
```

The replacement probe must read the prior committed cache from the dedicated volume. Do not remove python-ai-state between these two runs. Run tests/evaluation against their isolated temporary stores; the /tmp output path is writable by the nonroot container user. Remove your demonstration container after collecting evidence; retain or deliberately remove its own state volume according to your exercise plan. Never mount academy source, SMTP configuration or database volumes.

## 4. Restore a consistent snapshot

Session 9 teaches connection lifetime, transactions and SQLite backup. The published unit test test_consistent_backup_and_restore executes this entire procedure with temporary stores. For your running local store, stop incoming exercise traffic, then save/run restore_check.py with this complete block:

```python
import asyncio
import os
from pipeline import Store, FixtureProvider, answer_one

live = Store(os.environ.get('STATE_PATH', 'state/cache.sqlite3'))
# Establish known synthetic fixture state before taking the snapshot.
asyncio.run(answer_one('team-a', 'refund days?', FixtureProvider(), live))
live.backup('state/restored.sqlite3')
restored = Store('state/restored.sqlite3')
result = asyncio.run(answer_one('team-a', 'refund days?', FixtureProvider(), restored))
assert result['cached'] and result['source'] == 'a-refunds-v1'
other = asyncio.run(answer_one('team-b', 'refund days?', FixtureProvider(), restored))
assert other['source'] is None
print('Restored committed fixture and owner boundary verified')
```

This validates snapshot and restore mechanics. Another file on the same disk/volume is not resilience to loss of that disk. A real backup policy needs a tested copy in a separate failure domain, retention and access ownership.

## 5. Optional installed local model

Run the offline adapter tests first. Install/run Ollama separately and choose a tag supported by your machine. Set PROVIDER=ollama, OLLAMA_MODEL to that installed tag and optionally OLLAMA_ORIGIN to an operator-approved origin, then restart. Docker Desktop can use http://host.docker.internal:11434 when appropriate. Add these environment variables explicitly to docker run if using a container; host variables are not forwarded automatically. The model server and weights are not bundled or downloaded by the academy.

The adapter requests stream=false (one final model result) but reads its HTTP response incrementally to enforce a 64 KiB response allowance before JSON parsing. This is different from token-event streaming. It validates done, message shape, text length and supplied token counts. It assigns the selected source label; that label does not prove every generated claim is entailed. Freeze the model identity/digest when available and perform a separate reviewed claim-support evaluation. Tag-only identities can change underneath a cache.

evaluate.py intentionally runs the fixed fixture by default. For a real-provider contract report, call its evaluate(OllamaProvider(...)) from a separate script with explicit operator configuration and preserve failures. Then perform the separate semantic review; do not relabel the fixture report as real inference. Missing token counts remain null; local compute is not zero cost. Real model inference and production capacity are untested until you run and record them.

## 6. Failure boundaries and graduation evidence

The project validates the entire batch before starting workers; malformed caller data is InputError/400. Provider shape/usage/source or transport failures are ProviderError/502; deadline failures are 504. Nested task-group errors are classified without turning them into successful empty answers. A failed batch returns no completed batch. Previously completed read-style items may already have committed scoped cache entries; cancellation does not roll back an already-running thread's commit.

Keep a map from each session to its observed evidence: exact schema (1), response byte bounds (2), bounded/cancelled workers (3), overall/item deadlines (4), adapter contracts (5), safe-read retry policy and intentionally no automatic server retry (6), owner-scoped evidence (7), independent cache revision misses (8), rollback/snapshot restore (9), versioned measured gate (10), HTTP identity/quota/capacity (11), and the assembled/replaced container (12).

Operating limits: 16 KiB request bodies, 20 queries per batch, three workers, two active requests per process, ten requests per owner per minute, an 18-second item deadline and a 25-second batch deadline. Queue waiting and storage are inside the request lifetime, but cancellation cannot forcibly stop a thread or CPU loop. ThreadingHTTPServer can create request threads before the application semaphore. Before public hosting use TLS, managed identity, a production server, upstream connection admission, shared quotas, redacted observability, tested external backups and representative load/model evaluation. Do not add replicas and claim process-local counters are globally enforced.
