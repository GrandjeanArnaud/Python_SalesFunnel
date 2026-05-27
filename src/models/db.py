import os

"""Database helpers: base class, engine and session factory.

This module centralizes SQLAlchemy configuration. Callers should obtain a
session via `Session()` and manage the session lifecycle (commit/rollback)
in the application layer.
"""

from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Table, create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker

load_dotenv()


class Base(DeclarativeBase, MappedAsDataclass):
    """Declarative base used by all ORM models in the project."""
    pass


engine = create_engine(os.getenv('DB_URL'), echo=True)

interest_sectors = Table(
    "interest_sectors",
    Base.metadata,
    Column("interest_id", ForeignKey("interests.id")),
    Column("sector_id", ForeignKey("sectors.id"))
)


def Session():
    """Return a new SQLAlchemy `Session` instance from the configured engine.

    The caller is responsible for closing/committing/rolling back the
    returned session.
    """
    return sessionmaker(bind=engine)()


@contextmanager
def transactional_session():
    """Provide a transactional scope for SQLAlchemy session usage.

    The helper commits if the block completes successfully, rolls back on
    exception, and always closes the session.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
