import os
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

# PostgreSQL connection settings - read from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "code_confluence")

# Construct PostgreSQL connection string
POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
# Read echo setting from environment variable, default to False
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
engine = create_engine(POSTGRES_URL, echo=DB_ECHO)


def get_session():
    """Yield a database session using a context manager."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_cm():
    """Context manager for database session (original logic)."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def create_db_and_tables():
    """Create database tables from SQLModel models."""
    SQLModel.metadata.create_all(engine) 