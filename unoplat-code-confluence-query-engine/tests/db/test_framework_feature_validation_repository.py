"""Integration tests for framework feature validation persistence repository APIs."""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import delete, select
from unoplat_code_confluence_commons.base_models import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
    ValidationStatus,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
    UnoplatCodeConfluenceGitRepository,
)

from tests.utils.sync_db_utils import get_sync_postgres_session
from unoplat_code_confluence_query_engine.db.postgres.code_confluence_framework_repository import (
    db_get_all_framework_features_for_codebase,
    db_get_low_confidence_call_expression_candidates,
    db_set_framework_feature_validation_status,
    db_upsert_framework_feature_validation_evidence,
)
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    FrameworkFeatureUsageIdentity,
    FrameworkFeatureValidationDecision,
    FrameworkFeatureValidationEvidenceUpsertRequest,
    FrameworkFeatureValidationStatusTransitionRequest,
)

TEST_REPOSITORY_QUALIFIED_NAME = "validator-owner/validator-repo"
TEST_CODEBASE_QUALIFIED_NAME = "validator-owner/validator-repo:validator-codebase"
TEST_CODEBASE_PATH = "/tmp/validator-codebase"
TEST_FILE_PATH = "/tmp/validator-codebase/app/main.py"
TEST_FEATURE_LANGUAGE = "python"
TEST_FEATURE_LIBRARY = "validatorlib"
TEST_SOURCE_CAPABILITY_KEY = "database"
TEST_SOURCE_OPERATION_KEY = "db_sql"
TEST_SOURCE_FEATURE_KEY = "database.db_sql"
TEST_CORRECTED_CAPABILITY_KEY = "http_client"
TEST_CORRECTED_OPERATION_KEY = "send_request"
TEST_CORRECTED_FEATURE_KEY = "http_client.send_request"

TEST_TS_REPOSITORY_QUALIFIED_NAME = "validator-owner/validator-repo-typescript"
TEST_TS_CODEBASE_QUALIFIED_NAME = (
    "validator-owner/validator-repo-typescript:validator-typescript-codebase"
)
TEST_TS_CODEBASE_PATH = "/tmp/validator-typescript-codebase"
TEST_TS_FILE_PATH = "/tmp/validator-typescript-codebase/src/app.ts"
TEST_TS_FEATURE_LANGUAGE = "typescript"
TEST_TS_FEATURE_LIBRARY = "swr"
TEST_TS_CAPABILITY_KEY = "data_fetch"
TEST_TS_OPERATION_KEY = "fetch_data"
TEST_TS_FEATURE_KEY = "data_fetch.fetch_data"

TEST_TS_LOW_CONF_REPOSITORY_QUALIFIED_NAME = "validator-owner/validator-repo-ts-lowconf"
TEST_TS_LOW_CONF_CODEBASE_QUALIFIED_NAME = (
    "validator-owner/validator-repo-ts-lowconf:validator-ts-lowconf-codebase"
)
TEST_TS_LOW_CONF_CODEBASE_PATH = "/tmp/validator-ts-lowconf-codebase"
TEST_TS_LOW_CONF_FILE_PATH = "/tmp/validator-ts-lowconf-codebase/src/api.ts"
TEST_TS_LOW_CONF_FEATURE_LIBRARY = "swr"
TEST_TS_LOW_CONF_CAPABILITY_KEY = "data_fetch"
TEST_TS_LOW_CONF_OPERATION_KEY = "fetch_data_lowconf"
TEST_TS_LOW_CONF_FEATURE_KEY = "data_fetch.fetch_data_lowconf"

TEST_APP_INTERFACE_REPOSITORY_QUALIFIED_NAME = (
    "validator-owner/validator-repo-app-interface"
)
TEST_APP_INTERFACE_CODEBASE_QUALIFIED_NAME = (
    "validator-owner/validator-repo-app-interface:validator-app-interface-codebase"
)
TEST_APP_INTERFACE_CODEBASE_PATH = "/tmp/validator-app-interface-codebase"
TEST_APP_INTERFACE_FILE_PATH = "/tmp/validator-app-interface-codebase/app/interfaces.py"
TEST_APP_INTERFACE_LANGUAGE = "python"
TEST_APP_INTERFACE_DATA_MODEL_LIBRARY = "validator-pydantic"
TEST_APP_INTERFACE_HTTP_LIBRARY = "validator-fastapi"


