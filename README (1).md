# Task Tracker — FastAPI + CLI

A **split-architecture** task management application built for the Backend Development course. The project demonstrates clean-architecture principles by separating two completely independent programs:

| Layer | Technology | Responsibility |
|---|---|---|
| **Backend API** | FastAPI + SQLAlchemy | Business logic, data validation, persistence |
| **CLI Frontend** | argparse + requests + rich | User input/output only — never touches data directly |

---

## Project Structure

```
project_root/
│
├── backend/
│   ├── __init__.py       # Package marker
│   ├── database.py       # SQLAlchemy engine, session factory, Base, get_db()
│   ├── models.py         # Task ORM model → maps to `tasks` table in SQLite
│   ├── schemas.py        # Pydantic schemas: TaskCreate, TaskUpdate, TaskResponse
│   └── main.py           # FastAPI app + all route definitions
│
├── cli/
│   ├── __init__.py       # Package marker
│   └── cli.py            # Full CLI with argparse, requests, and rich formatting
│
├── requirements.txt      # Pinned dependencies
└── README.md             # This file
```

---

## Setup

### 1. Clone / download the project

```bash
cd project_root
```

### 2. Create and activate a virtual environment *(recommended)*

```bash
# macOS / Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Backend Server

```bash
uvicorn backend.main:app --reload
```

The server starts at `http://127.0.0.1:8000`. The SQLite database file (`task_tracker.db`) is created automatically in the project root on first launch.

> **Interactive docs** — open `http://127.0.0.1:8000/docs` in your browser to explore and test every endpoint without the CLI.

---

## CLI Commands

All CLI commands are run from the `project_root` directory **while the server is running in another terminal**.

### `add` — Create a new task

```bash
python -m cli.cli add "Write unit tests"
python -m cli.cli add "Deploy to staging" --priority high --desc "Use the prod config"
python -m cli.cli add "Read documentation" -p low
```

| Flag | Description | Default |
|---|---|---|
| `title` | *(positional)* Task title (1–120 chars) | required |
| `--priority / -p` | `low`, `medium`, or `high` | `medium` |
| `--desc / -d` | Optional longer description | `None` |

---

### `list` — List tasks

```bash
# All tasks
python -m cli.cli list

# Only high-priority incomplete tasks
python -m cli.cli list --priority high --completed false

# First 5 completed tasks
python -m cli.cli list --completed true --limit 5

# Skip the first 10 results (pagination)
python -m cli.cli list --limit 10 --offset 10
```

| Flag | Description | Default |
|---|---|---|
| `--priority / -p` | Filter by `low`, `medium`, or `high` | all |
| `--completed` | `true` or `false` | all |
| `--limit` | Max results returned (1–200) | `50` |
| `--offset` | Results to skip | `0` |

---

### `get` — Show details for one task

```bash
python -m cli.cli get 3
```

---

### `complete` — Mark a task as done

```bash
python -m cli.cli complete 3
```

---

### `update` — Edit task fields

All flags are optional; only the fields you provide are changed.

```bash
python -m cli.cli update 3 --title "New title" --priority high
python -m cli.cli update 3 --desc "Updated notes" --completed false
```

---

### `delete` — Permanently remove a task

```bash
# Interactive confirmation prompt
python -m cli.cli delete 3

# Skip the prompt (useful in scripts)
python -m cli.cli delete 3 --yes
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/tasks` | List tasks (supports `priority`, `completed`, `limit`, `offset`) |
| `GET` | `/tasks/{id}` | Get a single task |
| `POST` | `/tasks` | Create a task |
| `PATCH` | `/tasks/{id}` | Partially update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

### Query parameter examples (advanced querying bonus)

```
GET /tasks?priority=high&completed=false&limit=10
GET /tasks?limit=5&offset=0
```

---

## Bonus Features Implemented

| Feature | Details |
|---|---|
| **Database Persistence** | SQLite via SQLAlchemy 2.x ORM — data survives server restarts |
| **Polished UI** | `rich` library: colour-coded priority badges, rounded tables, panels for success/error messages |
| **Advanced Querying** | Server-side filtering by `priority` and `completed`; pagination with `limit`/`offset` |
| **Partial Updates** | `PATCH /tasks/{id}` lets the CLI update only the fields the user specifies |

---

## Architecture Notes

### Separation of Concerns

```
User types command
       │
       ▼
  cli/cli.py          ← Only handles I/O (argparse + rich)
       │  HTTP request (requests library)
       ▼
  backend/main.py     ← Routes + validation (FastAPI + Pydantic)
       │
       ▼
  backend/models.py   ← ORM (SQLAlchemy)
       │
       ▼
  task_tracker.db     ← Persistent storage (SQLite)
```

- The **CLI never imports** anything from `backend/`.
- The **backend never imports** anything from `cli/`.
- Communication is always over HTTP — just like a real production system where the frontend and backend run on separate machines.

### Data validation layers

1. **Pydantic** validates the JSON body before the route function runs (types, lengths, allowed values).
2. **SQLAlchemy** enforces non-null constraints at the database level as a second safety net.
3. **argparse** validates CLI arguments (choices, types) before any HTTP request is made.

---

## Grading Rubric Checklist

- [x] `POST /tasks` — create with Pydantic validation
- [x] `GET /tasks` + `GET /tasks/{id}` — retrieve all or one
- [x] `DELETE /tasks/{id}` — returns 204, 404 on missing ID
- [x] CLI with `argparse` + `requests`
- [x] Human-friendly `rich` output (tables, colour, panels)
- [x] SQLite persistence via SQLAlchemy
- [x] Advanced querying (`priority`, `completed`, `limit`, `offset`)
- [x] Comprehensive README with setup and usage
