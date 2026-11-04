"""Exercise migrations only against a Docker-owned disposable PostgreSQL.

This suite never uses application connection configuration or existing volumes.
Run from query-engine: uv run --group test --group migrations pytest tests_migrations -v
"""

from argparse import Namespace
import asyncio
from collections.abc import Iterator
from io import StringIO
import json
from pathlib import Path
import shutil
import subprocess
import time
from uuid import uuid4

from alembic import command
from alembic.config import Config
import asyncpg
import pytest

from unoplat_code_confluence_query_engine.db.postgres.migration_metadata import (
    application_metadata,
)
from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactManifest,
)

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "0001_application_baseline"
EXPAND = "0002_git_artifacts_expand"
CONTRACT = "0003_git_artifacts_contract"
CONTRACT_FLAGS = ("drained=true", "discard_legacy_artifacts=true")
# Synthetic, migration-only fixtures that check values survive the contract. The SHA
# and digest are not verified historical identity, and no live file or API reads them.
SYNTHETIC_COMMIT_SHA = "a" * 40
SYNTHETIC_MANIFEST_JSON = json.dumps(
    [
        {
            "path": "backend/AGENTS.md",
            "kind": "markdown",
            "scope": "codebase",
            "codebase_name": "backend",
            "byte_length": 7,
            "sha256": "b" * 64,
        }
    ]
)


def migration_config(*flags: str) -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.cmd_opts = Namespace(x=list(flags))
    return config


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    if shutil.which("docker") is None:
        pytest.skip("Docker is required for isolated migration tests")
    name = f"unoplat-alembic-test-{uuid4().hex[:12]}"
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "--name",
            name,
            "-e",
            "POSTGRES_PASSWORD=migration-test-only",
            "-p",
            "127.0.0.1::5432",
            "postgres:17",
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        pytest.fail(f"Could not start isolated PostgreSQL: {result.stderr}")
    try:
        for _ in range(60):
            ready = subprocess.run(
                ["docker", "exec", name, "pg_isready", "-U", "postgres"],
                capture_output=True,
                timeout=5,
            )
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            pytest.fail("Disposable PostgreSQL did not become ready")
        address = subprocess.check_output(
            ["docker", "port", name, "5432/tcp"],
            text=True,
            timeout=5,
        ).strip()
        yield f"postgresql://postgres:migration-test-only@{address}/postgres"
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=30)


async def create_database(url: str, name: str) -> None:
    connection = await asyncpg.connect(url)
    try:
        await connection.execute(f'CREATE DATABASE "{name}"')
    finally:
        await connection.close()


@pytest.fixture
def database_url(postgres_url: str, monkeypatch: pytest.MonkeyPatch) -> str:
    name = f"migration_{uuid4().hex}"
    asyncio.run(create_database(postgres_url, name))
    url = postgres_url.rsplit("/", 1)[0] + "/" + name
    monkeypatch.setenv("ALEMBIC_DATABASE_URL", url)
    monkeypatch.setenv("ALEMBIC_SCHEMA", "public")
    return url


async def execute_sql(url: str, sql: str) -> list[asyncpg.Record]:
    connection = await asyncpg.connect(url)
    try:
        if sql.lstrip().upper().startswith("SELECT"):
            return await connection.fetch(sql)
        await connection.execute(sql)
        return []
    finally:
        await connection.close()


def query(url: str, sql: str) -> list[asyncpg.Record]:
    return asyncio.run(execute_sql(url, sql))


