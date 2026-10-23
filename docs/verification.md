# Student teaching review verification — 20 October 2026

The primary work was an editorial and exercise-alignment review of the three programs, documented in `student-content-audit.json` and `course-books.md`. Passing application tests does not establish good teaching. The prior raw-source assembly was replaced because it contained unrelated chapters, unsupported absolutes, malformed code and unavailable exercise dependencies.

## Observed content checks

- All 60 sessions were reviewed for their decision, prerequisites, worked example, task, expected outcome and assessment relevance. The audit records a specific defect and replacement for each session.
- The exact 41 published single-file Python examples were extracted from the generated reader content and executed in isolated temporary folders. All assertions passed and stdout matched the displayed observations, both locally and in the app's Python 3.12 container. No hidden reference implementation was substituted.
- All published Python fences parse; the revised core books contain no REPL `>>>` fragments, `NotImplementedError` stubs, missing `code/main.py` dependencies or broken phase-reference substitutions.
- The completed fictional benefit calculation reconciles to 90 minutes in the expected case, −130 in the conservative case and 230 in the optimistic case. Effort is 52.8 planned hours and illustrative support load 15 hours/month. These are labeled teaching assumptions, not real customer observations.
- Lesson-specific quiz questions check mechanisms and limitations demonstrated by the examples. Unrelated imported questions and cards were removed rather than retained to inflate inventory totals.

## Published Docker exercise

The seven exact files from bootcamp session 19 were built as a separate `academy-student-lab` Compose project. Observed:

1. DRF readiness queried PostgreSQL and returned HTTP 200 with database `postgresql`.
2. The browser form saved `reviewed-container-restart-proof`; reload retrieved the saved record through the API.
3. Force-recreating the lab backend preserved that record in PostgreSQL.
4. Stopping only the lab database made readiness return HTTP 503 with `database_unavailable`.
5. Starting the database restored readiness and the original saved record.
6. The recovery lesson’s exact `pg_dump` → separate `createdb` → `pg_restore` script passed. Source and restored IDs/body text matched, with nonempty source data.
7. The isolated lab's containers and synthetic volume were removed after verification. The academy database was not used for the outage exercise.

This is a loopback-only synthetic deployment-boundary experiment, with a plain browser page and no authentication. It is explicitly not a production template. Its complete files avoid requiring students to guess missing modules, and its limitations are taught beside the code.

## Application and delivery checks

The revised books are seeded into the local React/Nginx → Django REST/Gunicorn → PostgreSQL app at port 8080. Port 5173 proxies to the same data.

- PostgreSQL regression suite: **19 tests pass**. Includes private practice, server-side grading, earlier work preservation, protected instructor edits and generated-content upgrades.
- Full three-program learner journey: syllabus, chapters, exercises, saved reflections, grading, flashcards, practical submissions, notes, completion, reload, account isolation and independent Accelerator pass.
- Preview parity: ports 5173 and 8080 expose identical revised PostgreSQL curriculum and saved learner work; expired-token public catalog also passes.
- Frontend TypeScript/Vite production build passes after correcting a reader navigation defect: selecting the currently open lesson must not replace loaded content with its summary and remove the tabs.
- `student-reading.cjs` checks all rendered lesson chapters, full code fences, aligned exercise criteria, reflection prompts and quiz controls. The full pass succeeded: **60 lessons and 198 chapters**, every rendered code block intact. After the two final teaching refinements were published, the focused pass also succeeded for B20 and W06: **2 lessons, 6 chapters**. All 41 published single-file examples then passed again in Python 3.12, and both targeted PostgreSQL inventory/upgrade tests passed.

## Reproduce

```sh
python3 scripts/build_programs.py
python3 tests/student-content-audit.py
docker compose up -d --build --wait
docker compose exec -T backend python manage.py test academy --noinput
PRACTICE_SNAPSHOT=/tmp/practical-ai-reviewed-state.json node tests/learning-studio.cjs
PRACTICE_SNAPSHOT=/tmp/practical-ai-reviewed-state.json node tests/preview-parity.cjs
node tests/student-reading.cjs
```

Browser scripts use bundled Playwright/Chrome paths. They create synthetic learner accounts; private snapshot tokens stay in temporary files. The complete Docker exercise is reproduced from its lesson rather than substituted with the academy stack.

