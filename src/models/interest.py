from __future__ import annotations
from src.models.db import Base
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

class Interest(Base):
    __tablename__ = 'interests'

    """Represents an interest node used for categorization and scoring.

    `parent` holds the id of the parent Interest or `None` for root nodes.
    """

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    parent: Mapped[int] = mapped_column(nullable=True)

    def __eq__(self, other):
        """Equality compares Interests by their primary key id."""
        if not isinstance(other, Interest):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        """Hash based on the unique primary key id to allow set membership."""
        return hash(self.id)

    