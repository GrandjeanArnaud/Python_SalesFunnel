from datetime import datetime

from sqlalchemy import select, union_all, literal, Integer
from sqlalchemy.orm import aliased, Session, joinedload
from src.models.event import Event, EventType
from src.models import Contact 


class EventRepository():
    """Repository for creating `Event` records.

    This repository only constructs and adds Events to the session; it does
    not commit the transaction. Callers should commit when the unit-of-work
    is complete.
    """
    __session: Session

    def __init__(self, session: Session):
        self.__session = session

    def new_event(self, contact_id: int, event_type: EventType, event_date: datetime, event_description: str) :
        """Create and add a new `Event` to the current session.

        Args:
            contact_id: id of the contact related to the event.
            event_type: an `EventType` enum value describing the event.
            event_date: datetime of the event.
            event_description: optional descriptive string.

        Returns:
            The created `Event` instance (attached to the session).
        """
        new_event = Event(contact_id, event_type, event_date, event_description)
        
        self.__session.add(new_event)
        return new_event
        
