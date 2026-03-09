"""Unit tests for framework feature language support helpers."""

from unoplat_code_confluence_query_engine.utils.framework_feature_language_support import (
    APP_INTERFACES_SUPPORTED_LANGUAGES,
    is_app_interfaces_supported,
)


def test_supported_languages_contains_python_and_typescript() -> None:
    assert "python" in APP_INTERFACES_SUPPORTED_LANGUAGES
    assert "typescript" in APP_INTERFACES_SUPPORTED_LANGUAGES


def test_is_supported_returns_true_for_python() -> None:
    assert is_app_interfaces_supported("python") is True


def test_is_supported_returns_true_for_typescript() -> None:
    assert is_app_interfaces_supported("typescript") is True


def test_is_supported_is_case_insensitive() -> None:
    assert is_app_interfaces_supported("TypeScript") is True
    assert is_app_interfaces_supported("Python") is True


def test_is_supported_returns_false_for_javascript() -> None:
    assert is_app_interfaces_supported("javascript") is False


def test_is_supported_returns_false_for_java() -> None:
    assert is_app_interfaces_supported("java") is False


def test_is_supported_returns_false_for_empty_string() -> None:
    assert is_app_interfaces_supported("") is False
