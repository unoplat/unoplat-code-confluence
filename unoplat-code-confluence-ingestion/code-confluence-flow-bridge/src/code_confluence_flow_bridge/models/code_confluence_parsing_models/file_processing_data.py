"""File processing data model."""

from typing import List

from pydantic import BaseModel, Field


class FileProcessingData(BaseModel):
    """Data structure for file processing."""

    file_path: str = Field(description="Absolute path to the source file")
    content: str = Field(description="Full content of the file")
    checksum: str = Field(description="MD5 checksum of the file content")
    imports: List[str] = Field(description="List of import statements in the file")
    poi_labels: List[str] = Field(description="Points of interest labels for the file")
    package_qualified_name: str = Field(
        description="Qualified name of the containing package"
    )
