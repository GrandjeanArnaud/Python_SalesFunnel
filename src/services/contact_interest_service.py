from fastapi.templating import Jinja2Templates

from src.models.event import EventType
from src.repositories.event_repository import EventRepository
from src.services.email_service import EmailService
from src.repositories.contact_repository import ContactRepository
from src.repositories.interest_repository import InterestRepository
from src.dto.contact_interest_dto import ContactInterestDTO 
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ContactInterestService:
    def __init__(self, contact_repo : ContactRepository, interest_repo : InterestRepository ):
        # On injecte les repositories nécessaires
        self.contact_repo = contact_repo
        self.interest_repo = interest_repo

    def generer_dtos_interets_contacts(self) -> list[ContactInterestDTO]:
        values: list[ContactInterestDTO] = []
        
        contacts = self.contact_repo.get_all_contacts()
        
        for contact in contacts:
            if contact.email is not None: 
            
            # 1. On récupère d'un coup tous les intérêts reliés au secteur du contact
                interests_du_secteur = self.interest_repo.get_interests_for_contact(contact.id)
                
                # 2. On délègue le calcul l'extraction, du cumul et du tri au repository
                interets_tries, roots = self.interest_repo.get_prioritized_interests(
                    user_json=contact.interests,
                    interests_du_secteur=interests_du_secteur,
                )
                
                # 3. On ajoute le DTO avec la liste triée
                values.append(ContactInterestDTO(contact=contact, interests_list=interets_tries, roots = roots))

        return values


    def send_batch_interest_emails(self, template_env: Jinja2Templates, resultat_dtos: list[ContactInterestDTO]) -> list[ContactInterestDTO]:

        jinja_template = template_env.get_template('email_template.html')
        successful_dtos = []

        for dto in resultat_dtos :
            try:
                html_content = jinja_template.render(
                    contact=dto.contact,
                    interests=dto.interests_list,
                    roots = dto.roots
                )
                EmailService.send_template_email(
                    to_email=dto.contact.email,
                    subject="Votre sélection d'intérêts !",
                    html_content=html_content
                )

                successful_dtos.append(dto)
                        
            except Exception as e:
                logger.error(f"Échec de l'envoi d'email pour le contact {dto.contact.id}: {e}")
                continue

        return successful_dtos
    
    def update_contact_interests(self, contact_id: int, interest_id: int):
        contact = self.contact_repo.get_contact(contact_id)
        interest_name = self.interest_repo.get_interest_from_id(interest_id).name

        increment = 0.1

        if interest_name not in contact.interests:
            contact.interests[interest_name] = 0.0

        # Incrément
        contact.interests[interest_name] += increment

        # Remet à 1.0 si dépassement
        contact.interests[interest_name] = min(1.0, contact.interests[interest_name])

        print(f'Updated interests for contact {contact.id}: {contact.interests}')
    
        self.contact_repo.save_contact(contact)

    def redirect_page_build(self, template_env: Jinja2Templates, interest: str) -> str:

        jinja_template = template_env.get_template('redirection_template.html')
        html_content = jinja_template.render(
            selected_interest = interest
        )

        return html_content
