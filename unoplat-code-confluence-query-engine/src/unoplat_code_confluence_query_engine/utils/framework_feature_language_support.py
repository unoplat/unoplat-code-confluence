"""Language support constants for framework feature app-interfaces pipeline."""

APP_INTERFACES_SUPPORTED_LANGUAGES: frozenset[str] = frozenset({"python", "typescript"})


def is_app_interfaces_supported(language: str) -> bool:
    """Check whether the given language is supported by the app-interfaces pipeline."""
    return language.lower() in APP_INTERFACES_SUPPORTED_LANGUAGES
