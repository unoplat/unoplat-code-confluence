"""Integration tests for business-logic data-model repository lookups."""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import delete
from unoplat_code_confluence_commons.base_models import Framework, FrameworkFeature
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
    UnoplatCodeConfluenceGitRepository,
)

from tests.utils.sync_db_utils import get_sync_postgres_session
from unoplat_code_confluence_query_engine.db.postgres.code_confluence_business_logic_repository import (
    db_get_data_model_files,
)

TEST_REPOSITORY_QUALIFIED_NAME = "business-owner/business-repo"
TEST_CODEBASE_QUALIFIED_NAME = "business-owner/business-repo:business-codebase"
TEST_CODEBASE_PATH = "/tmp/business-codebase"
TEST_PYDANTIC_FILE_PATH = "/tmp/business-codebase/domain/models.py"
TEST_SQL_FILE_PATH = "/tmp/business-codebase/domain/sql_models.py"
TEST_LANGUAGE = "python"
TEST_PYDANTIC_LIBRARY = "business-pydantic"
TEST_SQL_LIBRARY = "business-sqlmodel"


def _build_feature_definition(concept: str) -> dict[str, Any]:
    return {
        "description": "test feature",
        "absolute_paths": ["businesslib.Model"],
        "target_level": "class",
        "concept": concept,
        "locator_strategy": "VariableBound",
        "startpoint": False,
    }


@pytest.fixture
def seeded_namespaced_data_model_usage(service_ports, test_database_tables, db_connections):
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
                FrameworkFeature.language == TEST_LANGUAGE,
                FrameworkFeature.library.in_(
                    [
                        TEST_PYDANTIC_LIBRARY,
                        TEST_SQL_LIBRARY,
                    ]
                ),
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_LANGUAGE,
                Framework.library.in_(
                    [
                        TEST_PYDANTIC_LIBRARY,
                        TEST_SQL_LIBRARY,
                    ]
                ),
            )
        )

        session.add(
            UnoplatCodeConfluenceGitRepository(
                qualified_name=TEST_REPOSITORY_QUALIFIED_NAME,
                repository_url="https://example.com/business-repo.git",
                repository_name="business-repo",
            )
        )
        session.add(
            UnoplatCodeConfluenceCodebase(
                qualified_name=TEST_CODEBASE_QUALIFIED_NAME,
                repository_qualified_name=TEST_REPOSITORY_QUALIFIED_NAME,
                name="business-codebase",
                codebase_path=TEST_CODEBASE_PATH,
                programming_language=TEST_LANGUAGE,
            )
        )
        session.add(
            UnoplatCodeConfluenceFile(
                file_path=TEST_PYDANTIC_FILE_PATH,
                codebase_qualified_name=TEST_CODEBASE_QUALIFIED_NAME,
                imports=[],
                has_data_model=False,
                data_model_positions={},
            )
        )
        session.add(
            UnoplatCodeConfluenceFile(
                file_path=TEST_SQL_FILE_PATH,
                codebase_qualified_name=TEST_CODEBASE_QUALIFIED_NAME,
                imports=[],
                has_data_model=False,
                data_model_positions={},
            )
        )

        session.add(
            Framework(
                language=TEST_LANGUAGE,
                library=TEST_PYDANTIC_LIBRARY,
            )
        )
        session.add(
            Framework(
                language=TEST_LANGUAGE,
                library=TEST_SQL_LIBRARY,
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_LANGUAGE,
                library=TEST_PYDANTIC_LIBRARY,
                capability_key="data_model",
                operation_key="data_model",
                feature_definition=_build_feature_definition("Inheritance"),
            )
        )
        session.add(
            FrameworkFeature(
                language=TEST_LANGUAGE,
                library=TEST_SQL_LIBRARY,
                capability_key="relational_database",
                operation_key="db_data_model",
                feature_definition=_build_feature_definition("Inheritance"),
            )
        )

        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_PYDANTIC_FILE_PATH,
                feature_language=TEST_LANGUAGE,
                feature_library=TEST_PYDANTIC_LIBRARY,
                feature_capability_key="data_model",
                feature_operation_key="data_model",
                start_line=5,
                end_line=22,
                match_text="User",
                match_confidence=0.92,
                validation_status="completed",
                evidence_json=None,
            )
        )
        session.add(
            UnoplatCodeConfluenceFileFrameworkFeature(
                file_path=TEST_SQL_FILE_PATH,
                feature_language=TEST_LANGUAGE,
                feature_library=TEST_SQL_LIBRARY,
                feature_capability_key="relational_database",
                feature_operation_key="db_data_model",
                start_line=10,
                end_line=34,
                match_text="InvoiceRecord",
                match_confidence=0.88,
                validation_status="completed",
                evidence_json=None,
            )
        )

    yield {"codebase_path": TEST_CODEBASE_PATH}

    with get_sync_postgres_session(postgresql_port) as session:
        session.execute(
            delete(UnoplatCodeConfluenceGitRepository).where(
                UnoplatCodeConfluenceGitRepository.qualified_name
                == TEST_REPOSITORY_QUALIFIED_NAME
            )
        )
        session.execute(
            delete(FrameworkFeature).where(
                FrameworkFeature.language == TEST_LANGUAGE,
                FrameworkFeature.library.in_(
                    [
                        TEST_PYDANTIC_LIBRARY,
                        TEST_SQL_LIBRARY,
                    ]
                ),
            )
        )
        session.execute(
            delete(Framework).where(
                Framework.language == TEST_LANGUAGE,
                Framework.library.in_(
                    [
                        TEST_PYDANTIC_LIBRARY,
                        TEST_SQL_LIBRARY,
                    ]
                ),
            )
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_get_data_model_files_includes_namespaced_data_model_feature_keys(
    seeded_namespaced_data_model_usage,
) -> None:
    span_map = await db_get_data_model_files(
        seeded_namespaced_data_model_usage["codebase_path"]
    )

    assert TEST_PYDANTIC_FILE_PATH in span_map
    assert TEST_SQL_FILE_PATH in span_map
    assert span_map[TEST_PYDANTIC_FILE_PATH]["User"] == (5, 22)
    assert span_map[TEST_SQL_FILE_PATH]["InvoiceRecord"] == (10, 34)
