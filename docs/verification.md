# Course-book verification — 20 October 2026

The production app is running at http://127.0.0.1:8080/ with React/Nginx, Django REST/Gunicorn and PostgreSQL. The Vite preview at port 5173 now proxies to this Docker stack. Previously it used an older backend at port 8000 and could show stale courses; API parity is checked explicitly.

## What changed

The three practical paths now contain native course books: 238 concept, code-study and applied-case chapters across 60 sessions, 635 quiz questions, 905 flashcards, 180 reflection prompts and sixty specific input/output experiments. Chapter counts include code studies and cases; they are not a count of unique topics. Original client-delivery teaching and contextual exercises accompany selected, adapted MIT-licensed reference material. Each reader includes the license and teaching credit.

The learner reads actual explanations immediately, with a collapsible chapter index, implementation studies, worked cases and inline exercise material. Course-reader workbook calls to action were removed. These programs do not redirect to the reference repository or to GenAI Accelerator. The Accelerator remains independent.

## Observed checks

| Check | Result |
|---|---|
| Production build | TypeScript and Vite pass locally and in Docker |
| Full PostgreSQL regression suite | 19 tests pass; latest full run 26.665 seconds |
| Final content and upgrade checks | Two targeted PostgreSQL tests pass after editorial changes |
| All 60 readers | Substantive chapter bodies, own inline exercise material, expanded assessment, license and no repository redirects |
| Browser learner journey | Public syllabus, chapter selection, code studies, exercises, reflections, graded feedback, flashcards, practical evidence, notes, completion and reload pass in all three paths |
| Preview parity | Ports 5173 and 8080 expose identical PostgreSQL books and saved learner state; expired-token public catalog is covered |
| Restart persistence | Quiz results, reflections, flashcard confidence, submitted practical evidence and notes survived the Docker database/API/frontend restart |
| Privacy | Separate account cannot read another learner’s practice |
| Existing program | Independent Accelerator still opens its own 105-item curriculum |
| Layout | Desktop and phone checks pass; no uncaught browser errors or phone overflow |
| Upgrade preservation | Lesson identity, notes, enrollment, completion and earlier practice/quiz revisions survive recognized upgrades; instructor-edited text is retained |

A missing expanded assessment in the approval lesson was found during verification and corrected with additional teaching on exact approval revisions, atomic claims, idempotency, uncertain timeouts and external effects. Source-specific vendor capacity tables and broad performance claims were removed from adapted concept teaching; they were not measurements performed by this app.

## Reproduce

```sh
docker compose up -d --build --wait
docker compose exec -T backend python manage.py test academy --noinput
APP_URL=http://127.0.0.1:8080 PRACTICE_SNAPSHOT=/tmp/practical-ai-learning-state.json node tests/learning-studio.cjs
APP_URL=http://127.0.0.1:5173 node tests/preview-parity.cjs
docker compose restart db backend frontend
docker compose up -d --wait
APP_URL=http://127.0.0.1:8080 node tests/check-learning-persistence.cjs
```

Browser scripts use bundled Playwright and Chrome paths by default, overridable with PLAYWRIGHT_MODULE and CHROME_EXECUTABLE. They create synthetic learner accounts. Snapshot tokens stay in private temporary files and are not included in course downloads or images.

Coding practice runs in the learner’s scratch environment. The application records written evidence and grades its knowledge checks; it does not execute arbitrary learner code or certify submitted artifacts. No paid model inference was used. Source implementation chapters are code studies, not claims that every upstream integration was executed against a live provider.
