# Agent Registry and Admin Platform (flagship)

What it is:     
A backend service where AI agents are registered, configured, versioned, and administered. It has REST endpoints for creating agents, publishing immutable versions, rolling back, and managing configs, plus an admin API with role-based access and a full audit trail.

Stack:     
FastAPI, PostgreSQL, Alembic migrations, Redis, Docker, pytest, OIDC login via Keycloak.

What it does:     

Agent registration, configuration, versioning, and administration.
Schema design, migrations, and reliable data access.
Covers authN/authZ (OIDC and OAuth 2.0), input validation, and auditable admin actions.
Versioned APIs (/v1, /v2) hit a preferred qualification.
API documentation using OpenAPI docs and a README

Build Stages:     
Stage 1: data model, migrations, CRUD
Stage 2: versioning and rollback logic
Stage 3: auth, RBAC, audit log
Stage 4: tests, Docker, docs
Stage 5-6 (optional): API v2, polish
