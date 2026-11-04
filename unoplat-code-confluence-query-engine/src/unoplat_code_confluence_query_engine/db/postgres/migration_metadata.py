"""Complete application metadata without importing API or worker entrypoints."""

from sqlalchemy import MetaData, literal_column
from unoplat_code_confluence_commons import credentials, flags, repo_models
from unoplat_code_confluence_commons.base_models import framework_models
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase
from unoplat_code_confluence_commons.relational_models import unoplat_code_confluence

from unoplat_code_confluence_query_engine.db.postgres import ai_model_config

# Importing every model-owning module registers its tables on the shared base.
MODEL_MODULES = (
    credentials,
    flags,
    repo_models,
    framework_models,
    unoplat_code_confluence,
    ai_model_config,
)


def application_metadata() -> MetaData:
    """Return isolated metadata with PostgreSQL's canonical index spelling.

    PostgreSQL deparses the JSONB subscript literal with an explicit text cast.
    Alembic otherwise proposes rebuilding this unchanged expression index on
    every check. Normalize only the exact known expression, never omit indexes
    from comparison or mutate the application's live table definitions.
    """
    metadata = MetaData()
    for table in SQLBase.metadata.sorted_tables:
        table.to_metadata(metadata)
    for index in metadata.tables["framework_feature"].indexes:
        if (
            index.name == "framework_feature_startpoint_bool_idx"
            and len(index.expressions) == 1
            and str(index.expressions[0])
            == "coalesce((feature_definition['startpoint'])::boolean, false)"
        ):
            index.expressions[0] = literal_column(
                "COALESCE(feature_definition['startpoint'::text]::boolean, false)"
            )
    return metadata
