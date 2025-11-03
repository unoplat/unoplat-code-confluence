"""Neo4j repository for framework/library overview queries.

Centralizes graph reads so tools and services reuse the same DB layer.
"""

from __future__ import annotations

from typing import Dict, List

from neo4j import AsyncManagedTransaction

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)


async def _txn_check_codebase_exists(
    tx: AsyncManagedTransaction, codebase_path: str
) -> bool:
    query = """
    MATCH (cb:CodeConfluenceCodebase {codebase_path: $codebase_path})
    RETURN cb IS NOT NULL as exists
    """
    result = await tx.run(query, {"codebase_path": codebase_path})
    record = await result.single()
    return bool(record and record.get("exists"))


async def _txn_list_framework_libraries(
    tx: AsyncManagedTransaction, codebase_path: str
) -> List[str]:
    query = """
    MATCH (cb:CodeConfluenceCodebase {codebase_path: $codebase_path})
    -[:USES_FRAMEWORK]->(fw:CodeConfluenceFramework)
    RETURN DISTINCT fw.library as library
    ORDER BY fw.library
    """
    result = await tx.run(query, {"codebase_path": codebase_path})
    records = await result.data()
    return [r["library"] for r in records]


async def _txn_get_framework_with_features(
    tx: AsyncManagedTransaction, codebase_path: str, library: str
) -> Dict:
    query = """
    MATCH (cb:CodeConfluenceCodebase {codebase_path: $codebase_path})
    -[:USES_FRAMEWORK]->(fw:CodeConfluenceFramework {library: $library})
    OPTIONAL MATCH (fw)-[:HAS_FEATURE]->(feat:CodeConfluenceFrameworkFeature)
    WHERE NOT feat.feature_key IN ['data_model', 'db_data_model']
    OPTIONAL MATCH (feat)<-[usage:USES_FEATURE]-(file:CodeConfluenceFile)
    WITH fw, feat, 
         collect(DISTINCT CASE 
             WHEN file.file_path IS NOT NULL 
             THEN {
                 file_path: file.file_path, 
                 start_line: usage.start_line, 
                 end_line: usage.end_line
             } 
             ELSE NULL 
         END) as usage_locations
    WHERE feat IS NOT NULL
    WITH fw, collect({
        feature_key: feat.feature_key,
        startpoint: coalesce(feat.startpoint, false),
        usages: [u IN usage_locations WHERE u IS NOT NULL]
    }) as features
    RETURN fw.library as library,
           features
    """
    result = await tx.run(
        query, {"codebase_path": codebase_path, "library": library}
    )
    record = await result.single()
    if not record:
        return {"library": library, "features": []}
    return {"library": record["library"], "features": record.get("features") or []}


async def db_check_codebase_exists(
    neo4j_manager: CodeConfluenceGraphQueryEngine, codebase_path: str
) -> bool:
    async with neo4j_manager.get_session() as session:
        return await session.execute_read(_txn_check_codebase_exists, codebase_path)


async def db_list_framework_libraries(
    neo4j_manager: CodeConfluenceGraphQueryEngine, codebase_path: str
) -> List[str]:
    async with neo4j_manager.get_session() as session:
        return await session.execute_read(_txn_list_framework_libraries, codebase_path)


async def db_get_framework_with_features(
    neo4j_manager: CodeConfluenceGraphQueryEngine, codebase_path: str, library: str
) -> Dict:
    async with neo4j_manager.get_session() as session:
        return await session.execute_read(
            _txn_get_framework_with_features, codebase_path, library
        )


