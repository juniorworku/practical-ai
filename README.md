# Practical AI Education

A free learning academy built with Django REST Framework, PostgreSQL, React + TypeScript, Tailwind CSS 4, and Docker Compose. Original design inspired by the supplied program screenshot, with a public catalog and a working learner workspace.

## Start with Docker

```sh
cp .env.example .env
# Replace DJANGO_SECRET_KEY and POSTGRES_PASSWORD in .env.
sh scripts/start.sh
```

Open http://localhost:8080. Create a free learner account. The API and PostgreSQL are private to the Compose network; only the frontend is published, on localhost. Database data persists in a named volume. Startup applies migrations and imports course content without overwriting instructor edits.

### Run beside Workshop

| App | Browser URL |
|---|---|
| Practical AI Docker | http://127.0.0.1:8080 |
| Workshop Docker | http://127.0.0.1:8000 |
| Practical AI native Django (optional) | http://127.0.0.1:8001 |

`sh scripts/start.sh` starts the `practical-ai-academy` project using this directory's Compose and environment files, even when called from another folder or a shell with another `COMPOSE_PROJECT_NAME`. It builds and waits for startup, and retains the existing named database volume. To stop only this app, run `docker compose --project-name practical-ai-academy down` from this directory.

The dedicated host setting is `ACADEMY_PORT=8080` in `.env`; the generic `APP_PORT` is intentionally ignored so another app's exported value cannot move Practical AI onto port 8000. If upgrading an existing custom port, rename that `.env` key to `ACADEMY_PORT`. Internal API port 8000 and PostgreSQL port 5432 are private to this app's Docker network and can coexist with Workshop's internal ports. Vite's default proxy continues to use Docker on 8080; if choosing a different Docker port, set `ACADEMY_API_PROXY` to that origin before starting Vite.

Create an instructor/admin account:

```sh
docker compose exec backend python manage.py createsuperuser
```

Open http://localhost:8080/admin/. Program/lesson editing uses Django admin. Learner enrollment is free; there are no payment calls.

## Local development

Python 3.12+ and Node 22.12+ recommended. PostgreSQL is the default; explicit SQLite mode supports a lightweight local preview and tests.

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cd backend
export DJANGO_SECRET_KEY=local-development-only
export DEBUG=1
export USE_SQLITE=1
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py seed_curriculum
../.venv/bin/python manage.py import_workshop
../.venv/bin/python manage.py runserver 127.0.0.1:8001
```

In another terminal:

```sh
cd frontend
npm ci
ACADEMY_API_PROXY=http://127.0.0.1:8001 npm run dev
```

Open the Vite URL (normally http://localhost:5173). Vite forwards `/api` to Django. To develop against PostgreSQL, omit `USE_SQLITE`, configure the PostgreSQL variables from `.env.example`, and point `POSTGRES_HOST` at your local database. Shell development does not automatically read `.env`.

## Included

- AI Agent Bootcamp: eight weeks, 24 build sessions, approximately 50 hours.
- AI Workshops: six weeks, 18 project studios, approximately 50.5 hours.
- Freelancing Masterclass: six weeks, 18 delivery sessions, approximately 40 hours.
- Six runnable offline labs, 17 reference tests, synthetic fixtures, client-delivery templates, and 96 specific session deliverables.
- Full original workshop library: **523 chapters across 20 phases**, including source code and original quiz references.
- Original GenAI Accelerator: **85 catalog lessons + 20 labs**, including the added extension chapter; original materials describe 84 numbered core/advanced lessons. The import uses the actual catalog, not a hard-coded count.
- Eight-part Terminal Tutor guide, downloadable curriculum and original capstone starter.
- Learner registration/login/logout, idempotent enrollment and completion, persistent private lesson notes, searchable library and lessons.
- A saved project planner (deterministic guided template) and a safe, stateless terminal simulation.
- Five independent catalog programs with public syllabuses. The four authored practical programs include 96 substantive sessions, 288 quiz questions, 288 flashcards, 288 reflection prompts, guided exercises, acceptance checklists, private notes and inline input/output experiments.
- Sage/sand/cream theme across the public catalog and learner workspace; personal dashboard, admin, health endpoint, migrations, API and browser regression tests.

## Source materials

The course snapshot was copied from the user-specified Resume Studio directory. Only explicit curriculum files, licenses, and capstone starter artifacts were imported. No database, personal job-search material, credentials, account data, original application runtime, or learner progress was copied. Original teaching instructions are inert educational content. Markdown rendering disables raw HTML and remote images; source code is shown as text and never executed by the server.

The source library is pinned to `rohitg00/ai-engineering-from-scratch` commit `aae3dc64e53457aae952e90ee9304fd13f9941a8`. Attribution and licenses are in `backend/academy/content/`; see `docs/sources.md`. The original source may contain dated SDK/protocol material; learners should verify current official documentation before production use.

Re-import from a source folder deliberately:

```sh
python3 scripts/import_workshop.py '/path/to/resume-studio'
cd backend
../.venv/bin/python manage.py import_workshop
```

Existing seeded lesson rows are deliberately preserved. Review changes and apply a deliberate data migration when revising published curriculum.

## Verify

```sh
cd backend
DJANGO_SECRET_KEY=test-only USE_SQLITE=1 ../.venv/bin/python manage.py test
cd ../frontend
npm run build
```

For PostgreSQL integration tests, use a dedicated test database/user with permission to create the test database and omit `USE_SQLITE`. Never point tests at an existing production database.

`tests/browser-smoke.cjs` drives the real frontend/API with Playwright against a disposable database. Start both dev servers first, install Playwright in a separate test tools folder (or set `PLAYWRIGHT_MODULE`), then run it with Node. It creates uniquely named learner accounts; do not run it against production.

## Release boundaries

This is a runnable first release, not a deployed public service. The original lessons, lab readings, source quiz references, notes and downloads are integrated; original model-powered feedback, cohort video calls, email/password recovery, certificates and community discussion are not ported. The four practical programs now include server-graded quizzes, flashcards, reflections and practical evidence submissions. The Accelerator planner makes no model call and Terminal Tutor simulation never runs a shell. Learners run capstone code separately. Progress is self-reported, not an assessment or certification.

For Docker verification, use `APP_URL=http://127.0.0.1:8080 EXPECT_DATABASE=postgresql node tests/browser-smoke.cjs` against a development stack. The browser suite reads all 96 program sessions, exercises each program, checks account isolation and token revocation, and downloads the full learning kit.