def _build_feature_definition(concept: str) -> dict[str, Any]:
    return {
        "description": "test feature",
        "absolute_paths": ["validatorlib.Client"],
        "target_level": "function",
        "concept": concept,
        "locator_strategy": "VariableBound",
        "startpoint": False,
        "base_confidence": 0.5,
    }


def _build_usage_identity(
    capability_key: str,
    operation_key: str,
) -> FrameworkFeatureUsageIdentity:
    return FrameworkFeatureUsageIdentity(
        file_path=TEST_FILE_PATH,
        feature_language=TEST_FEATURE_LANGUAGE,
        feature_library=TEST_FEATURE_LIBRARY,
        feature_capability_key=capability_key,
        feature_operation_key=operation_key,
        start_line=10,
        end_line=12,
    )


def _build_typescript_feature_definition(
    base_confidence: float = 0.9,
) -> dict[str, Any]:
    return {
        "description": "swr data fetch hook",
        "absolute_paths": ["swr.default"],
        "target_level": "function",
        "concept": "CallExpression",
        "locator_strategy": "VariableBound",
        "startpoint": False,
        "base_confidence": base_confidence,
    }


@pytest.fixture
def seeded_framework_usage(service_ports, test_database_tables, db_connections):
    """Seed minimal framework usage graph for repository function tests."""
    postgresql_port = service_ports["postgresql"]

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_FEATURE_LANGUAGE,
                FrameworkFeature.library == TEST_FEATURE_LIBRARY,
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_FEATURE_LANGUAGE,
                Framework.library == TEST_FEATURE_LIBRARY,
            )
        )

        session.add(
            UnoplatCodeConfluenceGitRepository(
                qualified_name=TEST_REPOSITORY_QUALIFIED_NAME,
                repository_url="https://example.com/validator.git",
                repository_name="validator-repo",
            )
        )
        session.add(
            UnoplatCodeConfluenceCodebase(
                qualified_name=TEST_CODEBASE_QUALIFIED_NAME,
                repository_qualified_name=TEST_REPOSITORY_QUALIFIED_NAME,
                name="validator-codebase",
                codebase_path=TEST_CODEBASE_PATH,
                programming_language=TEST_FEATURE_LANGUAGE,
            )
        )
        session.add(
            UnoplatCodeConfluenceFile(
                file_path=TEST_FILE_PATH,
                codebase_qualified_name=TEST_CODEBASE_QUALIFIED_NAME,
                imports=[],
                has_data_model=False,
                data_model_positions={},
            )
        )

        session.add(
            Framework(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                capability_key=TEST_SOURCE_CAPABILITY_KEY,
                operation_key=TEST_SOURCE_OPERATION_KEY,
                feature_definition=_build_feature_definition("CallExpression"),
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                capability_key=TEST_CORRECTED_CAPABILITY_KEY,
                operation_key=TEST_CORRECTED_OPERATION_KEY,
                feature_definition=_build_feature_definition("CallExpression"),
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                capability_key=TEST_SOURCE_CAPABILITY_KEY,
                operation_key=TEST_SOURCE_OPERATION_KEY,
                absolute_path="validatorlib.Client",
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                capability_key=TEST_CORRECTED_CAPABILITY_KEY,
                operation_key=TEST_CORRECTED_OPERATION_KEY,
                absolute_path="validatorlib.HttpClient",
            )
        )

        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_FILE_PATH,
                feature_language=TEST_FEATURE_LANGUAGE,
                feature_library=TEST_FEATURE_LIBRARY,
                feature_capability_key=TEST_SOURCE_CAPABILITY_KEY,
                feature_operation_key=TEST_SOURCE_OPERATION_KEY,
                start_line=10,
                end_line=12,
                match_text="db.execute(query)",
                match_confidence=0.55,
                validation_status="pending",
                evidence_json={"callee": "db.execute", "args_text": "(query)"},
            )
        )

    yield {
        "postgresql_port": postgresql_port,
        "codebase_path": TEST_CODEBASE_PATH,
    }

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_FEATURE_LANGUAGE,
                FrameworkFeature.library == TEST_FEATURE_LIBRARY,
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_FEATURE_LANGUAGE,
                Framework.library == TEST_FEATURE_LIBRARY,
            )
        )


