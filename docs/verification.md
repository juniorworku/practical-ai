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

## Live password-recovery email — 2026-10-23

- Configured the user-supplied Gmail SMTP credentials in the ignored local `.env`, with mode 0600. STARTTLS authentication on port 587 succeeded. No credential values were printed or added to repository files.
- Added implicit-SSL support, mutually exclusive encryption flags, bounded SMTP timeouts, an explicit one-hour reset expiry, branded HTML plus plain-text email, sanitized delivery-failure reporting and a `check_email` management command.
- 31 targeted PostgreSQL tests passed across recovery, account/session and learning-workflow suites. Coverage includes canonical link origin, both message alternatives, expiry, weak passwords, single-use links, token/session revocation and sanitized SMTP failures.
- Real browser-to-inbox-to-browser verification passed: created one synthetic learner at a controlled Gmail test alias, saved learning progress, requested recovery through the app UI, confirmed the actual message arrived in Gmail's INBOX, extracted only that test email's delivered link, opened it in Chrome, changed the password and logged in with the new password. The old password and browser session were rejected, link reuse failed and saved learning progress remained intact.
- Real delivery is configured for the local origin `http://127.0.0.1:8080`. A hosted release requires the actual public HTTPS origin in `ACADEMY_PUBLIC_URL`. No SMTP details remain missing for local use.
- The temporary synthetic learner, associated browser sessions and private local test-link/state files were removed after verification. The test email remains in the owner's inbox.

## Six-program credits removal audit — 2026-10-23

A real Chrome audit against the running Docker/PostgreSQL app checked all six public program overviews, all six public lesson previews and every signed-in lesson page:

| Program | Signed-in lesson pages | Preview chapters checked |
|---|---:|---:|
| AI Agent Bootcamp | 24 | 6 |
| AI Workshops | 18 | 6 |
| Freelancing Masterclass | 18 | 7 |
| AI Engineering | 36 | 7 |
| GenAI Accelerator | 105 | 6 |
| Terminal Tutor | 8 | 8 |
| Total | 209 | 40 |

- The removed “Teaching credits & license” section, source-snapshot sentence and quoted copyright/license block were absent from every rendered page checked. No frontend component still references the removed attribution display. Source/license metadata remains in the underlying provenance records and downloadable source notices.
- All 40 preview chapters and their exercise controls worked. All 209 signed-in lessons loaded their teaching, and their complete teaching payloads were scanned for the removed text, excluding the retained attribution metadata.
- In the first lesson of each program, traversed all chapter navigation and exercised inline hints, questions, quiz submission with per-question feedback, flashcard reveal/next, practical-task controls, notes saving and reading completion. Reload retained both notes and reading progress for all six programs.
- All six overview syllabuses retained their expected lesson counts and preview controls. The Terminal Tutor reader also fit a 390px mobile viewport without page overflow.
- No JavaScript errors or failed API requests occurred during the full preview/lesson/activity audit. No additional application fixes were needed. Removed the single synthetic learner and its sessions after verification; real learner records were untouched.

## Favicon, interaction and motion refresh — 2026-10-23

- Created a vector favicon matching the layered forest/sage/cream academy mark, with 16/32/48px PNG and multi-resolution ICO fallbacks, a 180px Apple touch icon, 192/512px home-screen icons and web manifest. Browser checks validated asset responses, PNG dimensions and ICO entries.
- All six independent programs now appear in the public catalog. Verified keyword search, category filtering, result counts, no-match feedback and reset behavior. Lesson search now offers a clear recovery action when there are no matches.
- Added short page transitions, scroll-triggered card/section reveals, hover/press feedback, dialog/accordion/learning-feedback animations and a back-to-top control. Content is never hidden behind a pending reveal. Verified real Web Animations API calls with motion enabled and no new motion calls/CSS transitions after switching to reduced motion.
- Verified mobile sign-in visibility, menu focus on opening, Escape restoration and outside dismissal; also tested skip-to-main without changing the app route, meaningful page titles, keyboard global search, modal scroll restoration, and terminal command history with unfinished-draft restoration.
- Fixed opening the current lesson from global search replacing its full teaching with an unloaded catalog summary. Verified its chapter reader and quiz tabs remain available after keyboard search.
- Lazy-loaded lesson, preview, search, account, portfolio and learning-hub code. The main JavaScript entry chunk decreased from approximately 504 kB to 292 kB before gzip (about 42%); other code loads when needed. Production Docker build passed without the prior oversized-entry-chunk warning.
- Added a recoverable page-load error screen. A real browser intentionally blocked a preview module, received the fallback, then successfully loaded the lesson after removing the block and using Reload.
- `tests/ui-interactions.cjs`, `tests/account-workspace.cjs` and `tests/learning-workflows.cjs` passed against the running Docker/PostgreSQL app. Regression coverage includes session security, portfolio filters/export, deep-link return, autosave/recovery, all three executable Bootcamp browser labs, sandbox restrictions, stopping execution, questions, project evidence and review planning.
- Visually checked the favicon and desktop/mobile screenshots. The removed teaching-credit/license block remains absent. Synthetic test accounts and their tracked sessions were removed; existing learner records and SMTP configuration were preserved.

