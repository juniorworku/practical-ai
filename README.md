# Practical AI Education

A free learning academy built with Django REST Framework, PostgreSQL, React + TypeScript, Tailwind CSS 4, and Docker Compose. Original design inspired by the supplied program screenshot, with a public catalog and a working learner workspace.

## Start with Docker

```sh
cp .env.example .env
# Replace DJANGO_SECRET_KEY and POSTGRES_PASSWORD in .env.
docker compose up --build
```

Open http://localhost:8080. Create a free learner account. The API and PostgreSQL are private to the Compose network; only the frontend is published, on localhost. Database data persists in a named volume. Startup applies migrations and imports course content without overwriting instructor edits.

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
../.venv/bin/python manage.py runserver 127.0.0.1:8000
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open the Vite URL (normally http://localhost:5173). Vite forwards `/api` to Django. To develop against PostgreSQL, omit `USE_SQLITE`, configure the PostgreSQL variables from `.env.example`, and point `POSTGRES_HOST` at your local database. Shell development does not automatically read `.env`.

## Included

- AI Agent Bootcamp: eight weeks, 24 build sessions, approximately 50 hours.
- AI Workshops: six weeks, 18 project studios, approximately 50.5 hours.
- Freelancing Masterclass: six weeks, 18 delivery sessions, approximately 40 hours.
- Six runnable offline labs, 17 reference tests, synthetic fixtures, client-delivery templates, and 60 specific session deliverables.
- Full original workshop library: **523 chapters across 20 phases**, including source code and original quiz references.
- Original GenAI Accelerator: **85 catalog lessons + 20 labs**, including the added extension chapter; original materials describe 84 numbered core/advanced lessons. The import uses the actual catalog, not a hard-coded count.
- Eight-part Terminal Tutor guide, downloadable curriculum and original capstone starter.
- Learner registration/login/logout, idempotent enrollment and completion, persistent private lesson notes, searchable library and lessons.
- A saved project planner (deterministic guided template) and a safe, stateless terminal simulation.
- Four independent catalog programs with public syllabuses. The three practical programs include 60 substantive sessions, 238 teaching/code/case chapters, 635 quiz questions, 905 flashcards, 180 reflection prompts, guided exercises, acceptance checklists, private notes and inline input/output experiments.
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

This is a runnable first release, not a deployed public service. The original lessons, lab readings, source quiz references, notes and downloads are integrated; original model-powered feedback, cohort video calls, email/password recovery, certificates and community discussion are not ported. The three practical programs now include server-graded quizzes, flashcards, reflections and practical evidence submissions. The Accelerator planner makes no model call and Terminal Tutor simulation never runs a shell. Learners run capstone code separately. Progress is self-reported, not an assessment or certification.

For Docker verification, use `APP_URL=http://127.0.0.1:8080 EXPECT_DATABASE=postgresql node tests/browser-smoke.cjs` against a development stack. The browser suite reads all 60 program sessions, exercises each program, checks account isolation and token revocation, and downloads the full learning kit.

Build authored curriculum with `python3 scripts/build_programs.py`, then regenerate the public download using `python3 scripts/package_learning_kit.py`. The latter preserves a strict public-file allowlist. Recognized legacy introductory lessons are archived with their existing identities, notes, completions, and enrollments; they are excluded from active-course progress. Practical program rows are seeded by stable source IDs and instructor edits are retained.

Before public deployment, configure HTTPS and secure cookies, set `DEBUG=0`, use strong secrets and real hosts, configure trusted proxy/CSRF origins, add account recovery and email verification, use a shared throttle cache, and establish database backups. Development auth tokens are stored in tab-scoped sessionStorage; migrate to a reviewed secure cookie/session scheme for a public release. No live AI credentials or paid services are required.

Run `APP_URL=http://127.0.0.1:8080 node tests/learning-studio.cjs` to verify all seven activity sections, persisted results, independent curricula, chapter navigation, inline exercises and responsive layouts. See `docs/sources.md` for learning-interface research and palette attribution.

The three course books are built by `scripts/course_books/` from the pinned MIT source plus original academy teaching and cases. Learners read the content in the app; no GitHub redirect or workbook download is required. The license and teaching credit appear in each book. `docs/course-book-manifest.json` records the exact selection per session. Existing notes, enrollments and lesson identities are preserved during the recognized v3 upgrade; earlier practice revisions remain stored.

The Vite preview on port 5173 proxies to the Docker app on port 8080 by default, so both use the same PostgreSQL curriculum and learner state. For an intentionally separate native Django server, set `ACADEMY_API_PROXY=http://127.0.0.1:8000` before starting Vite.