@pytest.fixture
def seeded_typescript_framework_usage(
    service_ports, test_database_tables, db_connections
):
    """Seed TypeScript framework usage for query path coverage."""
    postgresql_port = service_ports["postgresql"]

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_TS_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_TS_FEATURE_LANGUAGE,
                FrameworkFeature.library == TEST_TS_FEATURE_LIBRARY,
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_TS_FEATURE_LANGUAGE,
                Framework.library == TEST_TS_FEATURE_LIBRARY,
            )
        )

        session.add(
            UnoplatCodeConfluenceGitRepository(
                qualified_name=TEST_TS_REPOSITORY_QUALIFIED_NAME,
                repository_url="https://example.com/validator-typescript.git",
                repository_name="validator-repo-typescript",
            )
        )
        session.add(
            UnoplatCodeConfluenceCodebase(
                qualified_name=TEST_TS_CODEBASE_QUALIFIED_NAME,
                repository_qualified_name=TEST_TS_REPOSITORY_QUALIFIED_NAME,
                name="validator-typescript-codebase",
                codebase_path=TEST_TS_CODEBASE_PATH,
                programming_language=TEST_TS_FEATURE_LANGUAGE,
            )
        )
        session.add(
            UnoplatCodeConfluenceFile(
                file_path=TEST_TS_FILE_PATH,
                codebase_qualified_name=TEST_TS_CODEBASE_QUALIFIED_NAME,
                imports=["import useSWR from 'swr'"],
                has_data_model=False,
                data_model_positions={},
            )
        )
        session.add(
            Framework(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_FEATURE_LIBRARY,
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_FEATURE_LIBRARY,
                capability_key=TEST_TS_CAPABILITY_KEY,
                operation_key=TEST_TS_OPERATION_KEY,
                feature_definition=_build_typescript_feature_definition(),
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_FEATURE_LIBRARY,
                capability_key=TEST_TS_CAPABILITY_KEY,
                operation_key=TEST_TS_OPERATION_KEY,
                absolute_path="swr.default",
            )
        )
        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_TS_FILE_PATH,
                feature_language=TEST_TS_FEATURE_LANGUAGE,
                feature_library=TEST_TS_FEATURE_LIBRARY,
                feature_capability_key=TEST_TS_CAPABILITY_KEY,
                feature_operation_key=TEST_TS_OPERATION_KEY,
                start_line=5,
                end_line=5,
                match_text="useSWR('/api/search', fetcher)",
                match_confidence=0.92,
                validation_status="pending",
                evidence_json={
                    "callee": "useSWR",
                    "args_text": "('/api/search', fetcher)",
                },
            )
        )

    yield {
        "postgresql_port": postgresql_port,
        "codebase_path": TEST_TS_CODEBASE_PATH,
    }

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_TS_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_TS_FEATURE_LANGUAGE,
                FrameworkFeature.library == TEST_TS_FEATURE_LIBRARY,
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_TS_FEATURE_LANGUAGE,
                Framework.library == TEST_TS_FEATURE_LIBRARY,
            )
        )


