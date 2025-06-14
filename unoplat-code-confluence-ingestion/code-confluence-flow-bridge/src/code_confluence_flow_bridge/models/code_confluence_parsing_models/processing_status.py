"""Processing status enumeration."""

from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of file processing operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"