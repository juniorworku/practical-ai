# Docker and PostgreSQL verification — 20 October 2026

The academy is running at **http://127.0.0.1:8080/** using the built Nginx/React frontend, Gunicorn/Django REST API, and PostgreSQL **17.11**. The API confirms `connection.vendor == postgresql`. SQLite was not used for this verification.

## Results

| Boundary | Observed result |
|---|---|
| Docker build | Both application images build successfully; TypeScript and Vite production compilation pass |
| Startup | Migrations, practical curriculum upgrade, imported library, and static collection complete |
| Database readiness | Actual `SELECT 1`; response identifies PostgreSQL; database errors produce 503 without raw errors |
| Probe rate limits | Readiness is exempt from learner API throttling; regression test passes |
| PostgreSQL test suite | **12 tests passed** in a separate `test_academy` database, automatically destroyed afterward |
| Downloadable lab references | **17 tests passed** inside the actual Python 3.12 container |
| Browser | Production Docker frontend and real API; all 60 authored session bodies read and validated; desktop and phone layouts pass |
| All three programs | Enrollment, actual lesson opening, completion and dashboard state verified for Bootcamp, Workshops and Masterclass |
| Learner state | Notes and completion checked after reload; login/logout and revoked-token rejection verified |
| Data isolation | A second account cannot read or delete another account's project or read its private notes |
| Full library and tools | 20-phase library, 105-item original Accelerator, project planner, terminal simulation, eight-part Tutor and ZIP download pass |
| Admin and proxy | Invalid login reaches Django's login validation with valid CSRF handling; collected admin CSS returns 200 |
| Service restart | Database, backend and frontend restarted; account, enrollment, completion, notes and saved project survive |
| Final rebuild | State remains readable after final readiness/proxy deployment; migrations match models |

Screenshots are in `docs/screenshots/`. Browser checks report no uncaught JavaScript errors and no horizontal overflow on the phone home page or lesson reader. The smoke test creates synthetic learner accounts only. The local environment file and test credential snapshots are private and are not packaged into images or course downloads.

## Curriculum release

- **AI Agent Bootcamp:** 24 sessions over a suggested eight weeks; about 50 hours of practice. One support-agent capstone covers source ingestion, retrieval, contracts, tool ownership, bounded loops, approvals, persistence, evaluation, threat modeling, deployment, recovery, and handover.
- **AI Workshops:** 18 studios over a suggested six weeks; about 50.5 hours. Six projects cover document extraction, meeting actions, grounded research, support triage, content operations, and an integrated app sprint.
- **Freelancing Masterclass:** 18 sessions over a suggested six weeks; about 40 hours. One simulated engagement covers discovery, baseline measurement, offer, scope, effort/cost assumptions, data access, pilot, feedback, evaluation, change control, operations, acceptance, support, and portfolio evidence.
- Every session includes substantive explanation, a worked example, independent implementation steps, a deliberate failure, three acceptance checks, and a unique deliverable. There are 60 deliverables and over 20,000 authored words; time estimates include building and review rather than reading alone.
- Six offline programming exercises, reference implementations, synthetic fixtures, and editable engagement/evaluation worksheets are included in the learning kit.
- Active inventory: **25 programs and 696 sessions/readings** (523 source chapters + 105 Accelerator entries + eight Tutor guides + 60 practical sessions). The 13 previous introductory lessons are archived with their existing learner records and excluded from active progress. A migration test verifies preservation and prevents old completion from being transferred to unrelated new lessons.

## Issues found and fixed

1. PostgreSQL enforced the previous 40-character prerequisite field limit, which SQLite had not enforced. Added `0002_alter_program_level` to support the richer descriptions. The failed seed transaction left no partial upgrade.
2. Nginx previously dropped the public port from the Host header, which could break admin CSRF checking. It now forwards the original Host header.
3. General anonymous API throttling could eventually reject repeated Docker readiness probes. Readiness is now explicitly unthrottled, with a regression test.
4. Compose now restarts the frontend when its API dependency is explicitly rebuilt so its upstream is refreshed.
5. Duplicate lesson titles in authored Markdown are suppressed in the reader while the original stored text remains intact.

## Reproduce

```sh
docker compose up -d --build --wait
docker compose exec -T backend python manage.py test --noinput
docker compose exec -T -w /app/academy/content/program_labs backend env LAB_MODULE=reference python -m unittest discover -s tests -v
APP_URL=http://127.0.0.1:8080 EXPECT_DATABASE=postgresql PERSISTENCE_FILE=/tmp/practical-ai-e2e-persistence.json node tests/browser-smoke.cjs
APP_URL=http://127.0.0.1:8080 node tests/admin-smoke.cjs
docker compose restart db backend frontend
docker compose up -d --wait
APP_URL=http://127.0.0.1:8080 PERSISTENCE_FILE=/tmp/practical-ai-e2e-persistence.json node tests/check-persistence.cjs
```

Browser scripts use the bundled Playwright/Chrome paths on this machine; `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE` can select another installation. Run only against a development stack. Test databases are isolated; the browser accounts live in the development database so their persistence can be checked.

## Verification limits

This verifies the implemented local academy flows. No public deployment, paid model inference, original AI feedback integration, live cohort calls, outbound email, or real external tool action was performed. The project planner remains a deterministic template; the command tutor remains a simulation. Offline exercise stubs intentionally fail until a learner implements them; the 17 passing cases refer to the supplied reference implementation. Course completion remains self-reported, not automatic assessment or certification.
