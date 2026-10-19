# API

All routes use `/api/`. JSON request/response bodies. Authenticated requests use `Authorization: Token <key>`.

| Route | Method | Access / behavior |
|---|---|---|
| `health/` | GET | Public database readiness; `database: postgresql` when connected; 503 on database failure |
| `programs/` | GET | Public program metadata and lesson summaries |
| `programs/<slug>/` | GET | Public single program |
| `auth/register/` | POST | username, email, password; password validation; auth throttle |
| `auth/login/` | POST | username, password; returns token |
| `auth/logout/` | POST | Revokes current token |
| `me/` | GET | Username, own enrollment IDs and completion IDs |
| `programs/<slug>/enroll/` | POST | Free idempotent enrollment |
| `lessons/<id>/` | GET | Enrolled lesson, source artifacts and own notes |
| `lessons/<id>/complete/` | POST / DELETE | Self-report or undo completion; enrollment required |
| `lessons/<id>/notes/` | PUT | Save own note; enrollment required; 10k limit |
| `projects/` | GET / POST | Own projects; creates deterministic blueprint |
| `projects/<id>/` | GET / DELETE | Own project only |
| `terminal/` | POST | Bounded command string; fixed simulation; never executes shell |
| `learning-kit/` | GET | Authenticated curated curriculum/starter ZIP |

Program editing is through Django admin. No learner ID or owner supplied by a client is trusted. Per-user unique constraints prevent duplicate enrollments/completions. Notes and projects are scoped to the authenticated user. Quiz answer references are educational source artifacts, not a secure graded assessment.
