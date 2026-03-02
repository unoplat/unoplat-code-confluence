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
TEST_SOURCE_FEATURE_KEY = "db_sql"
TEST_CORRECTED_FEATURE_KEY = "http_client"

TEST_TS_REPOSITORY_QUALIFIED_NAME = "validator-owner/validator-repo-typescript"
TEST_TS_CODEBASE_QUALIFIED_NAME = (
    "validator-owner/validator-repo-typescript:validator-typescript-codebase"
)
TEST_TS_CODEBASE_PATH = "/tmp/validator-typescript-codebase"
TEST_TS_FILE_PATH = "/tmp/validator-typescript-codebase/src/app.ts"
TEST_TS_FEATURE_LANGUAGE = "typescript"
TEST_TS_FEATURE_LIBRARY = "swr"
TEST_TS_FEATURE_KEY = "data_fetch"


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


def _build_usage_identity(feature_key: str) -> FrameworkFeatureUsageIdentity:
    return FrameworkFeatureUsageIdentity(
        file_path=TEST_FILE_PATH,
        feature_language=TEST_FEATURE_LANGUAGE,
        feature_library=TEST_FEATURE_LIBRARY,
        feature_key=feature_key,
        start_line=10,
        end_line=12,
    )


def _build_typescript_feature_definition() -> dict[str, Any]:
    return {
        "description": "swr data fetch hook",
        "absolute_paths": ["swr.default"],
        "target_level": "function",
        "concept": "CallExpression",
        "locator_strategy": "VariableBound",
        "startpoint": False,
        "base_confidence": 0.9,
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
                feature_key=TEST_SOURCE_FEATURE_KEY,
                feature_definition=_build_feature_definition("CallExpression"),
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                feature_key=TEST_CORRECTED_FEATURE_KEY,
                feature_definition=_build_feature_definition("CallExpression"),
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                feature_key=TEST_SOURCE_FEATURE_KEY,
                absolute_path="validatorlib.Client",
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_FEATURE_LANGUAGE,
                library=TEST_FEATURE_LIBRARY,
                feature_key=TEST_CORRECTED_FEATURE_KEY,
                absolute_path="validatorlib.HttpClient",
            )
        )

        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_FILE_PATH,
                feature_language=TEST_FEATURE_LANGUAGE,
                feature_library=TEST_FEATURE_LIBRARY,
                feature_key=TEST_SOURCE_FEATURE_KEY,
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
                feature_key=TEST_TS_FEATURE_KEY,
                feature_definition=_build_typescript_feature_definition(),
            )
        )
        session.add(
            FeatureAbsolutePath(
                language=TEST_TS_FEATURE_LANGUAGE,
                library=TEST_TS_FEATURE_LIBRARY,
                feature_key=TEST_TS_FEATURE_KEY,
                absolute_path="swr.default",
            )
        )
        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_TS_FILE_PATH,
                feature_language=TEST_TS_FEATURE_LANGUAGE,
                feature_library=TEST_TS_FEATURE_LIBRARY,
                feature_key=TEST_TS_FEATURE_KEY,
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


def _get_usage_row(
    postgresql_port: int,
    feature_key: str,
) -> dict[str, object] | None:
    with get_sync_postgres_session(postgresql_port) as session:
        stmt = (
            select(
                UnoplatCodeConfluenceFileFrameworkFeature.match_confidence,
                UnoplatCodeConfluenceFileFrameworkFeature.validation_status,
                UnoplatCodeConfluenceFileFrameworkFeature.evidence_json,
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.file_path == TEST_FILE_PATH
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_language
                == TEST_FEATURE_LANGUAGE
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_library
                == TEST_FEATURE_LIBRARY
            )
            .where(UnoplatCodeConfluenceFileFrameworkFeature.feature_key == feature_key)
            .where(UnoplatCodeConfluenceFileFrameworkFeature.start_line == 10)
            .where(UnoplatCodeConfluenceFileFrameworkFeature.end_line == 12)
        )
        row = session.execute(stmt).one_or_none()
        if row is None:
            return None

        match_confidence, validation_status, evidence_json = row
        return {
            "match_confidence": float(match_confidence),
            "validation_status": str(validation_status),
            "evidence_json": evidence_json,
        }