def seed_snapshot(
    url: str, progress: str = '{"architecture":100}', legacy_document: bool = True
) -> None:
    """Seed one finished run, with raw historical event and error text."""
    query(
        url,
        """
        INSERT INTO repository VALUES ('repo', 'owner', 'GITHUB_OPEN');
        INSERT INTO flag (id, name, status) VALUES (42, 'preserve-me', true);
        INSERT INTO codebase_config
          (repository_name, repository_owner_name, codebase_folder,
           programming_language_metadata)
        VALUES ('repo', 'owner', 'backend', '{"language":"python"}'::jsonb);
        INSERT INTO repository_workflow_run
          (repository_name, repository_owner_name, repository_workflow_run_id,
           repository_workflow_id, operation, status, error_report, started_at)
        VALUES ('repo', 'owner', 'run', 'workflow', 'AGENTS_GENERATION', 'COMPLETED',
          '{"error_message":"raw secret","stack_trace":"raw secret",
            "metadata":{"type":"ModelHTTPError","non_retryable":true,
              "next_retry_delay":"raw secret","model_error":{"body":"raw secret"},
              "details":[[{"agent":"dependency_guide","codebase":"backend",
                           "status_code":429,"traceback":"raw secret"},
                          {"agent":"raw secret"}]]}}'::jsonb,
          NOW());
        INSERT INTO codebase_workflow_run
          (repository_name, repository_owner_name, codebase_folder,
           codebase_workflow_run_id, codebase_workflow_id,
           repository_workflow_run_id, status, error_report, started_at)
        VALUES ('repo', 'owner', 'backend', 'child', 'child-workflow', 'run',
          'FAILED', '"raw secret"'::jsonb, NOW());
        INSERT INTO repository_agent_codebase_progress
          (repository_name, repository_owner_name, repository_workflow_run_id,
           codebase_name, next_event_id, latest_event_id, event_count, progress,
           completed_namespaces, created_at, modified_at)
        VALUES ('repo', 'owner', 'run', 'backend', 4, 3, 3, 55.5,
          '["dependency_guide"]'::jsonb, NOW(), NOW());
        INSERT INTO repository_agent_event
          (repository_name, repository_owner_name, repository_workflow_run_id,
           codebase_name, event_id, event, phase, message, tool_name, tool_call_id,
           tool_args, tool_result_content, created_at)
        VALUES
          ('repo', 'owner', 'run', 'backend', 1, 'dependency_guide', 'tool.call',
           'Tool call raw secret', 'write_file', 'call|1',
           '{"content":"raw secret"}'::jsonb, NULL, '2026-01-01T00:00:01+00'),
          ('repo', 'owner', 'run', 'backend', 2, 'dependency_guide', 'tool.result',
           'Tool result raw secret', 'raw secret', 'raw secret',
           NULL, 'raw secret', '2026-01-01T00:00:02+00'),
          ('repo', 'owner', 'run', 'backend', 3, 'raw secret', 'raw secret',
           'raw secret', NULL, NULL, NULL, NULL, '2026-01-01T00:00:03+00');
    """,
    )
    # Progress values are fixed test literals, never user-provided SQL.
    legacy_column = "agent_md_output, " if legacy_document else ""
    legacy_value = (
        f"""'{{"codebases":{{"backend":{{"document":"old body"}}}},
             "repository_activity_progress":{progress}}}'::jsonb, """
        if legacy_document
        else ""
    )
    query(
        url,
        f"""
        INSERT INTO repository_agent_md_snapshot
          (repository_name, repository_owner_name, repository_workflow_run_id,
           {legacy_column}statistics, overall_progress, created_at, modified_at)
        VALUES ('repo', 'owner', 'run', {legacy_value}
          '{{"usage":7}}'::jsonb, 100, NOW(), NOW());
    """,
    )


def test_registry_contains_every_table() -> None:
    assert set(application_metadata().tables) == {
        "ai_model_config",
        "code_confluence_codebase",
        "code_confluence_codebase_framework",
        "code_confluence_file",
        "code_confluence_file_framework_feature",
        "code_confluence_git_repository",
        "code_confluence_package_manager_metadata",
        "codebase_config",
        "codebase_workflow_run",
        "credentials",
        "feature_absolute_path",
        "flag",
        "framework",
        "framework_feature",
        "repository",
        "repository_agent_codebase_progress",
        "repository_agent_event",
        "repository_agent_md_snapshot",
        "repository_workflow_run",
    }


def test_fresh_upgrade_matches_metadata(database_url: str) -> None:
    config = migration_config(*CONTRACT_FLAGS)
    command.upgrade(config, CONTRACT)
    command.upgrade(config, CONTRACT)
    command.check(config)
    assert (
        query(database_url, "SELECT version_num FROM alembic_version")[0][0] == CONTRACT
    )