Build authored curriculum with `python3 scripts/build_programs.py`, then regenerate the public download using `python3 scripts/package_learning_kit.py`. The latter preserves a strict public-file allowlist. Recognized legacy introductory lessons are archived with their existing identities, notes, completions, and enrollments; they are excluded from active-course progress. Practical program rows are seeded by stable source IDs and instructor edits are retained.

Before public deployment, configure HTTPS and secure cookies, set `DEBUG=0`, use strong secrets and real hosts, configure trusted proxy/CSRF origins, add account recovery and email verification, use a shared throttle cache, and establish database backups. Development auth tokens are stored in tab-scoped sessionStorage; migrate to a reviewed secure cookie/session scheme for a public release. No live AI credentials or paid services are required.

Run `APP_URL=http://127.0.0.1:8080 node tests/learning-studio.cjs` to verify all seven activity sections, persisted results, independent curricula, chapter navigation, inline exercises and responsive layouts. See `docs/sources.md` for learning-interface research and palette attribution.

The original three course books are built by `scripts/course_books/` from the pinned MIT source plus original academy teaching and cases. Learners read the content in the app; no GitHub redirect or workbook download is required. The license and teaching credit appear in each book. `docs/course-book-manifest.json` records the exact selection per session. Existing notes, enrollments and lesson identities are preserved during the recognized v3 upgrade; earlier practice revisions remain stored.

The Vite preview on port 5173 proxies to the Docker app on port 8080 by default, so both use the same PostgreSQL curriculum and learner state. For an intentionally separate native Django server, set `ACADEMY_API_PROXY=http://127.0.0.1:8001` before starting Vite.

The independent 12-week AI Engineering program is generated by `scripts/engineering/`, with 36 sessions, five capstones and roughly 149 hours of practice. Every module applies software-first, production-oriented teaching and the latency/cost/quality, deterministic-evaluation and context-management pillars. See [the curriculum and evidence boundaries](docs/engineering-curriculum.md). Run `python3 tests/engineering-content.py` for exact published offline examples and `python tests/engineering-integrations.py` in an isolated environment with the supplied example dependencies for real local SDK/protocol checks. Neither suite establishes live provider quality or cloud/GPU scale.

The [student teaching review](docs/engineering-student-review.md) documents lesson sequencing, practice alignment and concrete example repairs. Run `python3 tests/engineering-teaching-audit.py` to execute all 36 complete published practice solutions. `node tests/engineering-student.cjs` walks every engineering lesson in the running Docker app, checking chapter/code rendering, staged hints, reference solutions, reflection guidance, selected-answer feedback and remediation navigation.


