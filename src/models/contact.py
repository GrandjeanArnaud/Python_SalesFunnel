from __future__ import annotations

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableDict

from src.models.db import Base

class Contact(Base):
    __tablename__ = 'contacts'

    """Model representing a contact (person/company).

    The `interests` column stores a mapping from interest name to a floating
    score between 0.0 and 1.0. It is a mutable JSON column so in-place updates
    are tracked by SQLAlchemy.
    """

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    last_name: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    sector_id: Mapped[int] = mapped_column(ForeignKey('sectors.id'))
    interests: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        default_factory=dict
    )

    @property
    def full_name(self) -> str:
        """Return the `first_name` and `last_name` combined as a single string."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def company_and_full_name(self) -> str:
        """Return a combined display string including company and the contact's full name."""
        return f"{self.name} - {self.full_name}"