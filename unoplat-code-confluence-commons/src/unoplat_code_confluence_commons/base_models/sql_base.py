"""SQLAlchemy 2.0 DeclarativeBase for all SQL models in unoplat-code-confluence."""

import enum

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase


class SQLBase(DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy 2.0 ORM models.
    
    This base class provides the foundation for all SQL table models
    in the unoplat-code-confluence project, enabling proper typing
    and modern SQLAlchemy 2.0 patterns with Mapped[T] and mapped_column.
    """
    
    type_annotation_map = {
        # Global enum configuration - automatically maps Python enums to SQLAlchemy Enum
        enum.Enum: sqlalchemy.Enum(enum.Enum),
    }