@pytest.mark.asyncio(loop_scope="session")
async def test_upsert_validation_evidence_updates_source_row(
    seeded_framework_usage,
) -> None:
    request = FrameworkFeatureValidationEvidenceUpsertRequest(
        identity=_build_usage_identity(TEST_SOURCE_FEATURE_KEY),
        decision=FrameworkFeatureValidationDecision.CONFIRM,
        final_confidence=0.81,
        evidence_json={"reason": "Symbol resolves to framework client"},
    )

    result = await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=request,
    )

    assert result.source_row_updated is True
    assert result.corrected_row_upserted is False

    updated_row = _get_usage_row(
        seeded_framework_usage["postgresql_port"],
        TEST_SOURCE_FEATURE_KEY,
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
async def test_upsert_validation_evidence_correct_decision_upserts_corrected_row(
    seeded_framework_usage,
) -> None:
    request = FrameworkFeatureValidationEvidenceUpsertRequest(
        identity=_build_usage_identity(TEST_SOURCE_FEATURE_KEY),
        decision=FrameworkFeatureValidationDecision.CORRECT,
        final_confidence=0.9,
        evidence_json={"reason": "Call belongs to HTTP client"},
        updated_feature_key=TEST_CORRECTED_FEATURE_KEY,
    )

    result = await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=request,
    )

    assert result.source_row_updated is True
    assert result.corrected_row_upserted is True
    assert result.corrected_identity is not None
    assert result.corrected_identity.feature_key == TEST_CORRECTED_FEATURE_KEY

    corrected_row = _get_usage_row(
        seeded_framework_usage["postgresql_port"],
        TEST_CORRECTED_FEATURE_KEY,
    )
    assert corrected_row is not None
    assert corrected_row["validation_status"] == "completed"
    assert corrected_row["match_confidence"] == pytest.approx(0.9)
    evidence_json = corrected_row["evidence_json"]
    assert isinstance(evidence_json, dict)
    assert evidence_json is not None
    corrected_from = evidence_json["corrected_from"]
    assert isinstance(corrected_from, dict)
    assert corrected_from["feature_key"] == TEST_SOURCE_FEATURE_KEY


@pytest.mark.asyncio(loop_scope="session")
async def test_status_transition_enforces_completed_terminal_behavior(
    seeded_framework_usage,
) -> None:
    identity = _build_usage_identity(TEST_SOURCE_FEATURE_KEY)

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
    assert candidate.match_confidence == pytest.approx(0.55)
    assert candidate.validation_status == ValidationStatus.PENDING
    assert candidate.absolute_paths == ["validatorlib.Client"]


@pytest.mark.asyncio(loop_scope="session")
async def test_app_interface_fetch_excludes_low_confidence_call_expression_until_completed(
    seeded_framework_usage,
) -> None:
    initial_rows = await db_get_all_framework_features_for_codebase(
        seeded_framework_usage["codebase_path"],
        TEST_FEATURE_LANGUAGE,
    )
    assert initial_rows == []

    identity = _build_usage_identity(TEST_SOURCE_FEATURE_KEY)
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
    identity = _build_usage_identity(TEST_SOURCE_FEATURE_KEY)
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
async def test_app_interface_fetch_excludes_source_row_after_correct_decision(
    seeded_framework_usage,
) -> None:
    source_identity = _build_usage_identity(TEST_SOURCE_FEATURE_KEY)
    await db_upsert_framework_feature_validation_evidence(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationEvidenceUpsertRequest(
            identity=source_identity,
            decision=FrameworkFeatureValidationDecision.CORRECT,
            final_confidence=0.9,
            evidence_json={"reason": "belongs to corrected feature key"},
            updated_feature_key=TEST_CORRECTED_FEATURE_KEY,
        ),
    )
    await db_set_framework_feature_validation_status(
        codebase_path=seeded_framework_usage["codebase_path"],
        request=FrameworkFeatureValidationStatusTransitionRequest(
            identity=source_identity,
            target_status=ValidationStatus.COMPLETED,
            expected_current_status=ValidationStatus.PENDING,
        ),
    )

    rows = await db_get_all_framework_features_for_codebase(
        seeded_framework_usage["codebase_path"],
        TEST_FEATURE_LANGUAGE,
    )
    assert len(rows) == 1
    assert rows[0]["feature_key"] == TEST_CORRECTED_FEATURE_KEY


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
