from __future__ import annotations
from models.database import Base
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

class Sector(Base):
    __tablename__ = 'sectors'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    label: Mapped[str] = mapped_column(nullable=False)

