# pyrefly: ignore [missing-import]
import pytest
from src.models import Contact, Sector
from src.repositories.contact_repository import ContactRepository


@pytest.fixture
def test_sector(db_session):
    """Fixture to persist a Sector, needed for foreign key constraints in Contact."""
    sector = Sector(code="IT", label="Information Technology")
    db_session.add(sector)
    db_session.commit()
    return sector


def test_save_contact(db_session, test_sector):
    repo = ContactRepository(db_session)
    
    contact = Contact(
        name="Acme Inc",
        last_name="Doe",
        first_name="John",
        email="john.doe@acme.com",
        sector_id=test_sector.id,
        interests={"AI": 0.8}
    )
    
    saved_contact = repo.save_contact(contact)
    db_session.commit()
    
    assert saved_contact.id is not None
    assert saved_contact.name == "Acme Inc"
    assert saved_contact.email == "john.doe@acme.com"
    assert saved_contact.full_name == "John Doe"
    assert saved_contact.company_and_full_name == "Acme Inc - John Doe"


def test_get_contact_exists(db_session, test_sector):
    repo = ContactRepository(db_session)
    
    contact = Contact(
        name="Acme Inc",
        last_name="Doe",
        first_name="John",
        email="john.doe@acme.com",
        sector_id=test_sector.id,
        interests={}
    )
    db_session.add(contact)
    db_session.commit()
    
    fetched = repo.get_contact(contact.id)
    assert fetched is not None
    assert fetched.id == contact.id
    assert fetched.first_name == "John"


def test_get_contact_not_found(db_session):
    repo = ContactRepository(db_session)
    fetched = repo.get_contact(9999)
    assert fetched is None


def test_get_all_contacts(db_session, test_sector):
    repo = ContactRepository(db_session)
    
    contact1 = Contact(
        name="Company A",
        last_name="Doe",
        first_name="John",
        email="john.doe@a.com",
        sector_id=test_sector.id,
        interests={}
    )
    contact2 = Contact(
        name="Company B",
        last_name="Smith",
        first_name="Jane",
        email="jane.smith@b.com",
        sector_id=test_sector.id,
        interests={}
    )
    db_session.add(contact1)
    db_session.add(contact2)
    db_session.commit()
    
    contacts = repo.get_all_contacts()
    assert len(contacts) == 2
    assert {c.email for c in contacts} == {"john.doe@a.com", "jane.smith@b.com"}