## Student UI review across six programs — 2026-10-23

Reviewed AI Agent Bootcamp, AI Workshops, Freelancing Masterclass, AI Engineering, GenAI Accelerator and Terminal Tutor in Chrome against the running Docker/PostgreSQL app at 1440×1000, 390×844 and 320×844. The 320px run used reduced motion. This was a responsive browser review; it did not use physical iOS or Android devices.

- Read every chapter in each program's first, middle and final lesson at all three widths: 54 lesson visits and 360 chapter views. Visually inspected desktop and mobile reading screenshots for each program.
- Completed the first lesson's guided activity flow in every program at every width: exercise hints, saved reflection, graded quiz with per-question feedback, retry and partially answered reload, flashcard reveal/navigation, saved practical-task evidence, saved notes/reload and next-lesson navigation. These were synthetic student reports, not claims that the tester completed production deployments.
- Checked all six preview routes at all three widths, including chapter selection and the exercise handoff. The removed credits/source-snapshot section remained absent.
- Fixed chapter selection competing with restored scroll positions. Explicit selections now close Contents, focus the new chapter heading and move directly to the reading. Saved scroll restoration remains available when reopening a chapter.
- Fixed the exercise and quiz-review handoffs retaining an unrelated position partway down the page. Their activity panels now receive focus and scroll into view. Next-lesson/sidebar navigation focuses the loaded lesson heading.
- Fixed quiz reloads combining edited answers with a previous attempt's feedback. New attempts and answer drafts persist separately from the last graded result; checking answers is disabled while saving.
- Improved reading text to 15px, code to 13px, touch targets and mobile form text. Code blocks and activity panels are keyboard-focusable. Task evidence has a stable explicit accessible label. Changing chapters resets code-copy feedback.
- Fixed signed-in header overflow at 320px that had pushed the navigation toggle off-screen. Verified the corrected page width is exactly 320px, with no horizontal page overflow in any of the six programs' reviewed chapters or activities.
- `tests/student-experience.cjs` records the repeatable six-program audit; optional `REVIEW_WIDTHS`, `REVIEW_PROGRAMS` and `REVIEW_TAG` select a targeted run. Existing chapter-reading harnesses now reopen Contents after its new automatic dismissal.
- `tests/ui-interactions.cjs` passed: actual motion, reduced-motion switching, keyboard search, skip link, mobile menu focus/Escape/outside dismissal, terminal history and failed-page recovery. `tests/learning-workflows.cjs` passed: all three executable Python labs, failure/success feedback, sandbox network boundary, stop execution, notes/draft recovery, chapter resume, project evidence, lesson help and review planning.
- Production Docker build (TypeScript and Vite) and `git diff --check` passed. Synthetic review accounts and their tracked sessions were removed after testing; existing students and their saved work were preserved.

Representative screenshots: `docs/screenshots/student-reader-desktop.png`, `student-reader-mobile.png` and `student-reader-narrow.png`.

## Documentation course redesign and advanced Python — 2026-10-23

