"""ORM events service for hot-reload functionality of AI model configuration.

NOTE: Not required in the current single-worker setup. We now refresh
agents immediately in the PUT /v1/config endpoint. This module remains as
scaffolding and will be replaced with a Postgres LISTEN/NOTIFY-based
invalidation so changes propagate across workers when we move to multi-worker.
"""

from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from loguru import logger
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    create_code_confluence_agents,
)
from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.services.ai_model_config_service import (
    AiModelConfigService,
)
from unoplat_code_confluence_query_engine.services.model_factory import ModelFactory

if TYPE_CHECKING:
    from fastapi import FastAPI

# Global state for tracking configuration changes and model instances
_config_invalidated = False
_current_model: Optional[Model] = None
_current_model_settings: Optional[ModelSettings] = None
_model_factory = ModelFactory()

# Flag used in session.info to track config changes
_CHANGED_FLAG = "ai_config_changed"


def _mark_if_config_changed(session: Session, flush_context: Any, instances: Any) -> None:
    """Mark session if AiModelConfig changed during flush.

    NOTE: Currently not required in single-worker mode. Kept until we migrate
    to a Postgres LISTEN/NOTIFY invalidation strategy for multi-worker.
    
    This event handler runs during before_flush to detect configuration changes.
    It's synchronous and lightweight, only setting a flag.
    
    Args:
        session: SQLAlchemy session
        flush_context: Flush context (unused)
        instances: Instances being flushed (unused)
    """
    try:
        # Check for creations/deletions (always require rebuild)
        if any(isinstance(obj, AiModelConfig) for obj in session.new):
            session.info[_CHANGED_FLAG] = True
            logger.debug("AI config creation detected, marking for rebuild")
            return
        
        if any(isinstance(obj, AiModelConfig) for obj in session.deleted):
            session.info[_CHANGED_FLAG] = True
            logger.debug("AI config deletion detected, marking for rebuild")
            return
        
        # Check for updates: only if real attribute changes (avoid no-op dirty)
        for obj in session.dirty:
            if not isinstance(obj, AiModelConfig):
                continue
            
            state = inspect(obj)
            config_fields = [
                'provider_key', 'provider_kind', 'model_name', 'base_url', 
                'profile_key', 'extra_config', 'temperature', 'top_p', 'max_tokens'
            ]
            
            # Check if any configuration field has actual changes
            changed: List[str] = [
                field for field in config_fields
                if getattr(state.attrs, field).history.has_changes()
            ]
            if changed:
                session.info[_CHANGED_FLAG] = True
                logger.debug(
                    "AI config update detected (changed fields: {}), marking for rebuild",
                    changed,
                )
                return
                
    except Exception as e:
        logger.error("Error in config change detection: {}", e)
        # Don't raise - event handlers should not break the transaction


def _invalidate_config_on_commit(session: Session) -> None:
    """Invalidate current model configuration after successful commit.

    NOTE: Currently not required in single-worker mode. Kept until adoption of
    Postgres LISTEN/NOTIFY for cross-worker invalidation.
    
    This event handler runs after_commit to invalidate the model when changes are persisted.
    It's safe to run after the transaction completes.
    
    Args:
        session: SQLAlchemy session
    """
    global _config_invalidated, _current_model
    
    try:
        # Only invalidate if changes were detected
        if session.info.get(_CHANGED_FLAG):
            _config_invalidated = True
            _current_model = None
            logger.info("AI model configuration invalidated after commit")
            logger.debug(
                "Hot reload state -> invalidated={}, model_present={}, settings_present={}",
                _config_invalidated,
                False,
                _current_model_settings is not None,
            )
            
            # Clear the flag for next transaction
            session.info.pop(_CHANGED_FLAG, None)
            
    except Exception as e:
        logger.error("Error in config invalidation: {}", e)
        # Don't raise - event handlers should not break post-commit cleanup


