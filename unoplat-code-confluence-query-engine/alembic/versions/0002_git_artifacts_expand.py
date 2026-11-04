# ruff: noqa: INP001
"""Add Git artifact identity and repository activity progress.

Historical document bytes are not converted into guessed Git identities.
This revision retains the legacy column only until application cleanup; it
introduces no application read fallback. The later contract discards its data.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_git_artifacts_expand"
down_revision = "0001_application_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '5s'")
    op.execute("""
        DO $$ BEGIN
          IF current_setting('unoplat.git_artifacts_drained', true)
               IS DISTINCT FROM 'true' THEN
            RAISE EXCEPTION 'Pause starts, drain affected Temporal histories, reconcile DB rows, then pass -x drained=true';
          END IF;
        END $$
    """)
    op.execute("""
        LOCK TABLE repository_workflow_run, repository_agent_md_snapshot
        IN ACCESS EXCLUSIVE MODE
    """)
    op.execute("""
        DO $$ BEGIN
          IF EXISTS (
            SELECT 1 FROM repository_workflow_run
            WHERE status IN ('SUBMITTED', 'RUNNING', 'RETRYING')
              AND operation IN ('INGESTION', 'AGENTS_GENERATION', 'AGENT_MD_UPDATE')
          ) THEN
            RAISE EXCEPTION 'Drain queued/active checkout mutators and reconcile stale rows against Temporal before expand';
          END IF;
        END $$
    """)
    op.add_column(
        "repository_agent_md_snapshot",
        sa.Column(
            "artifact_commit_sha",
            sa.String(40),
            nullable=True,
            comment="Full lowercase GitHub commit SHA; first-write-wins in the service",
        ),
    )
    op.add_column(
        "repository_agent_md_snapshot",
        sa.Column(
            "artifact_manifest",
            postgresql.JSONB(),
            nullable=True,
            comment="Content-free artifact inventory; immutable once prepared by the service",
        ),
    )
    op.add_column(
        "repository_agent_md_snapshot",
        sa.Column(
            "repository_activity_progress",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="Repository-level activity progress without document content",
        ),
    )
    op.add_column(
        "repository_agent_md_snapshot",
        sa.Column(
            "artifact_publication_error",
            postgresql.JSONB(),
            nullable=True,
            comment="Sanitized publication code, stage, message, and retryability metadata",
        ),
    )
    op.execute("""
        UPDATE repository_agent_md_snapshot
        SET repository_activity_progress = CASE
          WHEN jsonb_typeof(agent_md_output -> 'repository_activity_progress') = 'object'
          THEN agent_md_output -> 'repository_activity_progress'
          ELSE '{}'::jsonb
        END
    """)
    op.alter_column(
        "repository_agent_md_snapshot",
        "agent_md_output",
        server_default=sa.text("'{}'::jsonb"),
        comment="Legacy document payload retained until the contract migration",
        existing_type=postgresql.JSONB(),
        existing_nullable=False,
    )
    op.create_check_constraint(
        "ck_artifact_commit_sha_format",
        "repository_agent_md_snapshot",
        "artifact_commit_sha IS NULL OR artifact_commit_sha ~ '^[0-9a-f]{40}$'",
    )
    op.create_check_constraint(
        "ck_artifact_manifest_array",
        "repository_agent_md_snapshot",
        "artifact_manifest IS NULL OR jsonb_typeof(artifact_manifest) = 'array'",
    )
    op.create_check_constraint(
        "ck_artifact_sha_has_manifest",
        "repository_agent_md_snapshot",
        "artifact_commit_sha IS NULL OR (artifact_manifest IS NOT NULL AND artifact_manifest <> '[]'::jsonb)",
    )
    op.create_check_constraint(
        "ck_repository_activity_progress_object",
        "repository_agent_md_snapshot",
        "jsonb_typeof(repository_activity_progress) = 'object'",
    )
    op.create_check_constraint(
        "ck_artifact_publication_error_object",
        "repository_agent_md_snapshot",
        "artifact_publication_error IS NULL OR jsonb_typeof(artifact_publication_error) = 'object'",
    )
    op.create_index(
        "uq_repository_active_checkout_mutator",
        "repository_workflow_run",
        ["repository_owner_name", "repository_name"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('RUNNING', 'RETRYING') "
            "AND operation IN ('INGESTION', 'AGENTS_GENERATION', 'AGENT_MD_UPDATE')"
        ),
    )


def downgrade() -> None:
    raise RuntimeError(
        "Removing artifact identities/progress is destructive; restore an isolated backup instead"
    )