No paid model or real client system was used. Human factual-support review, usability, capstone integration, original learner implementations and client acceptance are not certified by these checks. The lessons explicitly ask students to collect those additional observations where required.

## Workshop coexistence — 2026-10-20

Practical AI Docker publishes localhost:8080; Workshop (`resume-studio`) publishes localhost:8000. Both were responding when inspected. Their private API/database container ports can be identical because they use different Docker networks.

Academy now uses the dedicated `ACADEMY_PORT` setting, and its existing local `.env` was migrated without changing port or database identity. `scripts/start.sh` pins the project name, Compose file, project directory and environment file. Native Django instructions use 8001 with an explicit Vite proxy instead of competing with Workshop on8000.

Observed verification:

- Started Academy from `/private/tmp` with deliberately conflicting inherited `APP_PORT=8000` and `COMPOSE_PROJECT_NAME=resume-studio`. It still published8080 under `practical-ai-academy` with the existing `practical-ai-academy_postgres_data` volume. API/database ports remained private.
- Restarted only Workshop's app while checking Academy health15 times. All checks returned200 with PostgreSQL, and the Academy catalog retained all four authored practical programs. Workshop recovered to health200 on8000.
- Separate browser tabs simultaneously rendered Academy's five-card catalog on8080 and Workshop sign-in on8000.
- Shell syntax and `git diff --check` passed. No workshop files or database volumes were changed.


## Learning workflow rollout — 2026-10-22

Docker frontend serves the academy on 127.0.0.1:8080; the PostgreSQL and backend services remain private. Migrations 0004 and 0005 applied without replacing existing program/lesson identities.

- Full backend suite: 47 tests passed in Docker against PostgreSQL.
- Updated experience regression suite: all 14 tests passed again against PostgreSQL after the empty-plan response fix.
- Frontend: TypeScript and production Vite build passed.
- tests/learning-workflows.cjs: full browser run passed. Verified public preview Python failure/success, browser Back/Forward, immediate navigation draft recovery, server autosave, chapter/direct-link reload, all three Bootcamp Python labs, blocked sandbox API access, stop execution, private versioned project submission, reference-file navigation, lesson questions, saved diagnostic plan, scheduled recall and mobile width. Screenshots: learning-workflow-dashboard.png and learning-workflow-mobile.png.
- Exact synthetic workflow accounts from the browser tests were removed after verification so sample questions/submissions do not appear as real student work.

Browser checks are reported practice evidence, not independently verified grades. Project review needs a staff reviewer. Lesson help is authored guidance, with no connected AI mentor. Optional sessions require actual staff scheduling. Password reset tokens and email content were tested with an in-memory mail backend; live delivery requires SMTP configuration. Real provider quality and cloud-scale capstone behavior were not retested by this rollout.

## Account and interface refresh — 2026-10-22

- Rebuilt the app with Docker and PostgreSQL; applied migration 0006 for tracked browser sessions, normalized new-account email identities and private bookmarks.
- Backend suite: 57 tests passed, including enforced CSRF on anonymous sign-in and authenticated writes, email login, session-only vs remembered cookie expiry, password/device revocation, session ownership, and private search/bookmarks/portfolio isolation.
- Real Chrome account journey: signup → saved lesson → search → dashboard/reload → profile → email login in a second device → device revocation → password change → sign out → requested lesson after sign-in → mobile dashboard. Verified no JavaScript-readable authentication token is created and the session cookie is HTTP-only.
- Visually inspected `refreshed-home.png`, `refreshed-sign-in.png`, `refreshed-dashboard.png` and `refreshed-mobile.png`. Responsive navigation, typography, focus indicators and forms retain the supplied sage/green/sand/cream identity.
- Password recovery delivery still requires SMTP credentials. Existing API token clients remain compatible; browser labs remain browser-reported practice results, and project review remains a human action.

- Complete learning workflow regression passed after the session/UI changes: actual public and authenticated Python failures/successes, all three Bootcamp labs, network isolation and stop, notes/reflections/chapter recovery, project evidence, help, planning and recall.
- Final Docker build also passed populated portfolio rendering, revision-status filters and evidence downloads. Synthetic test accounts and their tracked sessions were removed; real learner records were preserved. Migration drift check reported no changes.