The same guided teaching structure now covers the original three programs: 60 lessons with concept tutorials, causal walkthroughs, bounded practice before integration, complete code or decision references, progressive hints and selected-answer feedback. See [the practical-program student review](docs/practical-student-review.md). Run `python3 tests/practical-teaching-audit.py` for the exact published practice references and regression probes; run `node tests/practical-student.cjs` against the Docker app for every original program’s chapters and guided student flow. An optional comma-separated argument such as `B04,B22,F06` limits browser checks while still verifying served-source parity for all 60 lessons.

The GenAI Accelerator and Terminal Tutor have also undergone a [student teaching review](docs/imported-student-review.md), covering 113 sessions, complete inline examples and practice, and the isolated API/PostgreSQL/worker case study.

The [program progression review](docs/program-progression-review.md) documents entry skills, interleaved Accelerator labs, project prerequisite maps and preserved learner records.

The [capstone student-build review](docs/capstone-student-build-review.md) records the six independent runnable projects, complete inline code, restart/restore drills and observed results.

## Learning workflow improvements

- Every main program has a public full-lesson preview. Lesson, program and workspace URLs use hash routes so bookmarks and browser navigation work behind the Docker frontend.
- Notes and practice drafts recover from account-scoped browser storage, then autosave to PostgreSQL. Notes use a base-text conflict check; practice retains its revision/version checks. Conflict recovery lets learners export the local draft and load account data without silently overwriting it. Browser recovery drafts are local to that browser; only successfully synced data follows the account to another device.
- Reading position remembers the lesson, chapter and local scroll position. Reading completion is explicitly self-marked. Quiz success, browser-reported lab checks and human project review are distinct evidence states; none is represented as production certification.
- Three executable Python supplements are available in AI Agent Bootcamp sessions 1, 3 and 4. They teach scope boundaries, evaluation scoring and output contracts before the coding task. Exact checks, failure-specific feedback and reference solutions are visible. No student Python executes in Django. The pinned Pyodide runtime is served locally, loaded only when running a lab, and runs in a worker inside an opaque-origin iframe. Its CSP blocks academy API and external network access. Stop and a 30-second timeout dispose of the runner; output is bounded. These are browser-reported practice results, not trusted server grades. Full Docker/API capstones still run in the student's own workspace.
- My learning includes a goal/skills check, weekly practice estimate, a Python bridge, due flashcards and recent quiz mistakes. Recall ratings schedule again in ten minutes, hard in one day, and good at an expanding 3–30 day interval; confidence is not a quiz score.
- Practical tasks support immutable project revisions with artifact/commit, reproduction evidence, and latency/cost/quality, evaluation, context and limitation reports. URLs are recorded, never fetched automatically. Reports export as JSON. Staff use **My learning → Staff project review queue** to request changes or record review; users cannot review their own work. Reference capstone files can be browsed inside the task panel.
- Get help contains authored, progressive lesson hints, enrolled-learner questions and staff replies. It is explicitly an authored guide, not a connected AI tutor. Content issues retain the exact lesson revision and are triaged in Django admin.
- Optional live sessions are scheduled in **Django admin → Live sessions**. Set a real program, start/end time, meeting URL and capacity. Enrolled learners reserve/cancel in My learning; capacity is enforced transactionally and meeting links are shown after reservation. No sessions or instructors are invented. Programs remain independent and self-paced.

### Password recovery email

Password resets use plain-text and branded HTML emails with a single-use link valid for one hour. A successful reset preserves learning progress while revoking existing browser sessions and API tokens. Unknown addresses and delivery failures return the same public response; operators receive sanitized delivery-failure logs.

Set these **server-side** values in the ignored, private `.env` file:

```dotenv
ACADEMY_PUBLIC_URL=http://127.0.0.1:8080
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-account@gmail.com
EMAIL_HOST_PASSWORD=your-provider-app-password
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
EMAIL_TIMEOUT=10
DEFAULT_FROM_EMAIL=Practical AI <your-account@gmail.com>
PASSWORD_RESET_TIMEOUT=3600
```

For Gmail, use the account's SMTP app password. For a different provider, use its verified sender and SMTP credentials. Port 465 uses `EMAIL_USE_SSL=1` and `EMAIL_USE_TLS=0`; do not enable both encryption modes. Authentication credentials never belong in frontend configuration or Git.

```sh
docker compose up -d --build backend frontend
docker compose exec -T backend python manage.py check_email
# Optional: send one diagnostic to an address you control.
docker compose exec -T backend python manage.py check_email --recipient you@example.com
```

`check_email` validates settings and connects/authenticates without sending by default. It reports failures without printing credentials. SMTP acceptance alone does not prove inbox delivery: request a recovery email, confirm receipt, open the link, reset and sign in again. `tests/password-reset-email.cjs` provides a two-phase real-browser check with a controlled test inbox; its temporary state and received link must stay outside the repository with mode 0600.

