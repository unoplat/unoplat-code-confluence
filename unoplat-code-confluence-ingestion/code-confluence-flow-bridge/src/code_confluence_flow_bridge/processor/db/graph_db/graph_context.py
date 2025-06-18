"""
Context manager for CodeConfluenceGraphIngestion with proper lifecycle management.

This module provides a context manager to ensure each activity gets its own
Neo4j session and driver, preventing "Transaction in progress" errors that
occur when multiple activities share the same session.
"""

from contextlib import asynccontextmanager
from typing import Optional

from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion


@asynccontextmanager
async def graph_ingestion_ctx(env_settings: Optional[EnvironmentSettings] = None):
    """
    Context manager for CodeConfluenceGraphIngestion with proper lifecycle management.
    
    Creates a fresh CodeConfluenceGraphIngestion instance with its own Neo4j driver
    and session, initializes it, yields it for use, and ensures proper cleanup.
    
    Args:
        env_settings: Optional environment settings. If None, creates from environment.
        
    Yields:
        CodeConfluenceGraphIngestion: Initialized graph ingestion instance
        
    Example:
        async with graph_ingestion_ctx() as graph:
            await graph.insert_code_confluence_git_repo(repo)
    """
    if env_settings is None:
        env_settings = EnvironmentSettings()
    
    graph = CodeConfluenceGraphIngestion(code_confluence_env=env_settings)
    await graph.initialize()
    try:
        yield graph
    finally:
        await graph.close()