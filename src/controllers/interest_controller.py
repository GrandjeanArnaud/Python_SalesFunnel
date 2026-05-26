from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from requests import session
from src.services.contact_interest_service import ContactInterestService
from src.repositories.contact_repository import ContactRepository
from src.repositories.interest_repository import InterestRepository
from src.repositories.event_repository import EventRepository
from src.models.db import Session
from src.models.event import Event, EventType


interest_router = APIRouter(prefix="/interest")

template = Jinja2Templates(directory='src/templates')

@interest_router.get('')
def interest_clicked(contact_id: int, interest_id: int):
    with Session() as session:
        #Sauvegarde de l'événement de clic dans la base de données
        EventRepository(session).new_event(
            contact_id, 
            EventType.LINK_CLICKED, 
            datetime.now(), 
            "Interests Email Template"
        )

        #Adaptation des intérêts du contact
        int_repo = InterestRepository(session)
        service = ContactInterestService(ContactRepository(session), int_repo)
        service.update_contact_interests(contact_id, interest_id)

        #Redirection vers e-commerce (page html en dev/demo)
        selected_interest = int_repo.get_interest_from_id(interest_id)
        html_content = service.redirect_page_build(template, selected_interest.name)
        return HTMLResponse(content=html_content)

