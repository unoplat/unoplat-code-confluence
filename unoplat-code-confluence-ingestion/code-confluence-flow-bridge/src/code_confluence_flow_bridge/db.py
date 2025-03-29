import os

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
engine = create_engine(POSTGRES_URL, echo=True)

def get_session():
    """
    Create and yield a database session.
    
    Returns:
        Session: SQLModel session object
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """Create database tables from SQLModel models."""
    SQLModel.metadata.create_all(engine) 