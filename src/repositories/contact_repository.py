import code

from sqlalchemy import select, union_all, literal, Integer
from sqlalchemy.orm import aliased, Session, joinedload
from src.models import Contact 


class ContactRepository():
    """Repository for `Contact` model: provides simple data access helpers.

    This repository is intentionally thin: it adds and queries ORM objects
    but does not manage transactions (commit/rollback). Transaction
    boundaries must be handled by the caller (service or controller).
    """
    __session: Session

    def __init__(self, session: Session):
        self.__session = session

    def get_contact(self, contact_id: int) -> Contact:
        """Return the `Contact` with id `contact_id` or `None`.

        Args:
            contact_id: primary key of the contact to fetch.

        Returns:
            The `Contact` instance or `None` if not found.
        """
        contact = self.__session.query(Contact).where(Contact.id == contact_id).first()
        return contact
    
    def get_all_contacts(self) -> list[Contact]:
        """Return all `Contact` rows as a list.

        Returns:
            List of `Contact` instances.
        """
        contacts = self.__session.query(Contact).all()
        return contacts
    
    def save_contact(self, contact: Contact):
        """Persist the `contact` into the current session.

        This method adds the instance to the SQLAlchemy session but does not
        commit. The caller should commit or rollback as appropriate.

        Args:
            contact: `Contact` instance to persist.

        Returns:
            The same `contact` instance (now attached to the session).
        """
        self.__session.add(contact)
        return contact

                
       