@pytest.mark.parametrize(
    "progress, expected",
    [
        ('{"architecture":100}', '{"architecture": 100}'),
        ("null", "{}"),
        ("[]", "{}"),
    ],
)
def test_existing_baseline_preserves_other_data(
    database_url: str,
    progress: str,
    expected: str,
) -> None:
    command.upgrade(migration_config(), BASELINE)
    seed_snapshot(database_url, progress)
    # Simulate verified, unversioned pre-Alembic tables. This fixture's schema
    # was just created by the frozen baseline; real databases need an audit.
    query(database_url, "DROP TABLE alembic_version")
    command.stamp(migration_config("baseline_verified=true"), BASELINE)
    command.upgrade(migration_config("drained=true"), EXPAND)
    row = query(database_url, "SELECT * FROM repository_agent_md_snapshot")[0]
    assert row["repository_activity_progress"] == expected
    assert row["artifact_commit_sha"] is None
    assert row["artifact_manifest"] is None
    assert row["artifact_publication_error"] is None
    assert row["statistics"] == '{"usage": 7}'
    assert query(database_url, "SELECT name FROM flag")[0][0] == "preserve-me"
    assert query(database_url, "SELECT COUNT(*) FROM repository")[0][0] == 1

    # Saved identity and PR metadata must survive the contract untouched.
    query(
        database_url,
        f"""
        UPDATE repository_agent_md_snapshot
        SET artifact_commit_sha = '{SYNTHETIC_COMMIT_SHA}',
            artifact_manifest = '{SYNTHETIC_MANIFEST_JSON}'::jsonb,
            pr_metadata = '{{"pr_number":7}}'::jsonb
    """,
    )
    timestamps = query(
        database_url,
        "SELECT created_at, modified_at FROM repository_agent_md_snapshot",
    )[0]
    event_order = "SELECT * FROM repository_agent_event ORDER BY event_id"
    created_at = [row["created_at"] for row in query(database_url, event_order)]

    # drained=true alone is not enough, and the failure changes nothing.
    with pytest.raises(Exception, match="discard_legacy_artifacts=true"):
        command.upgrade(migration_config("drained=true"), CONTRACT)
    assert (
        query(database_url, "SELECT version_num FROM alembic_version")[0][0] == EXPAND
    )
    assert "agent_md_output" in query(
        database_url, "SELECT * FROM repository_agent_md_snapshot"
    )[0].keys()

    command.upgrade(migration_config(*CONTRACT_FLAGS), CONTRACT)
    row = query(database_url, "SELECT * FROM repository_agent_md_snapshot")[0]
    assert "agent_md_output" not in row.keys()
    assert row["repository_activity_progress"] == expected
    assert row["statistics"] == '{"usage": 7}'
    assert row["artifact_commit_sha"] == SYNTHETIC_COMMIT_SHA
    assert json.loads(row["artifact_manifest"]) == json.loads(SYNTHETIC_MANIFEST_JSON)
    ArtifactManifest.model_validate_json(row["artifact_manifest"])
    assert json.loads(row["pr_metadata"]) == {"pr_number": 7}
    assert (row["created_at"], row["modified_at"]) == tuple(timestamps)

    events = query(database_url, event_order)
    assert [event["event_id"] for event in events] == [1, 2, 3]
    assert [event["created_at"] for event in events] == created_at
    assert [event["message"] for event in events] == [
        "Tool call started",
        "Tool call finished",
        "Agent event recorded",
    ]
    assert [event["tool_name"] for event in events] == ["write_file", None, None]
    assert [event["tool_call_id"] for event in events] == ["call|1", None, None]
    assert [event["event"] for event in events][2] == "unknown"
    assert [event["phase"] for event in events][2] == "unknown"
    assert all(
        event["tool_args"] is None and event["tool_result_content"] is None
        for event in events
    )

    parent_report = query(
        database_url, "SELECT error_report FROM repository_workflow_run"
    )[0][0]
    child_report = query(
        database_url, "SELECT error_report FROM codebase_workflow_run"
    )[0][0]
    # Error reports keep their full message, stack trace and metadata so users
    # can still submit complete error details.
    assert json.loads(parent_report) == {
        "error_message": "raw secret",
        "stack_trace": "raw secret",
        "metadata": {
            "type": "ModelHTTPError",
            "non_retryable": True,
            "next_retry_delay": "raw secret",
            "model_error": {"body": "raw secret"},
            "details": [
                [
                    {
                        "agent": "dependency_guide",
                        "codebase": "backend",
                        "status_code": 429,
                        "traceback": "raw secret",
                    },
                    {"agent": "raw secret"},
                ]
            ],
        },
    }
    assert json.loads(child_report) == "raw secret"
    progress_row = query(
        database_url, "SELECT * FROM repository_agent_codebase_progress"
    )[0]
    assert progress_row["event_count"] == 3
    assert json.loads(progress_row["completed_namespaces"]) == ["dependency_guide"]
    assert query(database_url, "SELECT name FROM flag")[0][0] == "preserve-me"
    assert "raw secret" not in " ".join(
        str(tuple(event.values())) for event in events
    )

    # Nothing can claim to restore what the contract discarded.
    with pytest.raises(RuntimeError, match="no downgrade can restore"):
        command.downgrade(migration_config(*CONTRACT_FLAGS), EXPAND)
    assert (
        query(database_url, "SELECT version_num FROM alembic_version")[0][0] == CONTRACT
    )


