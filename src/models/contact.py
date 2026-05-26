from __future__ import annotations

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableDict

from src.models.db import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    last_name: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    sector_id: Mapped[int] = mapped_column(ForeignKey('sectors.id'))
    interests: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def company_and_full_name(self) -> str:
        return f"{self.name} - {self.full_name}"