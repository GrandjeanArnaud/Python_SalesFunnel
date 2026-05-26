from __future__ import annotations
from src.models.db import Base
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

class Interest(Base):
    __tablename__ = 'interests'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    parent: Mapped[int] = mapped_column(nullable=True)

    def __eq__(self, other):
        if not isinstance(other, Interest):
            return NotImplemented
        return self.id == other.id

    # Define hashing: use the hash of the unique ID
    def __hash__(self):
        return hash(self.id)

    