"""
Server-Sent Events (SSE) Response implementation for FastAPI.

This module provides SSE response classes and utilities for streaming
real-time updates during codebase detection operations.
"""

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi.responses import StreamingResponse


class EventSourceResponse(StreamingResponse):
    """
    A FastAPI response class for Server-Sent Events (SSE).
    
    Automatically sets the correct headers for SSE and provides
    helper methods for formatting SSE messages.
    """
    
    def __init__( #type: ignore
        self,
        content: AsyncGenerator[str, None],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        media_type: str = "text/event-stream",
        background = None, 
    ) -> None: 
        """
        Initialize EventSourceResponse with SSE-specific headers.
        
        Args:
            content: Async generator yielding SSE-formatted strings
            status_code: HTTP status code
            headers: Additional headers to include
            media_type: Content type (defaults to text/event-stream)
            background: Background tasks to run after response
        """
        # Set default SSE headers
        default_headers = {
            "Content-Type": "text/event-stream; charset=utf-8",
        }
        
        # Merge with user-provided headers
        if headers:
            default_headers.update(headers)
            
        super().__init__(
            content=content,
            status_code=status_code,
            headers=default_headers,
            media_type=media_type,
            background=background
        )


class SSEMessage:
    """Helper class for formatting SSE messages."""
    
    @staticmethod
    def format_sse(
        data: Any,
        event: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None
    ) -> str:
        """
        Format data as a Server-Sent Event message.
        
        Args:
            data: The data to send (will be JSON-encoded if not a string)
            event: Optional event type
            id: Optional event ID
            retry: Optional reconnection time in milliseconds
            
        Returns:
            Formatted SSE message string
        """
        lines = []
        
        if id is not None:
            lines.append(f"id: {id}")
            
        if event is not None:
            lines.append(f"event: {event}")
            
        if retry is not None:
            lines.append(f"retry: {retry}")
            
        # Convert data to JSON if it's not already a string
        if not isinstance(data, str):
            data = json.dumps(data, default=str)
            
        # Handle multi-line data
        for line in data.splitlines():
            lines.append(f"data: {line}")
            
        # SSE messages must end with double newline
        return "\n".join(lines) + "\n\n"
    
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
        return f": {text}\n\n"
    
    @staticmethod
    def connected() -> str:
        """Generate a connection established event."""
        return SSEMessage.format_sse(
            data={"status": "connected"},
            event="connected"
        )
    
    @staticmethod
    def progress(
        current: int,
        total: Optional[int] = None,
        message: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a progress update event.
        
        Args:
            current: Current progress value
            total: Total expected value (for percentage calculation)
            message: Progress message
            details: Additional details to include
            
        Returns:
            Formatted SSE progress event
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
            
        return SSEMessage.format_sse(data=data, event="progress")
    
    @staticmethod
    def error(error_message: str, error_type: Optional[str] = None) -> str:
        """
        Generate an error event.
        
        Args:
            error_message: Error message
            error_type: Optional error type/category
            
        Returns:
            Formatted SSE error event
        """
        data = {
            "error": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if error_type:
            data["type"] = error_type
            
        return SSEMessage.format_sse(data=data, event="error")
    
    @staticmethod
    def result(data: Any) -> str:
        """
        Generate a result event.
        
        Args:
            data: Result data
            
        Returns:
            Formatted SSE result event
        """
        return SSEMessage.format_sse(
            data=data,
            event="result"
        )
    
    @staticmethod
    def done() -> str:
        """
        Generate a completion event.
        
        Returns:
            Formatted SSE done event
        """
        return SSEMessage.format_sse(
            data={"status": "complete"},
            event="done"
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