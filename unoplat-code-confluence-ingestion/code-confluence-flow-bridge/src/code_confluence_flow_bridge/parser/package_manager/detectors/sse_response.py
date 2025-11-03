"""
Server-Sent Events (SSE) Response implementation for FastAPI.

This module provides SSE response classes and utilities for streaming
real-time updates during codebase detection operations.

Now uses sse-starlette for standards-compliant SSE implementation.
"""

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, AsyncGenerator, Dict, Optional


class SSEMessage:
    """Helper class for formatting SSE messages as dictionaries for sse-starlette."""
    
    @staticmethod
    def format_sse(
        data: Any,
        event: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Format data as a Server-Sent Event message dictionary for sse-starlette.
        
        Args:
            data: The data to send (will be JSON-encoded if not a string)
            event: Optional event type
            id: Optional event ID
            retry: Optional reconnection time in milliseconds
            
        Returns:
            Dictionary with event, data, and id keys for sse-starlette
        """
        # Convert data to JSON if it's not already a string
        if not isinstance(data, str):
            data = json.dumps(data, default=str)
        
        result = {
            "data": data,
        }
        
        if event is not None:
            result["event"] = event
            
        if id is not None:
            result["id"] = id
            
        # Note: sse-starlette handles retry directive through other mechanisms
        
        return result
    
    @staticmethod
    def comment(text: str) -> str:
        """
        Format a comment for SSE (starts with :).
        Used for keeping connection alive.
        
        Args:
            text: Comment text
            
        Returns:
            Formatted SSE comment
        """
        # Comments in SSE start with : and end with \n\n
        return f": {text}\n\n"
    
    @staticmethod
    def connected(event_id: Optional[str] = None) -> Dict[str, str]:
        """Generate a connection established event."""
        return SSEMessage.format_sse(
            data={"status": "connected"},
            event="connected",
            id=event_id
        )
    
    @staticmethod
    def progress(
        current: int,
        total: Optional[int] = None,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a progress update event.
        
        Args:
            current: Current progress value
            total: Total expected value (for percentage calculation)
            message: Progress message
            details: Additional details to include
            event_id: Optional event ID
            
        Returns:
            SSE progress event dictionary
        """
        data = {
            "current": current,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if total is not None:
            data["total"] = total
            data["percentage"] = round((current / total) * 100, 2) if total > 0 else 0
            
        if details:
            data["details"] = details
            
        return SSEMessage.format_sse(data=data, event="progress", id=event_id)
    
    @staticmethod
    def error(error_message: str, error_type: Optional[str] = None, event_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate an error event.
        
        Args:
            error_message: Error message
            error_type: Optional error type/category
            event_id: Optional event ID
            
        Returns:
            SSE error event dictionary
        """
        data = {
            "error": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if error_type:
            data["type"] = error_type
            
        return SSEMessage.format_sse(data=data, event="error", id=event_id)
    
    @staticmethod
    def result(data: Any, event_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a result event.
        
        Args:
            data: Result data
            event_id: Optional event ID
            
        Returns:
            SSE result event dictionary
        """
        return SSEMessage.format_sse(
            data=data,
            event="result",
            id=event_id
        )
    
    @staticmethod
    def done(event_id: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a completion event.
        
        Args:
            event_id: Optional event ID
            
        Returns:
            SSE done event dictionary
        """
        return SSEMessage.format_sse(
            data={"status": "complete"},
            event="done",
            id=event_id
        )


async def heartbeat_generator(
    interval: int = 30
) -> AsyncGenerator[str, None]:
    """
    Generate heartbeat comments to keep connection alive.
    
    Args:
        interval: Seconds between heartbeats
        
    Yields:
        SSE comment messages
    """
    while True:
        await asyncio.sleep(interval)
        yield SSEMessage.comment(f"heartbeat {datetime.now(timezone.utc).isoformat()}")