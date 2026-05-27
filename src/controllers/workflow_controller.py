from datetime import datetime
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from src.repositories.event_repository import EventRepository
from src.services.contact_interest_service import ContactInterestService
from src.repositories.contact_repository import ContactRepository
from src.repositories.interest_repository import InterestRepository
from src.models.db import transactional_session
from src.models.event import Event, EventType


workflow_router = APIRouter(prefix="/workflow")

template = Jinja2Templates(directory='src/templates')

@workflow_router.get('/send_to_all')
def workflow_clicked():
    """Trigger the batch email workflow.

    For each contact this builds interest DTOs, renders and sends emails,
    and records result events. All DB mutations are committed once inside
    the reusable transactional scope.
    """

    with transactional_session() as session:
        service = ContactInterestService(ContactRepository(session), InterestRepository(session))
        resultat_dtos = service.generer_dtos_interets_contacts()

        contacts_vises = service.send_batch_interest_emails(template, resultat_dtos)

        event_repo = EventRepository(session)
        if contacts_vises:
            for dto in contacts_vises:
                event_repo.new_event(
                    dto.contact.id,
                    EventType.EMAIL_SENT,
                    datetime.now(),
                    "Interests Email Template",
                )

    return {
        "status": "success",
        "emails_sent": len(contacts_vises),
    }