@pytest.mark.parametrize(
    "assignment",
    [
        "artifact_commit_sha = 'invalid'",
        "artifact_commit_sha = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'",
        "artifact_manifest = '{}'::jsonb",
        "repository_activity_progress = '[]'::jsonb",
        "artifact_publication_error = '[]'::jsonb",
    ],
)
def test_artifact_constraints(database_url: str, assignment: str) -> None:
    command.upgrade(migration_config(*CONTRACT_FLAGS), CONTRACT)
    seed_snapshot(database_url, legacy_document=False)
    with pytest.raises(asyncpg.CheckViolationError):
        query(database_url, f"UPDATE repository_agent_md_snapshot SET {assignment}")


def test_reservation_index_allows_queue_but_rejects_active_conflict(
    database_url: str,
) -> None:
    command.upgrade(migration_config(*CONTRACT_FLAGS), CONTRACT)
    seed_snapshot(database_url, legacy_document=False)
    query(database_url, "UPDATE repository_workflow_run SET status = 'RUNNING'")
    query(
        database_url,
        """
        INSERT INTO repository_workflow_run
          (repository_name, repository_owner_name, repository_workflow_run_id,
           repository_workflow_id, operation, status, started_at)
        VALUES ('repo', 'owner', 'queued-1', 'workflow', 'INGESTION', 'SUBMITTED', NOW()),
               ('repo', 'owner', 'queued-2', 'workflow', 'AGENT_MD_UPDATE', 'SUBMITTED', NOW());
    """,
    )
    with pytest.raises(asyncpg.UniqueViolationError):
        query(
            database_url,
            "UPDATE repository_workflow_run SET status = 'RUNNING' WHERE repository_workflow_run_id = 'queued-1'",
        )


