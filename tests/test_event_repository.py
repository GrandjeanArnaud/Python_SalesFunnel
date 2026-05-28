# pyrefly: ignore [missing-import]
import pytest
from datetime import datetime
from src.models import Contact, Sector
from src.models.event import Event, EventType
from src.repositories.event_repository import EventRepository


@pytest.fixture
def test_contact(db_session):
    """Fixture to persist a Sector and a Contact, needed for Event foreign key constraint."""
    sector = Sector(code="MKT", label="Marketing")
    db_session.add(sector)
    db_session.commit()
    
    contact = Contact(
        name="Test Contact",
        last_name="LastName",
        first_name="FirstName",
        email="test@example.com",
        sector_id=sector.id,
        interests={}
    )
    db_session.add(contact)
    db_session.commit()
    return contact


def test_new_event(db_session, test_contact):
    repo = EventRepository(db_session)
    
    now = datetime.now()
    event_type = EventType.EMAIL_SENT
    description = "Test email template name"
    
    event = repo.new_event(
        contact_id=test_contact.id,
        event_type=event_type,
        event_date=now,
        event_description=description
    )
    db_session.commit()
    
    assert event.id is not None
    assert event.contact_id == test_contact.id
    assert event.type == event_type
    assert event.date == now
    assert event.template == description
