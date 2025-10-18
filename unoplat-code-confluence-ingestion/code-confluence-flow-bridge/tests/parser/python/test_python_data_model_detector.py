"""Test validation for Python data model detection.

This module verifies that the Python data model detector correctly identifies
dataclass-decorated classes and extracts their names and line positions.
"""

from pathlib import Path

import pytest

from src.code_confluence_flow_bridge.detector.python.python_data_model_detector_strategy import (
    PythonDataModelDetectorStrategy,
)


@pytest.fixture
def detector_strategy() -> PythonDataModelDetectorStrategy:
    """Fixture providing a PythonDataModelDetectorStrategy instance."""
    return PythonDataModelDetectorStrategy()


def test_detect_dataclass_annotations(
    detector_strategy: PythonDataModelDetectorStrategy,
) -> None:
    """Test detection of @dataclass decorator with proper line positions."""
    source_code = """from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

@dataclass
class UserProfile:
    user: User
    bio: str
"""

    has_data_model, data_model_positions = detector_strategy.detect(source_code)

    # Verify detection works
    assert has_data_model is True
    assert len(data_model_positions.positions) == 2

    # Verify User dataclass
    assert "User" in data_model_positions.positions
    assert data_model_positions.positions["User"] == (4, 6)

    # Verify UserProfile dataclass
    assert "UserProfile" in data_model_positions.positions
    assert data_model_positions.positions["UserProfile"] == (9, 11)
