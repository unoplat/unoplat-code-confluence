"""
Progress tracking models for codebase detection with SSE support.

Simple models for tracking detection progress during SSE streaming.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# Import the actual CodebaseConfig model
from src.code_confluence_flow_bridge.models.configuration.settings import CodebaseConfig


class DetectionState(str, Enum):
    """States of the codebase detection process."""
    INITIALIZING = "initializing"
    CLONING = "cloning" 
    ANALYZING = "analyzing"
    COMPLETE = "complete"


class DetectionProgress(BaseModel):
    """Progress tracking for codebase detection."""
    state: DetectionState = Field(description="Current state of detection")
    message: str = Field(description="Human-readable progress message")
    repository_url: str = Field(description="Repository being analyzed")


class DetectionRequest(BaseModel):
    """Request model for codebase detection via SSE."""
    git_url: str = Field(description="GitHub repository URL")
    
    
class DetectionResult(BaseModel):
    """Final result of codebase detection."""
    repository_url: str = Field(description="Repository that was analyzed")
    duration_seconds: float = Field(description="Total time taken for detection")
    codebases: List[CodebaseConfig] = Field(description="List of detected codebases")
    error: Optional[str] = Field(None, description="Error message if detection failed")