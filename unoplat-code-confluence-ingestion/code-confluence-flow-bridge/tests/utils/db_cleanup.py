# """
# Database cleanup utilities for test isolation.

# Lightweight functions that accept database clients from fixtures to clean
# databases between tests. No connection management - relies on fixtures.
# """


# from typing import Any, Dict, List, Optional

# from loguru import logger
# from sqlalchemy import inspect, text
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Session
# from neomodel.async_.core import AsyncDatabase



# class DatabaseCleanupError(Exception):
#     """Raised when database cleanup fails."""


# def get_table_names_sync(sync_session: Session) -> List[str]:
#     """Get all table names from the database using synchronous session.
    
#     Args:
#         sync_session: A synchronous Session object passed by AsyncSession.run_sync
        
#     Returns:
#         List of table names in the database
#     """
#     # Get the connection from the session
#     connection = sync_session.connection()
#     # Now we can use inspect on the connection
#     return inspect(connection).get_table_names()


# async def cleanup_neo4j_data(adb_client: AsyncDatabase) -> None:
#     """
#     Clean all data from Neo4j database using provided client.
    
#     Args:
#         adb_client: neomodel adb client from fixture
        
#     Returns:
#         Dict with cleanup statistics
        
#     Raises:
#         DatabaseCleanupError: If cleanup fails
#     """
    
    
#     try:
#         # Get counts before deletion for stats
#         try:
#             await adb_client.cypher_query("MATCH ()-[r]->() RETURN count(r) as rel_count")
#             await adb_client.cypher_query("MATCH (n) RETURN count(n) as node_count")
    
#         except Exception as e:
#             logger.debug(f"Could not get pre-cleanup counts: {e}")
        
#         # Delete all data (preserves schema/indexes)
#         await adb_client.cypher_query("MATCH (n) DETACH DELETE n")
        
       
    
        
#     except Exception as e:
#         error_msg = f"Failed to cleanup Neo4j data: {str(e)}"
#         logger.error(error_msg)
#         raise DatabaseCleanupError(error_msg) from e


# async def cleanup_postgresql_data(session: AsyncSession, table_names: Optional[List[str]] = None) -> None:
#     """
#     Clean all data from PostgreSQL tables using provided session.
    
#     Args:
#         session: SQLAlchemy AsyncSession from fixture
#         table_names: Specific tables to clean. If None, cleans all tables
        
#     Returns:
#         Dict with cleanup statistics
        
#     Raises:
#         DatabaseCleanupError: If cleanup fails
#     """
    
#     try:
#         # Get all table names if not provided
#         if table_names is None:
#             all_tables = await session.run_sync(get_table_names_sync)
#             # Filter out system tables and temp tables
#             table_names = [t for t in all_tables if not t.startswith('_')]
        
#         # Disable foreign key checks temporarily for PostgreSQL
#         await session.execute(text("SET session_replication_role = replica;"))
        
#         try:
#             for table_name in table_names:
#                 try:
#                     # Truncate table (faster than DELETE, resets sequences)
#                     await session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                 
                    
#                 except Exception as e:
#                     logger.warning(f"Could not clean table {table_name}: {e}")
#                     # Continue with other tables - some might not exist in all environments
#                     continue
            
#             await session.commit()
            
#         finally:
#             # Re-enable foreign key checks
#             await session.execute(text("SET session_replication_role = DEFAULT;"))
#             await session.commit()

        
#     except Exception as e:
#         await session.rollback()
#         error_msg = f"Failed to cleanup PostgreSQL data: {str(e)}"
#         logger.error(error_msg)
#         raise DatabaseCleanupError(error_msg) from e


# async def cleanup_all_databases(adb_client: AsyncDatabase, postgres_session: AsyncSession) -> Dict[str, Any]:
#     """
#     Clean both Neo4j and PostgreSQL databases using provided clients.
    
#     Args:
#         adb_client: neomodel adb client from fixture
#         postgres_session: SQLAlchemy AsyncSession from fixture
        
#     Returns:
#         Dict with cleanup statistics from both databases
        
