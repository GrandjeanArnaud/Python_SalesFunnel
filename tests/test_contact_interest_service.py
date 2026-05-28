# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import MagicMock, patch
from src.models import Contact, Sector, Interest
from src.models.db import interest_sectors
from src.repositories.contact_repository import ContactRepository
from src.repositories.interest_repository import InterestRepository
from src.services.contact_interest_service import ContactInterestService


@pytest.fixture
def service_setup(db_session):
    contact_repo = ContactRepository(db_session)
    interest_repo = InterestRepository(db_session)
    service = ContactInterestService(contact_repo, interest_repo)
    return service, contact_repo, interest_repo


def test_generer_dtos_interets_contacts():
    # Mock repositories
    contact_repo = MagicMock()
    interest_repo = MagicMock()
    
    # Create transient contacts (not persisted to DB, avoiding email NOT NULL constraint)
    c1 = MagicMock()
    c1.id = 1
    c1.email = "john@acme.com"
    c1.interests = {"Python": 0.8}
    
    c2 = MagicMock()
    c2.id = 2
    c2.email = None
    c2.interests = {"Python": 0.8}
    
    contact_repo.get_all_contacts.return_value = [c1, c2]
    
    # Mock interest repo returns
    interests_du_secteur = [MagicMock()]
    interest_repo.get_interests_for_contact.return_value = interests_du_secteur
    
    interets_tries = [MagicMock()]
    roots = [MagicMock()]
    interest_repo.get_prioritized_interests.return_value = (interets_tries, roots)
    
    # Run service
    service = ContactInterestService(contact_repo, interest_repo)
    dtos = service.generer_dtos_interets_contacts()
    
    # Assertions: only c1 (who has email) should have a DTO
    assert len(dtos) == 1
    dto = dtos[0]
    assert dto.contact == c1
    assert dto.interests_list == interets_tries


def test_send_batch_interest_emails(service_setup):
    service, _, _ = service_setup
    
    # Setup mock template environment
    template_env = MagicMock()
    mock_template = MagicMock()
    template_env.get_template.return_value = mock_template
    mock_template.render.return_value = "<html>Test Render</html>"
    
    # Setup DTOs
    dto1 = MagicMock()
    dto1.contact.email = "john@example.com"
    dto1.contact.id = 1
    dto1.interests_list = []
    dto1.roots = []
    
    dto2 = MagicMock()
    dto2.contact.email = "jane@example.com"
    dto2.contact.id = 2
    dto2.interests_list = []
    dto2.roots = []
    
    dtos = [dto1, dto2]
    
    with patch("src.services.contact_interest_service.EmailService.send_template_email") as mock_send:
        # Mock successful send for dto1, and exception/failure for dto2
        def side_effect(to_email, subject, html_content):
            if to_email == "jane@example.com":
                raise Exception("SMTP error")
            return True
        mock_send.side_effect = side_effect
        
        successful = service.send_batch_interest_emails(template_env, dtos)
        
        assert len(successful) == 1
        assert successful[0] == dto1
        
        assert mock_template.render.call_count == 2
        mock_send.assert_any_call(to_email="john@example.com", subject="Votre sélection d'intérêts !", html_content="<html>Test Render</html>")


def test_update_contact_interests(db_session, service_setup):
    service, contact_repo, interest_repo = service_setup
    
    # Setup database records
    sector = Sector(code="IT", label="IT")
    db_session.add(sector)
    db_session.commit()
    
    contact = Contact(
        name="Acme",
        last_name="Doe",
        first_name="John",
        email="john@acme.com",
        sector_id=sector.id,
        interests={"Python": 0.5}
    )
    db_session.add(contact)
    
    interest = Interest(name="Python", parent=None)
    db_session.add(interest)
    db_session.commit()
    
    # Run update
    service.update_contact_interests(contact.id, interest.id)
    db_session.commit()
    
    # Verify persistence
    updated_contact = contact_repo.get_contact(contact.id)
    assert updated_contact.interests["Python"] == pytest.approx(0.6)


def test_redirect_page_build(service_setup):
    service, _, _ = service_setup
    
    template_env = MagicMock()
    mock_template = MagicMock()
    template_env.get_template.return_value = mock_template
    mock_template.render.return_value = "<html>Redirection to Python</html>"
    
    html = service.redirect_page_build(template_env, "Python")
    assert html == "<html>Redirection to Python</html>"
    template_env.get_template.assert_called_once_with("redirection_template.html")
    mock_template.render.assert_called_once_with(selected_interest="Python")
