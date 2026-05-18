from __future__ import annotations
from models.database import Base
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

class Contact(Base):
    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    last_name: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    interests: Mapped[JSON] = mapped_column(type_=JSON)
    
    sector: Mapped[int] = mapped_column()