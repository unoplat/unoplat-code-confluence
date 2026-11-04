"""Read-only Alembic revision readiness shared by both backend services.

Services never create, stamp or upgrade schema. A separate migration job owns
those changes. Each service calls verify_application_schema() with its own
engine before serving requests or polling Temporal, so the check observes the
same database and search_path as its ORM sessions. ORM tables are unqualified
and services configure no schema, so runtime support is public-only: a
connection resolving elsewhere fails instead of checking one schema and
querying another. ALEMBIC_SCHEMA remains for migrator reference builds only.
"""

import os
from typing import Final

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

RUNTIME_SCHEMA: Final[str] = "public"

# Exact revision this build requires. Update it with each schema release.
RELEASE_SCHEMA_REVISION: Final[str] = "0003_git_artifacts_contract"

# Earlier revisions this build's queries are known to work against. One may be
# selected explicitly for a staged rollout; anything else keeps startup blocked.
STAGED_SCHEMA_REVISIONS: Final[frozenset[str]] = frozenset(
    {"0002_git_artifacts_expand"}
)
STAGED_SCHEMA_REVISION_ENV: Final[str] = "APPLICATION_SCHEMA_STAGED_REVISION"


class SchemaNotReadyError(RuntimeError):
    """The database cannot serve this build. Messages never contain credentials."""


def expected_schema_revision() -> str:
    """Return the single revision this deployment accepts.

    Raises:
        SchemaNotReadyError: If the staged override names an unsupported revision.
    """
    staged_revision = os.environ.get(STAGED_SCHEMA_REVISION_ENV)
    if not staged_revision:
        return RELEASE_SCHEMA_REVISION
    if staged_revision not in STAGED_SCHEMA_REVISIONS:
        raise SchemaNotReadyError(
            f"{STAGED_SCHEMA_REVISION_ENV} names a revision this build does not "
            "support; unset it or deploy the matching build"
        )
    return staged_revision


async def verify_application_schema(engine: AsyncEngine) -> str:
    """Verify the exact Alembic revision through a read-only transaction.

    Args:
        engine: The engine the calling service uses for its ORM sessions.

    Returns:
        The verified revision.

    Raises:
        SchemaNotReadyError: If the database is unreachable, resolves to another
            schema, or has a missing, multiple-head or unexpected revision.
    """
    expected_revision = expected_schema_revision()
    current_schema: str | None = None
    version_table: str | None = None
    versions: list[str] = []
    try:
        async with engine.connect() as connection:
            async with connection.begin():
                await connection.execute(text("SET TRANSACTION READ ONLY"))
                await connection.execute(text("SET LOCAL lock_timeout = '5s'"))
                await connection.execute(text("SET LOCAL statement_timeout = '10s'"))
                current_schema = (
                    await connection.execute(text("SELECT current_schema()"))
                ).scalar()
                if current_schema == RUNTIME_SCHEMA:
                    version_table = (
                        await connection.execute(
                            text("SELECT to_regclass('public.alembic_version')::text")
                        )
                    ).scalar()
                if version_table is not None:
                    versions = list(
                        (
                            await connection.execute(
                                text("SELECT version_num FROM public.alembic_version")
                            )
                        ).scalars()
                    )
    except Exception as exc:
        # Driver errors can include connection details, so keep only the class.
        raise SchemaNotReadyError(
            f"Could not read the application schema revision ({type(exc).__name__}); "
            "check database connectivity and permissions"
        ) from None

    if current_schema != RUNTIME_SCHEMA:
        raise SchemaNotReadyError(
            f"Runtime connections resolve to schema {current_schema!r}, but backend "
            f"services support only {RUNTIME_SCHEMA!r}; fix the role search_path and "
            f"migrate with ALEMBIC_SCHEMA={RUNTIME_SCHEMA}"
        )
    if not versions:
        raise SchemaNotReadyError(
            f"No Alembic revision is recorded in {RUNTIME_SCHEMA}; run the migration "
            f"job for {expected_revision} with ALEMBIC_SCHEMA={RUNTIME_SCHEMA}. "
            "An existing unversioned database needs its audited adoption procedure"
        )
    if len(versions) > 1:
        raise SchemaNotReadyError(
            f"Multiple Alembic heads are recorded ({sorted(versions)}); this build "
            f"requires exactly {expected_revision}"
        )
    if versions[0] != expected_revision:
        raise SchemaNotReadyError(
            f"Database is at revision {versions[0]!r}, but this build requires "
            f"{expected_revision!r}; run the migration job or deploy the matching "
            "build. Do not stamp to bypass this check"
        )
    return expected_revision
