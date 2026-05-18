
from __future__ import annotations
from models.database import Base
from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

import enum
from sqlalchemy import Enum as EnumSQL

class EventType(enum.Enum):
    EMAIL_SENT = "Email_sent"
    EMAIL_DELIVERED = "Email_delivered"
    EMAIL_OPENED = "Email_opened"
    EMAIL_UNSUBSCRIBED = "Email_unsubscribed"
    LINK_CLICKED = "Link_clicked"
    BUTTON_CLICKED = "Button_clicked"
    IMAGE_CLICKED = "Image_clicked"
    PRODUCT_CLICKED = "Product_clicked"
    CATALOG_CLICKED = "Catalog_clicked"
    SCORE_UPDATED = "Score_updated"
    SCORE_INCREASED = "Score_increased"
    SCORE_DECREASED = "Score_decreased"
    SCORE_THRESHOLD_REACHED = "Score_treshold_reached"

class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, init=False, unique=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'))
    type : Mapped[EventType] = mapped_column(EnumSQL(EventType)) 
    date: Mapped[Date] = mapped_column()
    template: Mapped[str] = mapped_column(nullable=True)