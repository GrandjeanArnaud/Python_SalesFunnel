# pyrefly: ignore [missing-import]
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from src.main import app
from src.models import Contact, Sector, Interest
from src.models.db import Base, interest_sectors
from src.models.event import Event, EventType

# 1. Setup a single SQLite in-memory engine with StaticPool to keep connection alive
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Ensure tables are created on the test DB
Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Drop and recreate all tables to start with a fresh DB for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def mock_db_session(clean_db):
    """Patch the database Session creator to use our TestingSessionLocal."""
    with patch("src.models.db.Session", new=TestingSessionLocal):
        yield


@pytest.fixture(autouse=True)
def mock_email_service():
    """Prevent actual email sending during controller tests."""
    with patch("src.services.contact_interest_service.EmailService.send_template_email", return_value=True) as mock:
        yield mock


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


def test_interest_clicked_endpoint(client):
    # 1. Setup data in SQLite test DB
    session = TestingSessionLocal()
    sector = Sector(code="IT", label="IT")
    session.add(sector)
    session.commit()

    contact = Contact(
        name="Acme Inc",
        last_name="Doe",
        first_name="John",
        email="john@acme.com",
        sector_id=sector.id,
        interests={"Python": 0.5}
    )
    session.add(contact)

    interest = Interest(name="Python", parent=None)
    session.add(interest)
    session.commit()

    c_id = contact.id
    i_id = interest.id
    session.close()

    # 2. Call the endpoint
    response = client.get(f"/interest?contact_id={c_id}&interest_id={i_id}")

    # 3. Assertions
    assert response.status_code == 200
    assert "Python" in response.text  # HTML response containing the selected interest
    
    # 4. Verify DB state modifications
    session = TestingSessionLocal()
    
    # Check that contact interests score was updated
    updated_contact = session.get(Contact, c_id)
    assert updated_contact.interests["Python"] == pytest.approx(0.6)
    
    # Check that a LINK_CLICKED event was created
    event = session.query(Event).filter(Event.contact_id == c_id).first()
    assert event is not None
    assert event.type == EventType.LINK_CLICKED
    assert event.template == "Interests Email Template"
    
    session.close()


def test_workflow_send_to_all_endpoint(client):
    # 1. Setup data in SQLite test DB
    session = TestingSessionLocal()
    
    sector = Sector(code="IT", label="IT")
    session.add(sector)
    session.commit()

    c1 = Contact(
        name="Acme",
        last_name="Doe",
        first_name="John",
        email="john@acme.com",
        sector_id=sector.id,
        interests={"Python": 0.5}
    )
    session.add(c1)
    
    interest = Interest(name="Python", parent=None)
    session.add(interest)
    session.commit()
    
    # Associate Python to sector IT
    session.execute(interest_sectors.insert().values(interest_id=interest.id, sector_id=sector.id))
    session.commit()
    
    c1_id = c1.id
    session.close()

    # 2. Call endpoint
    # We need to mock the template environment or files. Because the real controller loads templates from
    # 'src/templates', which might exist in the workspace, we can run it. Let's make sure template rendering works.
    # In case the template files are not found, let's patch the redirection and email sending or jinja template rendering.
    # We can mock Jinja2Templates.get_template if we want, or rely on actual files. Since templates exist in 'src/templates', 
    # the actual templates will render, which is great.
    response = client.get("/workflow/send_to_all")

    # 3. Assertions
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["emails_sent"] == 1

    # 4. Verify DB state modifications
    session = TestingSessionLocal()
    
    # Check that an EMAIL_SENT event was created for the contact who received the email
    events = session.query(Event).filter(Event.contact_id == c1_id).all()
    assert len(events) == 1
    assert events[0].type == EventType.EMAIL_SENT
    assert events[0].template == "Interests Email Template"
    
    session.close()