#     Raises:
#         DatabaseCleanupError: If any cleanup fails critically
#     """
   
#     # Clean Neo4j first (usually faster)
#     try:
#         await cleanup_neo4j_data(adb_client)
#     except DatabaseCleanupError as e:
#         logger.error(f"Neo4j cleanup failed: {e}")
    
#     # Clean PostgreSQL
#     try:
#         await cleanup_postgresql_data(postgres_session)
#     except DatabaseCleanupError as e:
#         logger.error(f"PostgreSQL cleanup failed: {e}")
    
#     logger.debug("All databases cleaned successfully")
    
#     return {"neo4j_cleaned": True, "postgresql_cleaned": True}


# async def verify_databases_empty(adb_client: AsyncDatabase, postgres_session: AsyncSession) -> None:
#     """
#     Verify that databases are empty after cleanup.
    
#     Args:
#         adb_client: neomodel adb client from fixture
#         postgres_session: SQLAlchemy AsyncSession from fixture
        
#     Returns:
#         Dict indicating if each database is empty
#     """
    
    
#     # Check Neo4j
#     try:
#         await adb_client.cypher_query("MATCH (n) RETURN count(n) as node_count")
        
        
#     except Exception as e:
#         logger.warning(f"Could not verify Neo4j state: {e}")
    
#     # Check PostgreSQL - sample key tables
#     try:
#         tables_to_check = ["repository_workflow_run", "codebase_workflow_run", "workflow_execution"]
#         postgres_empty = True
        
#         for table in tables_to_check:
#             try:
#                 result = await postgres_session.execute(text(f"SELECT COUNT(*) FROM {table}"))
#                 count = result.scalar()
#                 if count > 0:
#                     postgres_empty = False
#                     logger.debug(f"Table {table} is not empty: {count} rows")
#                     break
#             except Exception:
#                 # Table might not exist, continue checking others
#                 continue
        
#         if postgres_empty:
#             logger.debug("PostgreSQL tables verified as empty")
        
#     except Exception as e:
#         logger.warning(f"Could not verify PostgreSQL state: {e}")


# async def quick_cleanup(adb_client: AsyncDatabase, postgres_session: AsyncSession) -> bool:
#     """
#     Quick database cleanup with minimal logging for test use.
    
#     Args:
#         adb_client: neomodel adb client from fixture
#         postgres_session: SQLAlchemy AsyncSession from fixture
        
#     Returns:
#         True if cleanup successful, False otherwise
#     """
#     try:
#         await cleanup_all_databases(adb_client, postgres_session)
#         return True
#     except Exception as e:
#         logger.error(f"Quick cleanup failed: {e}")
#         return False


# # Specific cleanup functions for common scenarios
# async def cleanup_repository_data(adb_client: AsyncDatabase, postgres_session: AsyncSession, repository_qualified_name: str) -> None:
#     """
#     Clean data related to a specific repository or all repositories.
    
#     Args:
#         adb_client: neomodel adb client from fixture
#         postgres_session: SQLAlchemy AsyncSession from fixture  
#         repository_qualified_name: Specific repository to clean, or None for all
        
#     Returns:
#         Dict with cleanup statistics
#     """
    
    
#     try:
#         if repository_qualified_name:
#             # Clean specific repository
#             neo4j_query = f"MATCH (r:CodeConfluenceGitRepository {{qualified_name: '{repository_qualified_name}'}}) DETACH DELETE r"
#             await adb_client.cypher_query(neo4j_query)
            
#             postgres_query = text("DELETE FROM repository_workflow_run WHERE repository_name = :repo_name")
#             await postgres_session.execute(postgres_query, {"repo_name": repository_qualified_name})
#             await postgres_session.commit()
            
            
#         else:
#             # Clean all repositories - use full cleanup
#             await cleanup_all_databases(adb_client, postgres_session)
        
#         logger.debug(f"Repository cleanup completed")
        
        
#     except Exception as e:
#         await postgres_session.rollback()
#         error_msg = f"Failed to cleanup repository data: {str(e)}"
#         logger.error(error_msg)
#         raise DatabaseCleanupError(error_msg) from e