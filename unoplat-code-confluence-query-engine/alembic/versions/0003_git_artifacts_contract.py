# ruff: noqa: INP001
"""Discard legacy generated content and historical raw event/error text.

This revision is irreversible. It drops ``agent_md_output`` without CASCADE and
scrubs generated bodies and raw exception text from event rows and error reports.
Rows, keys, event IDs, ordering, timestamps, statistics, progress, configuration,
credentials, PR metadata and saved Git identity are left untouched.

Everything here is frozen SQL, so online and offline runs apply the same gates and
cleanup. The error-code tables mirror the application's at the time of writing and
must not be updated or imported from application code. Attestation flags record
operational checks: SQL cannot prove that Temporal histories have drained.
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
            RAISE EXCEPTION 'This permanently discards legacy generated content and raw event and error text. Verify a backup, audit a clone, confirm callers are removed and old workers retired, then pass -x discard_legacy_artifacts=true';
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
    # pg_temp keeps the helper out of the application schema. It rebuilds a report
    # from allowlisted values only, so unknown keys cannot survive, whatever their
    # nesting. A malformed report becomes the generic summary, and its row is kept.
    op.execute(r"""
        CREATE FUNCTION pg_temp.scrub_error_report_0003(report jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $scrub$
        DECLARE
          known_codes CONSTANT text[] := ARRAY[
            'workflow_failed', 'execution_timed_out', 'agent_execution_failed',
            'codebase_workflow_failed', 'model_request_failed',
            'checkout_admission_timed_out', 'checkout_admission_denied',
            'git_operation_failed', 'graph_ingestion_failed',
            'package_metadata_failed', 'package_manager_unsupported',
            'workflow_state_invalid', 'status_update_failed',
            'agent_md_trigger_failed', 'artifact_publication_failed'
          ];
          source jsonb := '{}'::jsonb;
          error_code text;
          retryable jsonb := 'null'::jsonb;
          raw_failures jsonb;
          candidate jsonb;
          agent text;
          codebase text;
          entry_code text;
          status_code jsonb;
          failures jsonb := '[]'::jsonb;
          kept integer := 0;
        BEGIN
          IF jsonb_typeof(report -> 'metadata') = 'object' THEN
            source := report -> 'metadata';
          END IF;

          error_code := CASE source ->> 'type'
            WHEN 'TimeoutError' THEN 'execution_timed_out'
            WHEN 'AgentExecutionError' THEN 'agent_execution_failed'
            WHEN 'CodebaseWorkflowError' THEN 'codebase_workflow_failed'
            WHEN 'ModelHTTPError' THEN 'model_request_failed'
            WHEN 'ModelAPIError' THEN 'model_request_failed'
            WHEN 'FallbackExceptionGroup' THEN 'model_request_failed'
            WHEN 'UnexpectedModelBehavior' THEN 'model_request_failed'
            WHEN 'CheckoutAdmissionTimeout' THEN 'checkout_admission_timed_out'
            WHEN 'CheckoutAdmissionDenied' THEN 'checkout_admission_denied'
            WHEN 'CheckoutAdmissionError' THEN 'checkout_admission_denied'
            WHEN 'GIT_ACTIVITY_ERROR' THEN 'git_operation_failed'
            WHEN 'GithubHelperError' THEN 'git_operation_failed'
            WHEN 'GRAPH_INGESTION_ERROR' THEN 'graph_ingestion_failed'
            WHEN 'PACKAGE_METADATA_ERROR' THEN 'package_metadata_failed'
            WHEN 'PACKAGE_METADATA_INGESTION_ERROR' THEN 'package_metadata_failed'
            WHEN 'PACKAGE_PARSER_ERROR' THEN 'package_metadata_failed'
            WHEN 'PACKAGE_MANAGER_NOT_SPECIFIED_ERROR' THEN 'package_manager_unsupported'
            WHEN 'UNSUPPORTED_PACKAGE_MANAGER_ERROR' THEN 'package_manager_unsupported'
            WHEN 'ParentWorkflowRunNotFound' THEN 'workflow_state_invalid'
            WHEN 'CodebaseConfigNotFound' THEN 'workflow_state_invalid'
            WHEN 'AgentMdPrMissingRunContextError' THEN 'workflow_state_invalid'
            WHEN 'CodebaseStatusUpdateError' THEN 'status_update_failed'
            WHEN 'AGENT_MD_TRIGGER_NETWORK_ERROR' THEN 'agent_md_trigger_failed'
            WHEN 'AGENT_MD_TRIGGER_HTTP_ERROR' THEN 'agent_md_trigger_failed'
            WHEN 'AgentMdPrError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrNotFoundError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrConfigurationError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrAuthError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrInternalError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrGithubError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrConflictError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrStaleArtifactError' THEN 'artifact_publication_failed'
            WHEN 'AgentMdPrMissingArtifactError' THEN 'artifact_publication_failed'
            ELSE 'workflow_failed'
          END;
          IF source ->> 'code' = ANY (known_codes) THEN
            error_code := source ->> 'code';
          END IF;

          IF jsonb_typeof(source -> 'retryable') = 'boolean' THEN
            retryable := source -> 'retryable';
          ELSIF jsonb_typeof(source -> 'non_retryable') = 'boolean' THEN
            retryable := to_jsonb(NOT (source ->> 'non_retryable')::boolean);
          END IF;

          raw_failures := source -> 'failures';
          IF raw_failures IS NULL OR raw_failures = 'null'::jsonb THEN
            raw_failures := source -> 'details';
          END IF;
          IF jsonb_typeof(raw_failures) = 'array' THEN
            -- Temporal details can wrap the failure list in one more array.
            FOR candidate IN
              SELECT COALESCE(nested.value, item.value)
              FROM jsonb_array_elements(raw_failures)
                WITH ORDINALITY AS item (value, position)
              LEFT JOIN LATERAL jsonb_array_elements(
                CASE WHEN jsonb_typeof(item.value) = 'array' THEN item.value END
              ) WITH ORDINALITY AS nested (value, position) ON true
              ORDER BY item.position, nested.position
            LOOP
              EXIT WHEN kept = 32;
              CONTINUE WHEN jsonb_typeof(candidate) <> 'object';

              agent := NULL;
              IF jsonb_typeof(candidate -> 'agent') = 'string'
                 AND candidate ->> 'agent' ~ '^[a-z][a-z0-9_]{0,79}$' THEN
                agent := candidate ->> 'agent';
              END IF;

              codebase := NULL;
              IF jsonb_typeof(candidate -> 'codebase') = 'string'
                 AND candidate ->> 'codebase' ~ '^[A-Za-z0-9._/-]{1,255}$'
                 AND candidate ->> 'codebase' !~ '^/'
                 AND candidate ->> 'codebase' !~ '(^|/)[.][.](/|$)' THEN
                codebase := candidate ->> 'codebase';
              END IF;

              CONTINUE WHEN agent IS NULL AND codebase IS NULL;

              entry_code := 'workflow_failed';
              IF candidate ->> 'code' = ANY (known_codes) THEN
                entry_code := candidate ->> 'code';
              END IF;

              status_code := 'null'::jsonb;
              IF jsonb_typeof(candidate -> 'status_code') = 'number'
                 AND candidate ->> 'status_code' ~ '^[1-5][0-9][0-9]$' THEN
                status_code := candidate -> 'status_code';
              END IF;

              failures := failures || jsonb_build_object(
                'agent', agent,
                'codebase', codebase,
                'code', entry_code,
                'status_code', status_code
              );
              kept := kept + 1;
            END LOOP;
          END IF;

          RETURN jsonb_build_object(
            'error_message', CASE error_code
              WHEN 'execution_timed_out' THEN 'A workflow step timed out.'
              WHEN 'agent_execution_failed' THEN 'One or more agents failed.'
              WHEN 'codebase_workflow_failed' THEN 'One or more codebase or repository agent executions failed.'
              WHEN 'model_request_failed' THEN 'A model provider request failed.'
              WHEN 'checkout_admission_timed_out' THEN 'Checkout admission timed out.'
              WHEN 'checkout_admission_denied' THEN 'Checkout admission was denied.'
              WHEN 'git_operation_failed' THEN 'A Git operation failed.'
              WHEN 'graph_ingestion_failed' THEN 'Code graph ingestion failed.'
              WHEN 'package_metadata_failed' THEN 'Package metadata processing failed.'
              WHEN 'package_manager_unsupported' THEN 'The package manager is missing or unsupported.'
              WHEN 'workflow_state_invalid' THEN 'Required workflow state was not found.'
              WHEN 'status_update_failed' THEN 'A workflow status update failed.'
              WHEN 'agent_md_trigger_failed' THEN 'Agent generation could not be started.'
              WHEN 'artifact_publication_failed' THEN 'Generated artifacts could not be saved to Git.'
              ELSE 'The workflow failed.'
            END,
            'metadata', jsonb_build_object(
              'code', error_code,
              'retryable', retryable,
              'failures', failures
            )
          );
        END;
        $scrub$
    """)
    # SQL NULL and JSON null both mean "no report", so neither is rewritten.
    op.execute("""
        UPDATE repository_workflow_run
        SET error_report = pg_temp.scrub_error_report_0003(error_report)
        WHERE error_report IS NOT NULL AND error_report <> 'null'::jsonb
    """)
    op.execute("""
        UPDATE codebase_workflow_run
        SET error_report = pg_temp.scrub_error_report_0003(error_report)
        WHERE error_report IS NOT NULL AND error_report <> 'null'::jsonb
    """)
    op.execute("DROP FUNCTION pg_temp.scrub_error_report_0003(jsonb)")
    # No CASCADE: an unexpected dependency must stop this for review.
    op.drop_column("repository_agent_md_snapshot", "agent_md_output")


def downgrade() -> None:
    raise RuntimeError(
        "Contract permanently discarded legacy generated content and raw event and "
        "error text; no downgrade can restore them, and recreating an empty column "
        "would only hide that loss. Recover in an isolated restored pre-contract "
        "backup with its retained compatible build"
    )
