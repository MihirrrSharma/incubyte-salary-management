# Salary Management

## Overview

ACME's HR Manager needs a reliable alternative to spreadsheet-based salary management for employees across countries. This application provides a searchable employee directory, current salary updates, and compensation insights while keeping local-currency figures distinct.

## Features

- Employee directory with employee details from the selected record.
- Search, country/department/currency filters, server-side pagination, and sorting.
- Salary updates with currency-specific precision validation.
- Compensation analytics for headcount, country and department counts, and salary summaries and ranges grouped by currency.
- Deterministic command-line seed for 10,000 synthetic employees.

## Architecture

The frontend is React with TypeScript and Vite, using MUI and Recharts. It consumes JSON REST APIs from a Python/FastAPI backend. SQLAlchemy persists employee records in SQLite. Salary amounts are stored as integer minor units. Salary analytics remain grouped by local currency; no foreign-exchange conversion is performed.

## Project Structure

```text
backend/
  app/              # FastAPI routes, schemas, services, database and seed command
  tests/            # pytest API, analytics, salary and seed tests
frontend/
  src/              # React app, typed API client, employee and analytics views
docs/               # Product requirements, architecture and submission notes
pytest.ini
```

## Local Setup

Commands below are from the repository root. Use Python 3.10 or newer and Node.js/npm.

Create and activate a Python environment, then install backend dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

Seed the default 10,000 employees and start FastAPI:

```powershell
python -m backend.app.db.seed
python -m uvicorn app.main:app --app-dir backend --reload
```

In a second terminal from the repository root, install frontend dependencies and start Vite:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open the local URL printed by Vite. Its `/api` proxy forwards requests to FastAPI on `127.0.0.1:8000`. The SQLite database defaults to `salary_management.db` in the current working directory; set `DATABASE_URL` before seeding and starting the backend to use another location.

## Testing

Run from the repository root with the Python environment activated:

```powershell
python -m pytest backend
npm --prefix frontend test
npm --prefix frontend run build
```

The frontend build runs TypeScript project checking before Vite creates production assets.

## API Overview

- `GET /api/employees` — searchable, filtered, sorted, database-paginated employee directory.
- `PATCH /api/employees/{employee_id}/salary` — validate and persist an employee's current salary in the employee's existing currency.
- `GET /api/analytics/compensation` — filtered headcounts and salary metrics grouped by currency.

The current backend does not implement `GET /api/employees/{employee_id}`. The frontend drawer displays the selected employee record from the directory response and updates it using the salary PATCH response.

## AI-Assisted Development

AI tools assisted throughout development with design exploration, test generation, implementation, code review, and refinement. Requirements and architectural constraints guided the work; API slices were developed incrementally with tests written before their production behavior. Engineering decisions, requirements, tests, and final code were reviewed by the candidate. See [docs/ai-workflow.md](docs/ai-workflow.md) for the workflow reflected in the repository history.

## Design Decisions / Trade-offs

- SQLite keeps the assessment simple at the expected single-instance scale.
- Integer minor-unit storage avoids floating-point salary arithmetic.
- Salary metrics are grouped by local currency; no FX source or conversion requirement was specified.
- Pagination, filtering, and analytics execute in database queries.
- Authentication is outside the v1 requirements.
- No LLM chatbot is included: AI is used in development, while structured search and analytics meet the product requirements.

## Deployment

### Local Production Mode

Build the frontend from the repository root:

```powershell
npm --prefix frontend ci
npm --prefix frontend run build
```

With the Python environment activated, initialize an empty database and start FastAPI:

```powershell
python -m backend.app.db.seed --if-empty
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

When `frontend/dist` exists, FastAPI serves its assets, the React entry point, and SPA paths from the same origin as `/api`. `/docs` remains FastAPI Swagger UI.

### Railway

For a new Railway service, configure the following Build Command in the service settings. Do not rely on `railway.toml`; Railway's current documentation says new services cannot opt into Config-as-Code.

```sh
npm --prefix frontend ci && npm --prefix frontend run build
```

Configure this Start Command in the Railway service settings:

```sh
sh -c 'python -m backend.app.db.seed --if-empty && exec python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}'
```

Attach a persistent Railway volume to the service and set its mount path to `/data`. Railway supplies `RAILWAY_VOLUME_MOUNT_PATH` automatically. `DATABASE_URL` is optional: if unset, the application stores `salary_management.db` under that supplied mount path. To configure it explicitly, set `DATABASE_URL=sqlite:////data/salary_management.db`.

The seed runs conditionally at startup because Railway volumes are unavailable during pre-deploy. It initializes an empty employee table and preserves an initialized database on later starts. The SQLite file is generated on the mounted volume and is not committed to the repository; `*.db` is ignored. `.env.example` documents the optional local override and contains no secrets.

Python is pinned to 3.12 by `.python-version`; Railpack obtains Node.js 22 from `railpack.json`. The root `requirements.txt` shim installs `backend/requirements.txt`. Locally, when no Railway mount or `DATABASE_URL` is configured, the app continues to use `sqlite:///./salary_management.db` relative to the process working directory.

Deployment URL: TBD
Demo video: TBD