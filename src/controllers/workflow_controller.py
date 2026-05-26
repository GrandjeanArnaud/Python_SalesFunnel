from datetime import datetime
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from src.repositories.event_repository import EventRepository
from src.services.contact_interest_service import ContactInterestService
from src.dto.contact_interest_dto import ContactInterestDTO
from src.services.email_service import EmailService
from src.repositories.contact_repository import ContactRepository
from src.repositories.interest_repository import InterestRepository
from src.models.db import Session
from src.models.event import Event, EventType


workflow_router = APIRouter(prefix="/workflow")

template = Jinja2Templates(directory='src/templates')

@workflow_router.get('/send_to_all')
def workflow_clicked():
    
    with Session() as session:
        service = ContactInterestService(ContactRepository(session), InterestRepository(session))
        resultat_dtos = service.generer_dtos_interets_contacts()

        contacts_vises = service.send_batch_interest_emails(template, resultat_dtos)

        event_repo = EventRepository(session)
        if contacts_vises is not None:
            for dto in contacts_vises:
                event_repo.new_event(
                    dto.contact.id, 
                    EventType.EMAIL_SENT, 
                    datetime.now(), 
                    "Interests Email Template"
                )
        