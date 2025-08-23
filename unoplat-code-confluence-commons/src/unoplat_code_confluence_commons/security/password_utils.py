"""Password and token encryption utilities using Fernet symmetric encryption."""

import os

from cryptography.fernet import Fernet

# Initialize Fernet for symmetrical encryption (where we need to decrypt later)
# For tokens that need to be retrieved in their original form
_encryption_key: str = os.getenv("TOKEN_ENCRYPTION_KEY", "n85xG8uSDZgsZ-JmgnAhMmNsNkp6dntE4NU-gIDiBr0=")
if not _encryption_key:
    # In production, always set TOKEN_ENCRYPTION_KEY in environment variables
    # This is a fallback for development only
    _encryption_key = Fernet.generate_key().decode()
    print("WARNING: Using temporary encryption key. Set TOKEN_ENCRYPTION_KEY in environment for persistence.")

_fernet = Fernet(_encryption_key.encode())

# Prefix for encrypted values
_ENCRYPTED_PREFIX = "ENCRYPTED:"


def encrypt_token(token: str) -> str:
    """
    Encrypts a token using Fernet symmetric encryption.
    Use this for tokens that need to be retrieved later in plaintext.

    Args:
        token: The plaintext token to encrypt.

    Returns:
        The encrypted token string with a prefix to indicate it's encrypted.
    """
    encrypted = _fernet.encrypt(token.encode()).decode()
    return f"{_ENCRYPTED_PREFIX}{encrypted}"


def decrypt_token(stored_token: str) -> str:
    """
    Decrypts a stored token to retrieve the original value.
    
    Args:
        stored_token: The token string from storage (should be encrypted).

    Returns:
        The original plaintext token.

    Raises:
        ValueError: If the token has an invalid format.
    """
    if stored_token.startswith(_ENCRYPTED_PREFIX):
        # This is an encrypted token that we can decrypt
        encrypted_part = stored_token[len(_ENCRYPTED_PREFIX):]
        return _fernet.decrypt(encrypted_part.encode()).decode()
    else:
        # Assume this is a plaintext token (not recommended in production)
        return stored_token