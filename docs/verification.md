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
