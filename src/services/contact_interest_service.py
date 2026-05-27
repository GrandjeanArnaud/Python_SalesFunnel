import logging
from datetime import datetime

from fastapi.templating import Jinja2Templates

from src.dto.contact_interest_dto import ContactInterestDTO
from src.repositories.contact_repository import ContactRepository
from src.repositories.interest_repository import InterestRepository
from src.services.contact_service import increment_interest
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)

class ContactInterestService:
    """Application service orchestrating contact-interest workflows.

    Responsibilities:
    - Build interest DTOs for contacts
    - Orchestrate template rendering and email sending
    - Apply simple mutations to contact interests 

    Note: persistence commit/rollback is performed by controllers that open
    the database session and manage the unit-of-work.
    """

    def __init__(self, contact_repo : ContactRepository, interest_repo : InterestRepository ):
        self.contact_repo = contact_repo
        self.interest_repo = interest_repo

    def generer_dtos_interets_contacts(self) -> list[ContactInterestDTO]:
        """Generate a list of `ContactInterestDTO` for every contact with an email.

        Returns:
            List of `ContactInterestDTO` instances ready for rendering/sending.
        """
        values: list[ContactInterestDTO] = []
        
        contacts = self.contact_repo.get_all_contacts()
        
        for contact in contacts:
            if contact.email is not None:
                interests_du_secteur = self.interest_repo.get_interests_for_contact(contact.id)

                interets_tries, roots = self.interest_repo.get_prioritized_interests(
                    user_json=contact.interests,
                    interests_du_secteur=interests_du_secteur,
                )

                values.append(
                    ContactInterestDTO(
                        contact=contact,
                        interests_list=interets_tries,
                        roots=roots,
                    )
                )

        return values


    def send_batch_interest_emails(self, template_env: Jinja2Templates, resultat_dtos: list[ContactInterestDTO]) -> list[ContactInterestDTO]:
        """Render and send emails for the provided DTOs.

        Returns:
            A list of DTOs for which sending succeeded.
        """
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
        """Increment the contact's interest score for `interest_id`.

        This delegates the mutation logic to a pure helper and persists the
        change by adding the contact to the session. The controller should
        commit the transaction.
        """
        contact = self.contact_repo.get_contact(contact_id)
        interest_name = self.interest_repo.get_interest_from_id(interest_id).name

        increment_interest(contact, interest_name, increment=0.1)
        logging.getLogger(__name__).info("Updated interests for contact %s: %s", contact.id, contact.interests)

        self.contact_repo.save_contact(contact)


    def redirect_page_build(self, template_env: Jinja2Templates, interest: str) -> str:
        """Render a lightweight redirection HTML page for the provided interest.

        Args:
            template_env: Jinja environment container.
            interest: selected interest name to display in the redirection page.

        Returns:
            Rendered HTML as a string.
        """
        jinja_template = template_env.get_template('redirection_template.html')
        html_content = jinja_template.render(
            selected_interest = interest
        )

        return html_content