@pytest.fixture
def seeded_app_interface_data_model_and_http_usage(
    service_ports, test_database_tables, db_connections
):
    """Seed namespaced data-model + app-interface rows for exclusion tests."""
    postgresql_port = service_ports["postgresql"]

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_APP_INTERFACE_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_APP_INTERFACE_LANGUAGE,
                FrameworkFeature.library.in_(
                    [
                        TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
                        TEST_APP_INTERFACE_HTTP_LIBRARY,
                    ]
                ),
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_APP_INTERFACE_LANGUAGE,
                Framework.library.in_(
                    [
                        TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
                        TEST_APP_INTERFACE_HTTP_LIBRARY,
                    ]
                ),
            )
        )

        session.add(
            UnoplatCodeConfluenceGitRepository(
                qualified_name=TEST_APP_INTERFACE_REPOSITORY_QUALIFIED_NAME,
                repository_url="https://example.com/validator-app-interface.git",
                repository_name="validator-app-interface",
            )
        )
        session.add(
            UnoplatCodeConfluenceCodebase(
                qualified_name=TEST_APP_INTERFACE_CODEBASE_QUALIFIED_NAME,
                repository_qualified_name=TEST_APP_INTERFACE_REPOSITORY_QUALIFIED_NAME,
                name="validator-app-interface-codebase",
                codebase_path=TEST_APP_INTERFACE_CODEBASE_PATH,
                programming_language=TEST_APP_INTERFACE_LANGUAGE,
            )
        )
        session.add(
            UnoplatCodeConfluenceFile(
                file_path=TEST_APP_INTERFACE_FILE_PATH,
                codebase_qualified_name=TEST_APP_INTERFACE_CODEBASE_QUALIFIED_NAME,
                imports=[],
                has_data_model=False,
                data_model_positions={},
            )
        )

        session.add(
            Framework(
                language=TEST_APP_INTERFACE_LANGUAGE,
                library=TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
            )
        )
        session.add(
            Framework(
                language=TEST_APP_INTERFACE_LANGUAGE,
                library=TEST_APP_INTERFACE_HTTP_LIBRARY,
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_APP_INTERFACE_LANGUAGE,
                library=TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
                capability_key="data_model",
                operation_key="data_model",
                feature_definition=_build_feature_definition("Inheritance"),
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_APP_INTERFACE_LANGUAGE,
                library=TEST_APP_INTERFACE_HTTP_LIBRARY,
                capability_key="rest_api",
                operation_key="get",
                feature_definition=_build_feature_definition("AnnotationLike"),
            )
        )
        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_APP_INTERFACE_FILE_PATH,
                feature_language=TEST_APP_INTERFACE_LANGUAGE,
                feature_library=TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
                feature_capability_key="data_model",
                feature_operation_key="data_model",
                start_line=7,
                end_line=20,
                match_text="class User(BaseModel)",
                match_confidence=0.83,
                validation_status="completed",
                evidence_json=None,
            )
        )
        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_APP_INTERFACE_FILE_PATH,
                feature_language=TEST_APP_INTERFACE_LANGUAGE,
                feature_library=TEST_APP_INTERFACE_HTTP_LIBRARY,
                feature_capability_key="rest_api",
                feature_operation_key="get",
                start_line=28,
                end_line=29,
                match_text="@router.get('/health')",
                match_confidence=0.97,
                validation_status="completed",
                evidence_json=None,
            )
        )

    yield {
        "postgresql_port": postgresql_port,
        "codebase_path": TEST_APP_INTERFACE_CODEBASE_PATH,
    }

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_APP_INTERFACE_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_APP_INTERFACE_LANGUAGE,
                FrameworkFeature.library.in_(
                    [
                        TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
                        TEST_APP_INTERFACE_HTTP_LIBRARY,
                    ]
                ),
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_APP_INTERFACE_LANGUAGE,
                Framework.library.in_(
                    [
                        TEST_APP_INTERFACE_DATA_MODEL_LIBRARY,
                        TEST_APP_INTERFACE_HTTP_LIBRARY,
                    ]
                ),
            )
        )


def _get_usage_row(
    postgresql_port: int,
    capability_key: str,
    operation_key: str,
    *,
    file_path: str = TEST_FILE_PATH,
    start_line: int = 10,
    end_line: int = 12,
) -> dict[str, object] | None:
    with get_sync_postgres_session(postgresql_port) as session:
        stmt = (
            select(
                UnoplatCodeConfluenceFileFrameworkFeature.file_path,
                UnoplatCodeConfluenceFileFrameworkFeature.start_line,
                UnoplatCodeConfluenceFileFrameworkFeature.end_line,
                UnoplatCodeConfluenceFileFrameworkFeature.match_text,
                UnoplatCodeConfluenceFileFrameworkFeature.match_confidence,
                UnoplatCodeConfluenceFileFrameworkFeature.validation_status,
                UnoplatCodeConfluenceFileFrameworkFeature.evidence_json,
            )
            .where(UnoplatCodeConfluenceFileFrameworkFeature.file_path == file_path)
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_language
                == TEST_FEATURE_LANGUAGE
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_library
                == TEST_FEATURE_LIBRARY
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_capability_key
                == capability_key
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_operation_key
                == operation_key
            )
            .where(UnoplatCodeConfluenceFileFrameworkFeature.start_line == start_line)
            .where(UnoplatCodeConfluenceFileFrameworkFeature.end_line == end_line)
        )
        row = session.execute(stmt).one_or_none()
        if row is None:
            return None

        (
            row_file_path,
            row_start_line,
            row_end_line,
            match_text,
            match_confidence,
            validation_status,
            evidence_json,
        ) = row
        return {
            "file_path": str(row_file_path),
            "start_line": int(row_start_line),
            "end_line": int(row_end_line),
            "match_text": match_text,
            "match_confidence": float(match_confidence),
            "validation_status": str(validation_status),
            "evidence_json": evidence_json,
        }


