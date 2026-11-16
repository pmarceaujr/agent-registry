# Agent Registry

A backend service for registering AI agents and managing their configurations as **immutable, versioned releases**, with one-call **rollback**.

Think of it as a release manager for agent configs. Each change to an agent's model, prompt or settings is published as a new numbered version. Old versions are never edited, and you can switch the live version back (or forward) at any time.

## Why it's useful

- **Safe changes.** If a new prompt or model setting misbehaves, rolling back is a single API call. Nothing is copied or rewritten; the live-version pointer just moves.
- **Trustworthy history.** Versions can't be changed after they're published. The API has no update route, and a Postgres trigger rejects `UPDATE`s from *any* client, so "what config was live on March 3?" always has an accurate answer.
- **One source of truth.** Agent runtimes fetch `GET /versions/current` instead of hard-coding config.
- **Correct when requests overlap.** Simultaneous publishes for the same agent are serialized with a row lock, and a unique constraint acts as a backstop, so version numbers never collide.

## Tech stack

FastAPI · PostgreSQL 16 · SQLAlchemy 2.0 · Alembic · Pydantic v2 · psycopg 3 · Docker Compose

## Quick start

Requires Docker and Python 3.11+.

```bash
git clone <repo-url> agent-registry && cd agent-registry

# Python environment (used to run migrations)
python -m venv agreg
source agreg/Scripts/activate        # Windows Git Bash; on macOS/Linux: source agreg/bin/activate
pip install -r requirements.txt

# Start Postgres, apply migrations, start the API
docker compose up -d db
alembic upgrade head
docker compose up -d --build api

curl localhost:8000/health/db        # confirms the API can reach the database
```

Interactive API docs (Swagger UI): <http://localhost:8000/docs>

> Postgres is published on host port **55432** (to avoid clashing with local installs). Credentials in `docker-compose.yml` are for local development only.

## Usage example

```bash
# 1. Register an agent
curl -X POST localhost:8000/v1/agents -H "Content-Type: application/json" \
  -d '{"name":"support-bot","description":"Customer support assistant"}'
# -> returns the agent, including its "id"

# 2. Publish v1 and v2 (each publish becomes the live version)
curl -X POST localhost:8000/v1/agents/<id>/versions -H "Content-Type: application/json" \
  -d '{"config":{"model":"gpt-4o","temperature":0.2}}'
curl -X POST localhost:8000/v1/agents/<id>/versions -H "Content-Type: application/json" \
  -d '{"config":{"model":"gpt-4o","temperature":0.7}}'

# 3. See what's live
curl localhost:8000/v1/agents/<id>/versions/current          # -> v2

# 4. Roll back
curl -X POST localhost:8000/v1/agents/<id>/rollback -H "Content-Type: application/json" \
  -d '{"version_number":1}'
# -> {"previous_version_number":2,"current_version_number":1,...}
```

## API (all under `/v1`)

| Method | Path | What it does |
|---|---|---|
| POST | `/agents` | Register an agent (409 if the name is taken) |
| GET | `/agents` | List agents (`limit`, `offset`) |
| GET | `/agents/{id}` | Get one agent |
| PATCH | `/agents/{id}` | Update name/description (partial) |
| DELETE | `/agents/{id}` | Delete an agent and its versions |
| POST | `/agents/{id}/versions` | Publish a new immutable version; it becomes live |
| GET | `/agents/{id}/versions` | Version history, newest first |
| GET | `/agents/{id}/versions/current` | The live config |
| GET | `/agents/{id}/versions/{n}` | A specific version |
| POST | `/agents/{id}/rollback` | Make version `n` live (idempotent) |

## Design notes

- **Pointer-based rollback.** `agents.current_version_id` points at the live version. Rolling back moves the pointer and creates no new row, so version numbers keep increasing (rolling back to v1 and then publishing creates v3).
- **Immutability in two layers:** the API has no update route, and the `trg_agent_versions_immutable` trigger enforces it in the database. In production, the app should also run as a least-privilege database role, since a table owner can disable triggers.
- **Concurrency:** publish and rollback lock the agent row (`SELECT ... FOR UPDATE`), and `UNIQUE (agent_id, version_number)` backs that up.
- **Scoped lookups:** rollback only accepts versions that belong to the same agent.
- **Migrations:** hand-reviewed Alembic migrations, tested in both directions (`downgrade -1` / `upgrade head`).

## Roadmap

- [x] Agent CRUD, schema and migrations
- [x] Versioning, rollback, DB-enforced immutability
- [ ] Authentication with OIDC (Keycloak), role-based access, audit log
- [ ] pytest suite and GitHub Actions CI
- [ ] Azure deployment