Reset URLs use `ACADEMY_PUBLIC_URL`, never the incoming Host header. The local URL works on the computer running the app; a hosted release needs the actual public HTTPS origin. Secure cookies follow that origin. No `EMAIL_HOST` means no email delivery. If mail is missing, check provider authentication, verified sender, spam placement, outbound connectivity and sanitized backend logs.

Configuration follows [Django 5.2's SMTP settings](https://docs.djangoproject.com/en/5.2/topics/email/). Provider inbox delivery and the complete reset journey must be verified separately from unit tests.

### Verify learning workflows

```sh
docker compose exec -T backend python manage.py test academy --noinput
npm --prefix frontend run build
node tests/learning-workflows.cjs
```

The browser harness uses `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE` when set, or the local Codex Playwright runtime and macOS Chrome defaults. It exercises real Python failures/successes, sandbox network rejection, stop execution, autosave/recovery through navigation and reload, project evidence, lesson questions, diagnostic planning, spaced recall and mobile layout. CI checks the backend against PostgreSQL and builds the frontend. It does not claim live model quality, a staffed mentoring service or cloud-scale capstone verification.

### Account and workspace refresh

The sage-and-cream interface now includes a focused resume dashboard, saved lessons, enrolled-lesson/private-note search (`⌘/Ctrl K`), a private project portfolio and account settings. Project revisions retain their original measurements and human review status; exporting evidence does not publish it.

Browser sign-in accepts a username or an unambiguous email address. New accounts use an HTTP-only Django session cookie, CSRF-protected writes, optional 30-day device remembrance and no browser-stored API token. Account settings support display names, password changes and revoking other browser sessions. Password changes and recovery revoke existing API tokens and other tracked sessions. Existing token API clients remain supported. Older accounts sharing an email must sign in with their username. Email/username changes are deliberately unavailable until a verified identity-change workflow exists.

Use `ACADEMY_PUBLIC_URL` for the actual origin. Hosted deployments must use HTTPS: secure-cookie flags follow that setting. Local Docker remains at `http://127.0.0.1:8080`, independently of the workshop app. SMTP setup above is still required for real recovery email delivery.

```sh
docker compose up -d --build
node tests/account-workspace.cjs
```

The account browser harness covers signup, sign-in by email, remember-device expiry, session restoration, CSRF rejection, profile updates, device revocation, password changes, saved lessons, search, return to a requested lesson after sign-in and mobile overflow. `backend/academy/test_accounts.py` covers session security and cross-account workspace privacy against the database.

### Interactive interface and favicon

All six independent programs appear in the public catalog, with topic search, category filters, result counts and a reset action. Lesson search has a recovery action when no lesson matches. Global search supports `⌘/Ctrl K`, arrow keys, Enter and Escape; opening the current lesson preserves its loaded teaching.

The favicon follows the academy's layered sage/cream mark. Sources and browser assets live in `frontend/public/`: SVG, multi-resolution ICO, Apple touch icon, 192/512px icons and `site.webmanifest`.

Page transitions, scroll reveals, card/button feedback, accordions, learning feedback and dialogs use short decorative motion. Content stays usable without animation. Both JavaScript motion and CSS effects honor `prefers-reduced-motion`, including changes made while the app is open. A skip link, route-specific document titles, keyboard-friendly mobile navigation, a visible mobile sign-in action and back-to-top control improve navigation.

Terminal Tutor remembers up to 50 unique commands in the current app session. Up/Down recalls commands and restores an unfinished draft; output follows the newest response. This is still a simulated, stateless command tutorial.

Lesson, preview, search and account screens load on demand. If a screen fails to load, an error page offers a reload action. Existing server-side learning state is unaffected by page loading.

```sh
node tests/ui-interactions.cjs
node tests/account-workspace.cjs
node tests/learning-workflows.cjs
```

The interaction harness verifies favicon dimensions, the six-program catalog, empty states, menu/focus handling, keyboard search, terminal history, real motion calls, reduced-motion behavior, and recovery after an intentionally failed page-module request.

The six-program student UI regression checks first, middle and final lessons at desktop, 390px phone and 320px phone widths, plus saved exercises, quiz retries and notes:

```bash
node tests/student-experience.cjs
# Target a viewport or program when retesting a specific change:
REVIEW_WIDTHS=320 REVIEW_PROGRAMS=ai-agent-bootcamp node tests/student-experience.cjs
```

The harness creates synthetic learners and records their exact usernames in `/tmp/academy-student-ui-users.json` for cleanup. See `docs/verification.md` for the reviewed flows and representative reading screenshots.
