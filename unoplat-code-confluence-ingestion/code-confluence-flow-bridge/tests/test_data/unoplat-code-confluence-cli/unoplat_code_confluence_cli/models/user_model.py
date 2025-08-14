"""Sample dataclass for testing data model detection."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User data model."""
    name: str
    email: str
    age: int
    is_active: bool = True


@dataclass
class UserProfile:
    """User profile with additional details."""
    user: User
    bio: Optional[str] = None
    followers: int = 0