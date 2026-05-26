from dataclasses import dataclass

from src.models.contact import Contact
from src.models.interest import Interest

@dataclass
class ContactInterestDTO():
    contact: Contact
    interests_list: list[Interest]
    roots: list[Interest]






    