@pytest.mark.asyncio(loop_scope="session")
async def test_upsert_validation_evidence_updates_source_row(
    seeded_framework_usage,
) -> None:
    request = FrameworkFeatureValidationEvidenceUpsertRequest(
        identity=_build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY),
        decision=FrameworkFeatureValidationDecision.CONFIRM,
        final_confidence=0.81,
        evidence_json={"reason": "Symbol resolves to framework client"},
    )

    result = await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=request,
    )

    assert result.source_row_updated is True
    assert result.current_identity == request.identity

    updated_row = _get_usage_row(
        seeded_framework_usage["postgresql_port"],
        TEST_SOURCE_CAPABILITY_KEY,
        TEST_SOURCE_OPERATION_KEY,
    )
    assert updated_row is not None
    assert updated_row["match_confidence"] == pytest.approx(0.81)
    evidence_json = updated_row["evidence_json"]
    assert isinstance(evidence_json, dict)
    assert evidence_json is not None
    validator_payload = evidence_json["validator"]
    assert isinstance(validator_payload, dict)
    assert validator_payload["decision"] == "confirm"


@pytest.mark.asyncio(loop_scope="session")
async def test_upsert_validation_evidence_correct_decision_updates_source_row_in_place(
    seeded_framework_usage,
) -> None:
    request = FrameworkFeatureValidationEvidenceUpsertRequest(
        identity=_build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY),
        decision=FrameworkFeatureValidationDecision.CORRECT,
        final_confidence=0.9,
        evidence_json={"reason": "Call span was off by one line"},
        corrected_start_line=11,
        corrected_end_line=13,
        corrected_match_text="db.execute(validated_query)",
    )

    result = await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=request,
    )

    assert result.source_row_updated is True
    assert result.current_identity == request.identity.model_copy(
        update={"start_line": 11, "end_line": 13}
    )

    old_row = _get_usage_row(
        seeded_framework_usage["postgresql_port"],
        TEST_SOURCE_CAPABILITY_KEY,
        TEST_SOURCE_OPERATION_KEY,
    )
    assert old_row is None

    updated_row = _get_usage_row(
        seeded_framework_usage["postgresql_port"],
        TEST_SOURCE_CAPABILITY_KEY,
        TEST_SOURCE_OPERATION_KEY,
        start_line=11,
        end_line=13,
    )
    assert updated_row is not None
    assert updated_row["validation_status"] == "pending"
    assert updated_row["match_confidence"] == pytest.approx(0.9)
    assert updated_row["match_text"] == "db.execute(validated_query)"
    evidence_json = updated_row["evidence_json"]
    assert isinstance(evidence_json, dict)
    assert evidence_json is not None
    validator_payload = evidence_json["validator"]
    assert isinstance(validator_payload, dict)
    assert validator_payload["decision"] == "correct"
    corrected_from = validator_payload["corrected_from"]
    assert isinstance(corrected_from, dict)
    assert corrected_from["file_path"] == TEST_FILE_PATH
    assert corrected_from["start_line"] == 10
    assert corrected_from["end_line"] == 12
    assert corrected_from["match_text"] == "db.execute(query)"


