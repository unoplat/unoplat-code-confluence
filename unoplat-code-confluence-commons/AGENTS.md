# AGENTS

## Purpose
Shared data models for the Code Confluence system. It captures repository structure (Python/TypeScript signatures), framework feature catalogs, package manager metadata, and workflow/agent snapshots that track ingestion and analysis progress.

## Primary Language & Tooling
- Language: Python
- Package manager: uv

## Common Commands
- Install: `uv sync` (see `Taskfile.yml`)
- Test: `uv run pytest -v tests/` (see `Taskfile.yml`)

## Key Dependencies
- cryptography: High-level recipes and low-level cryptographic primitives (Fernet, X.509, hazmat APIs).
- sqlalchemy: ORM + SQL Expression Language for DB connectivity, transactions, and schema management.
- pydantic: Typed data validation/models, JSON Schema, and custom validation/serialization.
- pytest: Test discovery, assertion introspection, and fixtures.
- pytest-asyncio: Asyncio-enabled pytest support for coroutine tests.
- sqlmodel: Pydantic + SQLAlchemy-based ORM models with validation and DB mappings.

## Domain References
See `business_logic_references.md` for model file locations and domain context.