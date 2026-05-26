from datetime import datetime

from sqlalchemy import select, union_all, literal, Integer
from sqlalchemy.orm import aliased, Session, joinedload
from src.models.event import Event, EventType
from src.models import Contact 


class EventRepository():
    __session: Session

    def __init__(self, session: Session):
        self.__session = session

    def new_event(self, contact_id: int, event_type: EventType, event_date: datetime, event_description: str) :
        new_event = Event(contact_id, event_type, event_date, event_description)
        self.__session.add(new_event)
        self.__session.commit()
        self.__session.refresh(new_event)
        