@pytest.mark.asyncio(loop_scope="session")
async def test_status_transition_enforces_completed_terminal_behavior(
    seeded_framework_usage,
) -> None:
    identity = _build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY)

    transition_result = await db_set_framework_feature_validation_status(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationStatusTransitionRequest(
            identity=identity,
            target_status=ValidationStatus.COMPLETED,
            expected_current_status=ValidationStatus.PENDING,
        ),
    )

    assert transition_result.status == "updated"
    assert transition_result.previous_status == ValidationStatus.PENDING
    assert transition_result.current_status == ValidationStatus.COMPLETED

    with pytest.raises(
        ValueError,
        match="Invalid validation_status transition: completed -> needs_review",
    ):
        await db_set_framework_feature_validation_status(
            codebase_path=seeded_framework_usage["codebase_path"],
            request=FrameworkFeatureValidationStatusTransitionRequest(
                identity=identity,
                target_status=ValidationStatus.NEEDS_REVIEW,
            ),
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_low_confidence_candidate_query_returns_pending_call_expression_only(
    seeded_framework_usage,
) -> None:
    candidates = await db_get_low_confidence_call_expression_candidates(
        codebase_path=seeded_framework_usage["codebase_path"],
        programming_language=TEST_FEATURE_LANGUAGE,
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.identity.feature_key == TEST_SOURCE_FEATURE_KEY
    assert candidate.identity.feature_capability_key == TEST_SOURCE_CAPABILITY_KEY
    assert candidate.identity.feature_operation_key == TEST_SOURCE_OPERATION_KEY
    assert candidate.match_confidence == pytest.approx(0.55)
    assert candidate.validation_status == ValidationStatus.PENDING
    assert candidate.absolute_paths == ["validatorlib.Client"]


@pytest.mark.asyncio(loop_scope="session")
async def test_low_confidence_candidate_query_excludes_completed_call_expression(
    seeded_framework_usage,
) -> None:
    identity = _build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY)
    await db_set_framework_feature_validation_status(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationStatusTransitionRequest(
            identity=identity,
            target_status=ValidationStatus.COMPLETED,
            expected_current_status=ValidationStatus.PENDING,
        ),
    )

    candidates = await db_get_low_confidence_call_expression_candidates(
        codebase_path=seeded_framework_usage["codebase_path"],
        programming_language=TEST_FEATURE_LANGUAGE,
    )
    assert candidates == []


@pytest.mark.asyncio(loop_scope="session")
async def test_app_interface_fetch_excludes_low_confidence_call_expression_until_completed(
    seeded_framework_usage,
) -> None:
    initial_rows = await db_get_all_framework_features_for_codebase(
        seeded_framework_usage["codebase_path"],
        TEST_FEATURE_LANGUAGE,
    )
    assert initial_rows == []

    identity = _build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY)
    await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationEvidenceUpsertRequest(
            identity=identity,
            decision=FrameworkFeatureValidationDecision.CONFIRM,
            final_confidence=0.61,
            evidence_json={"reason": "resolved by validator"},
        ),
    )
    await db_set_framework_feature_validation_status(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationStatusTransitionRequest(
            identity=identity,
            target_status=ValidationStatus.COMPLETED,
            expected_current_status=ValidationStatus.PENDING,
        ),
    )

    updated_rows = await db_get_all_framework_features_for_codebase(
        seeded_framework_usage["codebase_path"],
        TEST_FEATURE_LANGUAGE,
    )
    assert len(updated_rows) == 1
    assert updated_rows[0]["feature_key"] == TEST_SOURCE_FEATURE_KEY


@pytest.mark.asyncio(loop_scope="session")
async def test_app_interface_fetch_excludes_revalidated_pending_row_even_if_confidence_high(
    seeded_framework_usage,
) -> None:
    identity = _build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY)
    await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationEvidenceUpsertRequest(
            identity=identity,
            decision=FrameworkFeatureValidationDecision.CONFIRM,
            final_confidence=0.91,
            evidence_json={"reason": "validated but status transition pending"},
        ),
    )

    rows = await db_get_all_framework_features_for_codebase(
        seeded_framework_usage["codebase_path"],
        TEST_FEATURE_LANGUAGE,
    )
    assert rows == []


