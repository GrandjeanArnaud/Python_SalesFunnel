# pyrefly: ignore [missing-import]
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from src.models.db import Base
# Explicitly import src.models to trigger package walk and register all models on Base.metadata
import src.models


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce foreign key constraints in SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory SQLite database session for each test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create all tables defined in the metadata
    Base.metadata.create_all(engine)
    
    # Bind session factory to our memory engine
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
