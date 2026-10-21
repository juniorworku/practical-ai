# Capstones built as a student

Built the six independent final projects from the program's published teaching. The earlier review established prerequisite maps, but that did not establish that a learner could assemble and run a complete application. This pass supplies and executes the missing connecting code. Complete files appear inline before the final assignment and in each program's optional capstone/ download.

## Actual student deliverables

| Program | Working build | Checks performed |
| --- | --- | --- |
| AI Agent Bootcamp | Bounded read-only support agent, DRF API, PostgreSQL results, browser review and transactional local outbox. | 32 HTTP checks; evidence-before-draft, allowlist and step-budget probes; wrong-owner/stale-payload denial; concurrent duplicate approval; restart, outage, quota and isolated PostgreSQL restore. |
| AI Workshops | One selected extraction studio: validated purchase requests, precise decimal totals, correction/review states, persisted records and browser confirmation. | 32 HTTP checks including missing/negative fields; actual browser submission and correction; repeat approval; durable restart/readback, outage, quota and restore. Other studios remain useful independent portfolio artifacts rather than five imaginary deployed products. |
| Freelancing Masterclass | Complete fictional client packet, an executable source-extractive pilot, actual acceptance report, SQLite backup/restore, bounded handover email and case study. | Three unchanged acceptance cases; mismatched promise, false expected label, excess data and unapproved change blocked. Human client acceptance remains explicitly not performed. |
| AI Engineering | Local source-grounded SaaS route with PostgreSQL ingestion, owner-scoped retrieval, context cap, two named routing fixtures, reviewed local effects, shared quotas and evaluation. | 36 HTTP checks plus 120 real API cases in ten families at four concurrent clients; individual failures retained; browser ingestion/review; restart, database outage, shared quota and actual restored-record comparison. |
| GenAI Accelerator | Complete FastAPI/PostgreSQL/Redis/Celery ingestion system, a bounded agent querying its actual stored sources, and a real stdio MCP server/client. | Actual upload → worker → database → grounded answer → agent → MCP round trip; no-source/denied-write/budget paths; worker/database/Redis outages; process recreation; isolated restore; incremental migration; shared quota and fail-closed recovery. |
| Terminal Tutor | Actual scratch-workspace CLI with inspected instructions, fresh-process execution, captured output/exit/deadline evidence and bounded resumable notes. | Real passing and failing assertions, a real timeout, stale-source rejection, denied symlink and instruction expansion, preserved failed evidence, fresh-process resumption and no overwrite of existing exercises. Tested with Python 3.12. |

## Gaps repaired

- Separate lesson specimens had no complete assembly path. Each project now has every import, file, schema setup, command, expected observation and diagnosis procedure. No other academy program or private Workshop checkout is needed.
- The web projects needed an explicit HTTP/storage/workflow connection: exact input fields, authenticated fixture ownership, raw JSONB decoding, saved failure states and database-backed review receipts now connect end to end.
- The first actual PostgreSQL startup exposed a reserved identifier (`window`) in the quota schema. It was corrected to `bucket`, then rebuilt and run successfully.
- Approval needed one canonical serialization between browser and server. The server provides the stored-payload digest; JavaScript does not reconstruct Python's JSON serialization by rewriting text. Row locks, a stable receipt ID and one transaction preserve concurrent replay behavior.
- The Accelerator's original independent agent/MCP policy fixtures were not connected to its persisted ingestion service. The final agent and MCP tool now retrieve the document actually uploaded by the acceptance script, under a server-owned identity.
- The final client engagement needed real deliverables rather than prefilled passed flags. The pilot writes and reopens a database, runs fixed cases and restores a separate copy; client communication carries the resulting limitations.
- Tutor resumption needed actual execution evidence, not a copied success message. It now binds observed command output to source and instruction hashes, rejects stale evidence and returns nonzero for failed/timed-out exercises.

Assembly teaching is inserted before the capstone: Bootcamp session 19 → build in 22; Workshops 17 → 18; Freelancing 15 → 18; Engineering 35 → 36; Accelerator lesson 80 → final MCP lab; Tutor 7 → 8. Original bounded lesson variations remain separate practice; passing them alone does not complete the integrated project.

## Evidence boundaries

These are working **local student projects**, with real HTTP, databases, workers, containers, browser interactions and MCP where described. Model proposals/routing are explicitly scripted fixtures and retrieval baselines; no live model quality, paid provider usage, GPU capacity, production authentication or cloud autoscaling is claimed. The local outbox is a persisted simulated effect; no real message, event, order or refund is sent. The fictional engagement's business assumptions are illustrative, and human factual/client acceptance remains untested. These boundaries appear in the source, teaching, runbooks and reports.

Engineering's four-client test measures this local service and machine, not thousands of cloud users. Its twelve variants per family do not constitute 120 independent semantic tasks. Unknown model costs and token usage remain null.

## Reproduction and reports

Each folder under backend/academy/content/capstones/ has its own complete README. Docker project names and ports are independent: capstone-boot 8211, capstone-workshop 8212, capstone-engineering 8214 and capstone-accelerator 8215. Academy remains on 8080 and Workshop on 8000.

- [Per-file source audit](capstone-source-audit.json)
- [Web capstone operations](capstone-operations.json)
- [Accelerator operations](accelerator-capstone-operations.json)
- [Actual capstone browser workflows](capstone-ui.json)
- [Published lesson/file parity](capstone-published.json)
- [Preserved student build evidence](capstone-build-evidence/)

The evidence folder includes actual reports and synthetic deliverables, including Engineering's 120-case HTTP report and the actual MCP transcript result. In the app, project files are hash-bound to their published revision. Backend regression coverage verifies identical downloaded files, protected accounts and preserved learner data; the browser checks every final project's inline source against its file manifest.

Final published verification: all six project chapters and 56 file hashes matched the deployed browser; all three project browser forms passed their real submission/review/negative paths with no JavaScript errors. The full PostgreSQL backend suite passed **33 tests**, including exact program-download integrity, enrollment protection and learner-record preservation. The frontend build and whitespace checks passed. The academy was rebuilt successfully at http://127.0.0.1:8080/.