@pytest.mark.asyncio(loop_scope="session")
async def test_app_interface_fetch_includes_in_place_corrected_row_after_correct_decision(
    seeded_framework_usage,
) -> None:
    source_identity = _build_usage_identity(TEST_SOURCE_CAPABILITY_KEY, TEST_SOURCE_OPERATION_KEY)
    upsert_result = await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationEvidenceUpsertRequest(
            identity=source_identity,
            decision=FrameworkFeatureValidationDecision.CORRECT,
            final_confidence=0.9,
            evidence_json={"reason": "same feature, corrected span"},
            corrected_start_line=11,
            corrected_end_line=13,
            corrected_match_text="db.execute(validated_query)",
        ),
    )
    await db_set_framework_feature_validation_status(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationStatusTransitionRequest(
            identity=upsert_result.current_identity,
            target_status=ValidationStatus.COMPLETED,
            expected_current_status=ValidationStatus.PENDING,
        ),
    )

    rows = await db_get_all_framework_features_for_codebase(
        seeded_framework_usage["codebase_path"],
        TEST_FEATURE_LANGUAGE,
    )
    assert len(rows) == 1
    assert rows[0]["feature_key"] == TEST_SOURCE_FEATURE_KEY
    assert rows[0]["file_path"] == TEST_FILE_PATH
    assert rows[0]["start_line"] == 11
    assert rows[0]["end_line"] == 13
    assert rows[0]["match_text"] == "db.execute(validated_query)"

    updated_row = _get_usage_row(
        seeded_framework_usage["postgresql_port"],
        TEST_SOURCE_CAPABILITY_KEY,
        TEST_SOURCE_OPERATION_KEY,
        start_line=11,
        end_line=13,
    )
    assert updated_row is not None
    assert updated_row["validation_status"] == "completed"


