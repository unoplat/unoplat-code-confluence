"""Security utilities for safe logging and data handling."""


def mask_sensitive_string(value: str, visible_chars: int = 4) -> str:
    """Mask a sensitive string for safe logging, showing only first/last few chars.

    Args:
        value: The sensitive string to mask.
        visible_chars: Number of characters to show at start and end (default: 4).

    Returns:
        Masked string like "sk-a****xyz" or "****" if too short.
    """
    if not value:
        return ""
    if len(value) <= visible_chars * 2:
        return "*" * len(value)
    return f"{value[:visible_chars]}{'*' * max(4, len(value) - visible_chars * 2)}{value[-visible_chars:]}"