def test_explicit_schema(database_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    query(database_url, "CREATE SCHEMA application")
    monkeypatch.setenv("ALEMBIC_SCHEMA", "application")
    config = migration_config(*CONTRACT_FLAGS)
    command.upgrade(config, CONTRACT)
    command.check(config)
    assert (
        query(database_url, "SELECT version_num FROM application.alembic_version")[0][0]
        == CONTRACT
    )
    assert query(database_url, "SELECT to_regclass('public.repository')")[0][0] is None


def test_offline_sql_does_not_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "ALEMBIC_DATABASE_URL", "postgresql://unused:unused@localhost:1/offline"
    )
    monkeypatch.setenv("ALEMBIC_SCHEMA", "public")
    config = migration_config(*CONTRACT_FLAGS)
    config.output_buffer = StringIO()
    command.upgrade(config, CONTRACT, sql=True)
    sql = config.output_buffer.getvalue()
    assert "CREATE TABLE" in sql
    assert sql.index("pg_advisory_xact_lock") < sql.index("CREATE TABLE")
    assert "SET LOCAL unoplat.git_artifacts_drained = 'true'" in sql
    assert "SET LOCAL unoplat.git_artifacts_discard_legacy = 'true'" in sql
    # Gates, locks and drain checks all come before any cleanup or the drop.
    assert (
        sql.index("current_setting('unoplat.git_artifacts_discard_legacy', true)")
        < sql.index("LOCK TABLE\n          repository_workflow_run")
        < sql.index("child codebase workflows")
        < sql.index("UPDATE repository_agent_event")
        < sql.index("DROP COLUMN agent_md_output;")
    )
    assert "DROP COLUMN agent_md_output CASCADE" not in sql

    # Generated without the acknowledgement, the SQL fails its own gate when run.
    unacknowledged = migration_config("drained=true")
    unacknowledged.output_buffer = StringIO()
    command.upgrade(unacknowledged, CONTRACT, sql=True)
    gated_sql = unacknowledged.output_buffer.getvalue()
    assert "SET LOCAL unoplat.git_artifacts_discard_legacy" not in gated_sql
    assert "current_setting('unoplat.git_artifacts_discard_legacy', true)" in gated_sql


def test_missing_drain_rolls_back_entire_upgrade(database_url: str) -> None:
    with pytest.raises(Exception, match="drained=true"):
        command.upgrade(migration_config(), CONTRACT)
    assert query(database_url, "SELECT to_regclass('repository')")[0][0] is None
    # A first bootstrap also rolls back as one transaction without the acknowledgement.
    with pytest.raises(Exception, match="discard_legacy_artifacts=true"):
        command.upgrade(migration_config("drained=true"), CONTRACT)
    assert query(database_url, "SELECT to_regclass('repository')")[0][0] is None


def test_unverified_stamp_is_rejected(database_url: str) -> None:
    command.upgrade(migration_config(), BASELINE)
    query(database_url, "DROP TABLE alembic_version")
    with pytest.raises(RuntimeError, match="schema/data audit"):
        command.stamp(migration_config(), BASELINE)
    assert query(database_url, "SELECT to_regclass('alembic_version')")[0][0] is None


def test_queued_mutator_blocks_expand(database_url: str) -> None:
    command.upgrade(migration_config(), BASELINE)
    seed_snapshot(database_url)
    query(database_url, "UPDATE repository_workflow_run SET status = 'SUBMITTED'")
    with pytest.raises(Exception, match="Drain queued/active"):
        command.upgrade(migration_config("drained=true"), EXPAND)
    assert (
        query(database_url, "SELECT version_num FROM alembic_version")[0][0] == BASELINE
    )
    assert (
        query(
            database_url,
            """
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = 'repository_agent_md_snapshot'
          AND column_name = 'artifact_manifest'
    """,
        )[0][0]
        == 0
    )

    # Contract repeats the parent check and also checks children on their own.
    query(database_url, "UPDATE repository_workflow_run SET status = 'COMPLETED'")
    command.upgrade(migration_config("drained=true"), EXPAND)
    query(database_url, "UPDATE repository_workflow_run SET status = 'SUBMITTED'")
    with pytest.raises(Exception, match="queued/active checkout mutators"):
        command.upgrade(migration_config(*CONTRACT_FLAGS), CONTRACT)
    # Old code could mark a parent ERROR while its siblings were still running.
    query(
        database_url,
        """
        UPDATE repository_workflow_run SET status = 'ERROR';
        UPDATE codebase_workflow_run SET status = 'RUNNING';
    """,
    )
    with pytest.raises(Exception, match="child codebase workflows"):
        command.upgrade(migration_config(*CONTRACT_FLAGS), CONTRACT)
    assert (
        query(database_url, "SELECT version_num FROM alembic_version")[0][0] == EXPAND
    )
    assert (
        query(
            database_url,
            "SELECT COUNT(*) FROM repository_agent_event WHERE tool_args IS NOT NULL",
        )[0][0]
        == 1
    )
    assert "agent_md_output" in query(
        database_url, "SELECT * FROM repository_agent_md_snapshot"
    )[0].keys()
