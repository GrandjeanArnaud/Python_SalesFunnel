from __future__ import annotations
from models.database import Base
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

class Interest(Base):
    __tablename__ = 'interests'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    parent: Mapped[str] = mapped_column()

    