- Adapted the learner-supplied Datalumina screenshots and retrieved reference content into a navy/mint course interface. Source evidence and intentional differences are recorded in `DESIGN.md`; no claim is made that live computed styles were extracted.
- Installed actual shadcn/ui registry components with Tailwind v4 and Radix primitives. Courses now have horizontal module navigation, a grouped/searchable lesson path, progress, a central chapter reader and an active section outline. Phone course contents use a keyboard-accessible Sheet; public previews retain an inline section outline.
- Added the independent advanced Python for AI program: 12 sessions, 62 chapters, 36 distinct scenario quiz questions, 36 flashcards and approximately 52 planned practice hours. Entry requirements are working Python, HTTP/JSON, testing and basic SQL. Each session teaches the mechanism, supplies complete runnable code, then assigns a matching variation with negative cases and a complete reference solution.
- Executed every baseline and reference variation with Python 3.12. All 24 examples passed. The seven integrated capstone unit tests passed both on the host and inside its Docker image.
- Exercised the actual capstone container over HTTP: readiness, authenticated owner isolation, supported answers and abstention, versioned cache hits, cache survival after container replacement, invalid credentials, exact request schema, query/batch/body bounds and per-owner quota. All passed. Removed its temporary container and state volume afterward.
- The deterministic provider is explicitly an offline fixture. A complete optional Ollama adapter is taught and published, but real model inference, semantic quality and production load capacity were not tested. The reference HTTP server and process-local quotas are explicitly scoped to a local teaching deployment.
- `tests/course-layout.cjs` passed for all seven programs at 1440×1000, 390×844 and 320×844 (reduced motion at 320px): module navigation, grouped lesson selection/search, Sheet dismissal and focus return, section jumps, exercise hints, quiz feedback, notes saving and reload. No horizontal overflow, JavaScript errors or failed API calls occurred. All 12 advanced lesson contracts and the six published capstone files were checked through the authenticated API.
- Visual review caught and fixed the legacy workspace grid collapsing the new reading column, progress overlapping the section outline, remaining pale surfaces and low-contrast code/terminal/feedback text. Final representative course captures are `docs/screenshots/course-redesign-1440.png`, `course-redesign-390.png`, `course-redesign-320.png` and `course-redesign-home.png`.
- Final deployed visual checks passed for all seven public previews, all three reader widths, outline/progress separation and readable editor/terminal text. `tests/learning-workflows.cjs` passed against PostgreSQL: actual failing/passing browser Python, all three executable Bootcamp labs, network isolation, stop execution, saved notes/reflections, chapter resume, project evidence, lesson questions and review planning. `tests/ui-interactions.cjs` passed: seven-program catalog, actual animations/reduced motion, keyboard search, menu focus/dismissal, terminal history and recoverable failed page loading.
- Final TypeScript/Vite Docker builds and `git diff --check` passed. This was Chrome responsive testing, not physical-device or Safari testing. Temporary preview processes, synthetic learners and tracked sessions were cleaned up; the Docker academy remains running on port 8080. Existing learner records, the workshop app and SMTP settings were preserved.

## Python for AI student-depth review and selective engineering briefs — 2026-10-23

See `docs/python-ai-student-review.md` for the lesson-by-lesson findings, teaching corrections and intended advanced entry level.

- Reviewed and expanded all 12 sessions to 77 chapters, including 11 complete advanced studios, cumulative pipeline/evaluation/HTTP implementation slices, 60 distinct scenario questions and 60 flashcards. Exercises include their full primary variation, assigned negative cases, studio evidence and specific diagnostic feedback. Approximately 67 planned practice hours cover implementation, measurement and review.
- Ran 47 published Python examples/reference blocks from the actual lesson JSON, including the complete offline HTTPX adapter. Reconstructed the capstone in a fresh directory from its printed files and passed all 25 unit/HTTP/adapter/evaluation tests. The measured evaluator passed six fixed cases over twenty repetitions (120 local observations); this is explicitly not a 120-case independent dataset or representative production load.
- All 25 capstone tests also passed in its nonroot Docker image. Actual container HTTP checks passed for readiness, scoped answering/abstention, credentials, malformed/oversized input, quota and persisted cache after container recreation. The temporary container/volume were removed. The published snapshot-restore Python block and exact local credential-generation/source commands were independently executed in a temporary workspace; credential contents were not printed.
- Applied the engineering brief only to Bootcamp, Workshops, AI Engineering, GenAI Accelerator and Python for AI. Python has six explicit stage-specific contracts. Workshops retain their own studio use cases; Bootcamp’s API/data stage no longer receives an unrelated calendar-agent assignment. Freelancing and Terminal Tutor keep contextual teaching without the dense engineering overview block.
- Fixed generated-release recognition: exact older authored Python text/quiz variants were safely registered, and future generation records authored hashes before replacement. Four Django regression tests passed in a separate test database, including notes/completion/lesson identity preservation and preservation of an unrecognized instructor edit. Verified all 12 original database lesson IDs remained unchanged and all 12 served content hashes/learning revisions match the reviewed authoring source.
- Advanced quiz feedback now carries an explicit valid review chapter. The generic reader retains a fallback for courses without this metadata; advanced Python answers lead to their actual studio. The category-independent overview now recognizes Python’s full teaching, quiz and flashcard counts.
- TypeScript/Vite Docker builds, scope checks and `git diff --check` passed. Optional real Ollama inference, semantic model quality, representative public-hosting capacity and physical-device/Safari behavior remain untested; no claim is made that fixture, source-ID or mock-transport checks establish those results.
- `tests/python-ai-student.cjs` passed against the final Docker/PostgreSQL app: all 77 teaching chapters across all 12 lessons, every full reference panel and stage-specific hint, intentionally wrong advanced answers with correct remediation handoff, all 60 correct graded answers, flashcard feedback, notes saving/reload and all 11 capstone files matching source. All seven overview pages showed engineering briefs only for the five selected programs. Targeted 390px and 320px reduced-motion readers and course Sheet dismissal passed with no page overflow, JavaScript errors or failed API calls. Representative advanced reading captures are `docs/screenshots/python-depth-1440.png`, `python-depth-390.png` and `python-depth-320.png`.
- Removed the exact synthetic depth-review learner and its tracked sessions after verification; existing learners and workshop/SMTP configuration were preserved. The academy remains running on port 8080.