async def get_current_model() -> Tuple[Optional[Model], Optional[ModelSettings]]:
    """Get the current AI model, rebuilding if configuration changed.

    NOTE: In the current setup, agents are explicitly refreshed after PUT
    /v1/config. This lazy-rebuild path is retained for future LISTEN/NOTIFY
    migration and as a safety net.
    
    This implements lazy rebuilding - the model is only rebuilt when actually requested
    after a configuration change.
    
    Returns:
        Current Pydantic AI model instance and settings, or None if no configuration exists
    """
    global _config_invalidated, _current_model, _current_model_settings
    
    try:
        # If model is valid and not invalidated, return cached instance
        logger.debug(
            "Hot reload cache check: invalidated={}, cached_model_present={}, cached_settings_present={}",
            _config_invalidated,
            _current_model is not None,
            _current_model_settings is not None,
        )
        if _current_model is not None and not _config_invalidated:
            logger.debug("Returning cached model without rebuild")
            return _current_model, _current_model_settings
        
        # Need to rebuild - fetch current configuration
        service = AiModelConfigService()
        config = await service.get_config()
        
        if config is None:
            logger.debug("No AI model configuration found")
            _current_model = None
            _current_model_settings = None
            _config_invalidated = False
            return None, None
        
        # Build new model from configuration
        logger.info("Building AI model from config: provider={}, model={}", 
                   config.provider_key, config.model_name)
        
        _current_model, _current_model_settings = await _model_factory.build(config)
        _config_invalidated = False
        
        logger.info("AI model rebuilt successfully")
        logger.debug(
            "Rebuild result -> model_present={}, settings_present={}, invalidated={}",
            _current_model is not None,
            _current_model_settings is not None,
            _config_invalidated,
        )
        return _current_model, _current_model_settings
        
    except Exception as e:
        logger.error("Error rebuilding AI model: {}", e)
        _current_model = None
        _config_invalidated = False
        return None


def register_orm_events() -> None:
    """Register SQLAlchemy ORM event listeners for hot-reload functionality.

    NOTE: Not required right now (single-worker). Retained temporarily; will be
    replaced by Postgres LISTEN/NOTIFY-based invalidation across workers.
    This should be called once during application startup to set up the event handlers.
    """
    try:
        # Register before_flush event to detect changes
        event.listen(Session, 'before_flush', _mark_if_config_changed)
        
        # Register after_commit event to invalidate on successful transaction
        event.listen(Session, 'after_commit', _invalidate_config_on_commit)
        
        logger.info("AI model config hot-reload events registered")
        
    except Exception as e:
        logger.error("Failed to register ORM events: {}", e)
        raise


def unregister_orm_events() -> None:
    """Unregister ORM event listeners.

    NOTE: Not required right now (single-worker). Retained temporarily; will be
    replaced by Postgres LISTEN/NOTIFY-based invalidation across workers.
    This should be called during application shutdown for cleanup.
    """
    try:
        event.remove(Session, 'before_flush', _mark_if_config_changed)
        event.remove(Session, 'after_commit', _invalidate_config_on_commit)
        
        logger.info("AI model config hot-reload events unregistered")
        
    except Exception as e:
        logger.warning("Error unregistering ORM events: {}", e)


async def update_app_agents(app: "FastAPI") -> None:
    """Update application agents with current model configuration.

    NOTE: This is the explicit refresh used now after PUT /v1/config. When we
    add LISTEN/NOTIFY, workers will invoke this on notifications.

    This should be called when the application needs to refresh its agents
    with the latest model configuration.
    
    Args:
        app: FastAPI application instance with agents in app.state
    """
    try:
        # Get the current model (will rebuild if needed)
        current_model, current_model_settings = await get_current_model()
        
        if current_model is None:
            logger.warning("No model configuration available, keeping existing agents")
            return
        
        # Recreate agents with new model
        logger.info("Updating application agents with new model configuration")
        try:
            before_keys = list(getattr(app.state, 'agents', {}).keys())  # type: ignore[attr-defined]
        except Exception:
            before_keys = []
        logger.debug("Agents before update: {}", before_keys)
        app.state.agents = create_code_confluence_agents(app.state.mcp_manager, current_model, current_model_settings)
        after_keys = list(app.state.agents.keys())
        logger.info("Application agents updated successfully")
        logger.debug("Agents after update: {}", after_keys)
        
    except Exception as e:
        logger.error("Failed to update application agents: {}", e)
        raise


def force_model_rebuild() -> None:
    """Force a model rebuild on next request.

    NOTE: Not required in current explicit-refresh flow but kept as utility
    until LISTEN/NOTIFY invalidation is implemented.

    This can be called programmatically to invalidate the current model cache.
    Useful for testing or manual configuration refresh.
    """
    global _config_invalidated
    _config_invalidated = True
    logger.info("Forced AI model configuration invalidation")
