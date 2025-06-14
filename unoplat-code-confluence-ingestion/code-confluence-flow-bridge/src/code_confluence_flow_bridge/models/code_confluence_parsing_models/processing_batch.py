"""Processing batch model."""

from typing import List

from pydantic import BaseModel, Field

from .file_processing_data import FileProcessingData


class ProcessingBatch(BaseModel):
    """Represents a batch of files for processing."""
    batch_id: str = Field(description="Unique identifier for the batch")
    files: List[FileProcessingData] = Field(description="List of files in this batch")
    total_files: int = Field(description="Total number of files in the batch")
    batch_size: int = Field(description="Maximum number of files per batch")