@pytest.mark.asyncio(loop_scope="session")
async def test_app_interface_fetch_excludes_namespaced_data_model_family_rows(
    seeded_app_interface_data_model_and_http_usage,
) -> None:
    rows = await db_get_all_framework_features_for_codebase(
        seeded_app_interface_data_model_and_http_usage["codebase_path"],
        TEST_APP_INTERFACE_LANGUAGE,
    )

    feature_keys = {str(row["feature_key"]) for row in rows}
    assert "rest_api.get" in feature_keys
    assert "data_model.data_model" not in feature_keys


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_framework_features_supports_typescript_language_filter(
    seeded_typescript_framework_usage,
) -> None:
    rows = await db_get_all_framework_features_for_codebase(
        seeded_typescript_framework_usage["codebase_path"],
        TEST_TS_FEATURE_LANGUAGE,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["library"] == TEST_TS_FEATURE_LIBRARY
    assert row["feature_key"] == TEST_TS_FEATURE_KEY
    assert row["file_path"] == TEST_TS_FILE_PATH


@pytest.fixture
def seeded_typescript_low_confidence_framework_usage(
    service_ports, test_database_tables, db_connections
):
    """Seed TypeScript framework usage with low-confidence CallExpression for validator tests."""
    postgresql_port = service_ports["postgresql"]

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_TS_LOW_CONF_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_TS_FEATURE_LANGUAGE,
                FrameworkFeature.library == TEST_TS_LOW_CONF_FEATURE_LIBRARY,
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_TS_FEATURE_LANGUAGE,
                Framework.library == TEST_TS_LOW_CONF_FEATURE_LIBRARY,
            )
        )

        session.add(
            UnoplatCodeConfluenceGitRepository(
                qualified_name=TEST_TS_LOW_CONF_REPOSITORY_QUALIFIED_NAME,
                repository_url="https://example.com/validator-ts-lowconf.git",
                repository_name="validator-repo-ts-lowconf",
            )
        )
        session.add(
            UnoplatCodeConfluenceCodebase(
                qualified_name=TEST_TS_LOW_CONF_CODEBASE_QUALIFIED_NAME,
                repository_qualified_name=TEST_TS_LOW_CONF_REPOSITORY_QUALIFIED_NAME,
                name="validator-ts-lowconf-codebase",
                codebase_path=TEST_TS_LOW_CONF_CODEBASE_PATH,
                programming_language=TEST_TS_FEATURE_LANGUAGE,
            )
        )
        session.add(
            UnoplatCodeConfluenceFile(
                file_path=TEST_TS_LOW_CONF_FILE_PATH,
                codebase_qualified_name=TEST_TS_LOW_CONF_CODEBASE_QUALIFIED_NAME,
                imports=["import useSWR from 'swr'"],
                has_data_model=False,
                data_model_positions={},
            )
        )
        session.add(
            Framework(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_LOW_CONF_FEATURE_LIBRARY,
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_LOW_CONF_FEATURE_LIBRARY,
                capability_key=TEST_TS_LOW_CONF_CAPABILITY_KEY,
                operation_key=TEST_TS_LOW_CONF_OPERATION_KEY,
                feature_definition=_build_typescript_feature_definition(
                    base_confidence=0.5,
                ),
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_LOW_CONF_FEATURE_LIBRARY,
                capability_key=TEST_TS_LOW_CONF_CAPABILITY_KEY,
                operation_key=TEST_TS_LOW_CONF_OPERATION_KEY,
                absolute_path="swr.default",
            )
        )
        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_TS_LOW_CONF_FILE_PATH,
                feature_language=TEST_TS_FEATURE_LANGUAGE,
                feature_library=TEST_TS_LOW_CONF_FEATURE_LIBRARY,
                feature_capability_key=TEST_TS_LOW_CONF_CAPABILITY_KEY,
                feature_operation_key=TEST_TS_LOW_CONF_OPERATION_KEY,
                start_line=3,
                end_line=3,
                match_text="useSWR('/api/data', fetcher)",
                match_confidence=0.55,
                validation_status="pending",
                evidence_json={
                    "callee": "useSWR",
                    "args_text": "('/api/data', fetcher)",
                },
            )
        )

    yield {
        "postgresql_port": postgresql_port,
        "codebase_path": TEST_TS_LOW_CONF_CODEBASE_PATH,
    }

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_TS_LOW_CONF_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_TS_FEATURE_LANGUAGE,
                FrameworkFeature.library == TEST_TS_LOW_CONF_FEATURE_LIBRARY,
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_TS_FEATURE_LANGUAGE,
                Framework.library == TEST_TS_LOW_CONF_FEATURE_LIBRARY,
            )
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_low_confidence_typescript_candidate_query_returns_pending_call_expression(
    seeded_typescript_low_confidence_framework_usage,
) -> None:
    """Mirrors Python test — verifies TypeScript low-confidence candidates are returned."""
    candidates = await db_get_low_confidence_call_expression_candidates(
        codebase_path=seeded_typescript_low_confidence_framework_usage["codebase_path"],
        programming_language=TEST_TS_FEATURE_LANGUAGE,
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.identity.feature_key == TEST_TS_LOW_CONF_FEATURE_KEY
    assert candidate.identity.feature_capability_key == TEST_TS_LOW_CONF_CAPABILITY_KEY
    assert candidate.identity.feature_operation_key == TEST_TS_LOW_CONF_OPERATION_KEY
    assert candidate.match_confidence == pytest.approx(0.55)
    assert candidate.validation_status == ValidationStatus.PENDING
    assert candidate.absolute_paths == ["swr.default"]


@pytest.mark.asyncio(loop_scope="session")
async def test_app_interface_fetch_excludes_low_confidence_typescript_until_completed(
    seeded_typescript_low_confidence_framework_usage,
) -> None:
    """Mirrors Python exclusion test — low-confidence TS rows excluded until validated."""
    initial_rows = await db_get_all_framework_features_for_codebase(
        seeded_typescript_low_confidence_framework_usage["codebase_path"],
        TEST_TS_FEATURE_LANGUAGE,
    )
    assert initial_rows == []

    identity = FrameworkFeatureUsageIdentity(
        file_path=TEST_TS_LOW_CONF_FILE_PATH,
        feature_language=TEST_TS_FEATURE_LANGUAGE,
        feature_library=TEST_TS_LOW_CONF_FEATURE_LIBRARY,
        feature_capability_key=TEST_TS_LOW_CONF_CAPABILITY_KEY,
        feature_operation_key=TEST_TS_LOW_CONF_OPERATION_KEY,
        start_line=3,
        end_line=3,
    )
    await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_typescript_low_confidence_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationEvidenceUpsertRequest(
            identity=identity,
            decision=FrameworkFeatureValidationDecision.CONFIRM,
            final_confidence=0.61,
            evidence_json={"reason": "resolved by validator"},
        ),
    )
    await db_set_framework_feature_validation_status(
        codebase_path=seeded_typescript_low_confidence_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationStatusTransitionRequest(
            identity=identity,
            target_status=ValidationStatus.COMPLETED,
            expected_current_status=ValidationStatus.PENDING,
        ),
    )

    updated_rows = await db_get_all_framework_features_for_codebase(
        seeded_typescript_low_confidence_framework_usage["codebase_path"],
        TEST_TS_FEATURE_LANGUAGE,
    )
    assert len(updated_rows) == 1
    assert updated_rows[0]["feature_key"] == TEST_TS_LOW_CONF_FEATURE_KEY
