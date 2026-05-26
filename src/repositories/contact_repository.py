import code

from sqlalchemy import select, union_all, literal, Integer
from sqlalchemy.orm import aliased, Session, joinedload
from src.models import Contact 


class ContactRepository():
    __session: Session

    def __init__(self, session: Session):
        self.__session = session

    def get_contact(self, contact_id: int) -> Contact:
        contact = self.__session.query(Contact).where(Contact.id == contact_id).first()
        return contact
    
    def get_all_contacts(self) -> list[Contact]:
        contacts = self.__session.query(Contact).all()
        return contacts
    
    def save_contact(self, contact: Contact):
        self.__session.commit()
        self.__session.refresh(contact)

                
       