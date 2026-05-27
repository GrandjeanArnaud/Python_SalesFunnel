from fastapi import Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from src.models import Contact, Interest, interest, interest_sectors
from src.repositories.contact_repository import ContactRepository
from src.services.interest_scoring import (
    extract_interests,
    build_indexes,
    compute_propagated_scores,
    sort_and_filter_interests,
)
import logging


logger = logging.getLogger(__name__)


class InterestRepository():
    """Repository handling read access for `Interest` objects and helpers.

    The repository focuses on data retrieval. Business logic related to
    scoring/prioritization is delegated to the `src.services.scoring` module.
    """
    __session: Session

    def __init__(self, session: Session = Depends(Session)):
        self.__session = session

    def get_interest_from_id(self, id: int) -> Interest:
        """Return an `Interest` by its numeric `id` or `None` if missing."""
        interest = self.__session.query(Interest).filter(Interest.id == id).first()
        return interest
    
    def get_interest_from_name(self, name: str) -> Interest:
        """Return an `Interest` matching `name` or `None`."""
        interest = self.__session.query(Interest).filter(Interest.name == name).first()
        return interest

    def get_all_interests(self) -> list[Interest]:
        """Return all interests for administrative use."""
        interests = self.__session.query(Interest).all()
        return interests
    
    def get_interests_for_contact(self, contact_id: int) -> list[Interest]:
        """Return interests available for the sector of the given contact.

        This method looks up the contact to obtain its `sector_id` and then
        queries the `interest_sectors` association table.
        """
        contact_repository = ContactRepository(self.__session)
        contact = contact_repository.get_contact(contact_id)

        interests = (
            self.__session.query(Interest)
            .join(interest_sectors, Interest.id == interest_sectors.c.interest_id)
            .filter(interest_sectors.c.sector_id == contact.sector_id)
            .all()
        )
        return interests
    

    def get_prioritized_interests(self, user_json, interests_du_secteur):
        """Return a tuple of (`sorted_non_roots`, `roots`) based on the
        provided `user_json` scores and the list of interests for the sector.

        The heavy lifting (parsing, propagation and sorting) is delegated to
        `src.services.scoring` so the repository remains testable and focused
        on data retrieval.
        """
        user_interests_dict = extract_interests(user_json)
        by_name, _, children, roots = build_indexes(interests_du_secteur)

        result_scores = compute_propagated_scores(user_interests_dict, by_name, children)

        sorted_non_roots = sort_and_filter_interests(result_scores, by_name, roots)

        return sorted_non_roots, roots
