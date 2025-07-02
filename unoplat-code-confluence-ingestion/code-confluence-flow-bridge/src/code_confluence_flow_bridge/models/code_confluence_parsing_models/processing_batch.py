"""Processing batch model."""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.file_processing_data import (
    FileProcessingData,
)

from typing import List

from pydantic import BaseModel, Field


class ProcessingBatch(BaseModel):
    """Represents a batch of files for processing."""
    batch_id: str = Field(description="Unique identifier for the batch")
    files: List[FileProcessingData] = Field(description="List of files in this batch")
    total_files: int = Field(description="Total number of files in the batch")
    batch_size: int = Field(description="Maximum number of files per batch")