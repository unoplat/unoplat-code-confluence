# ruff: noqa: INP001
"""Discard legacy generated content and historical raw agent event text.

This revision is irreversible. It drops ``agent_md_output`` without CASCADE and
scrubs tool payloads and message previews from agent event rows. Workflow
``error_report`` values are preserved unchanged, so users can still submit full
error details. Rows, keys, event IDs, ordering, timestamps, statistics, progress,
configuration, credentials, PR metadata and saved Git identity are left untouched.

Everything here is frozen SQL, so online and offline runs apply the same gates and
cleanup. Attestation flags record operational checks: SQL cannot prove that
Temporal histories have drained.
"""

from alembic import op

revision = "0003_git_artifacts_contract"
down_revision = "0002_git_artifacts_expand"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Bounds waits on live sessions, and any single cleanup statement. A failure
    # rolls back this revision's schema and data changes together.
    op.execute("SET LOCAL lock_timeout = '5s'")
    op.execute("SET LOCAL statement_timeout = '30min'")
    op.execute("""
        DO $$ BEGIN
          IF current_setting('unoplat.git_artifacts_drained', true)
               IS DISTINCT FROM 'true' THEN
            RAISE EXCEPTION 'Pause starts, drain affected Temporal histories, reconcile DB rows, then pass -x drained=true';
          END IF;
          IF current_setting('unoplat.git_artifacts_discard_legacy', true)
               IS DISTINCT FROM 'true' THEN
            RAISE EXCEPTION 'This permanently discards legacy generated content and raw agent event text. Verify a backup, audit a clone, confirm callers are removed and old workers retired, then pass -x discard_legacy_artifacts=true';
          END IF;
        END $$
    """)
    op.execute("""
        LOCK TABLE
          repository_workflow_run,
          codebase_workflow_run,
          repository_agent_md_snapshot,
          repository_agent_event
        IN ACCESS EXCLUSIVE MODE
    """)
    # Children are checked whatever their parent's status: old code could mark a
    # parent ERROR while its siblings were still running.
    op.execute("""
        DO $$ BEGIN
          IF EXISTS (
            SELECT 1 FROM repository_workflow_run
            WHERE status IN ('SUBMITTED', 'RUNNING', 'RETRYING')
              AND operation IN ('INGESTION', 'AGENTS_GENERATION', 'AGENT_MD_UPDATE')
          ) THEN
            RAISE EXCEPTION 'Drain queued/active checkout mutators and reconcile stale rows against Temporal before contract';
          END IF;
          IF EXISTS (
            SELECT 1 FROM codebase_workflow_run
            WHERE status IN ('SUBMITTED', 'RUNNING', 'RETRYING')
          ) THEN
            RAISE EXCEPTION 'Drain queued/active child codebase workflows, including children of terminal parents, and reconcile stale rows against Temporal before contract';
          END IF;
        END $$
    """)
    # An unexpected schema stops the transaction here, before any row changes.
    op.execute("""
        DO $$ BEGIN
          IF (
            SELECT count(*)
            FROM (VALUES
              ('repository_agent_md_snapshot', 'agent_md_output', 'jsonb'),
              ('repository_agent_md_snapshot', 'artifact_commit_sha', 'character varying(40)'),
              ('repository_agent_md_snapshot', 'artifact_manifest', 'jsonb'),
              ('repository_agent_md_snapshot', 'repository_activity_progress', 'jsonb'),
              ('repository_agent_md_snapshot', 'artifact_publication_error', 'jsonb'),
              ('repository_agent_event', 'event', 'character varying'),
              ('repository_agent_event', 'phase', 'character varying'),
              ('repository_agent_event', 'message', 'character varying'),
              ('repository_agent_event', 'tool_name', 'character varying'),
              ('repository_agent_event', 'tool_call_id', 'character varying'),
              ('repository_agent_event', 'tool_args', 'jsonb'),
              ('repository_agent_event', 'tool_result_content', 'character varying'),
              ('repository_workflow_run', 'error_report', 'jsonb'),
              ('codebase_workflow_run', 'error_report', 'jsonb')
            ) AS expected (table_name, column_name, data_type)
            JOIN pg_attribute AS attribute
              ON attribute.attrelid = to_regclass(expected.table_name)
             AND attribute.attname = expected.column_name
             AND NOT attribute.attisdropped
             AND format_type(attribute.atttypid, attribute.atttypmod) = expected.data_type
          ) <> 14 THEN
            RAISE EXCEPTION 'Schema differs from the expanded reference; stop and prepare a reviewed reconciliation before contract';
          END IF;
        END $$
    """)
    # Tool bodies and previews go. Identifiers stay only if they meet the contract,
    # which an unconditional update also applies to rows that are already clean.
    op.execute(r"""
        UPDATE repository_agent_event
        SET
          tool_args = NULL,
          tool_result_content = NULL,
          message = CASE phase
            WHEN 'tool.call' THEN 'Tool call started'
            WHEN 'tool.result' THEN 'Tool call finished'
            WHEN 'result' THEN 'Agent step completed'
            ELSE 'Agent event recorded'
          END,
          tool_name = CASE
            WHEN tool_name ~ '^[A-Za-z0-9_.:-]{1,128}$' THEN tool_name
          END,
          tool_call_id = CASE
            WHEN tool_call_id ~ '^[A-Za-z0-9_.:|-]{1,200}$' THEN tool_call_id
          END,
          event = CASE
            WHEN event ~ '^[A-Za-z0-9_.:-]{1,128}$' THEN event
            ELSE 'unknown'
          END,
          phase = CASE
            WHEN phase ~ '^[a-z][a-z0-9_.]{0,63}$' THEN phase
            ELSE 'unknown'
          END
    """)
    # No CASCADE: an unexpected dependency must stop this for review.
    op.drop_column("repository_agent_md_snapshot", "agent_md_output")


def downgrade() -> None:
    raise RuntimeError(
        "Contract permanently discarded legacy generated content and raw agent "
        "event text; no downgrade can restore them, and recreating an empty column "
        "would only hide that loss. Recover in an isolated restored pre-contract "
        "backup with its retained compatible build"
    )
