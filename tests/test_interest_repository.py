# pyrefly: ignore [missing-import]
import pytest
from src.models import Contact, Sector, Interest
from src.models.db import interest_sectors
from src.repositories.interest_repository import InterestRepository


def test_get_interest_from_id(db_session):
    repo = InterestRepository(db_session)
    
    interest = Interest(name="AI", parent=None)
    db_session.add(interest)
    db_session.commit()
    
    fetched = repo.get_interest_from_id(interest.id)
    assert fetched is not None
    assert fetched.id == interest.id
    assert fetched.name == "AI"


def test_get_interest_from_name(db_session):
    repo = InterestRepository(db_session)
    
    interest = Interest(name="Machine Learning", parent=None)
    db_session.add(interest)
    db_session.commit()
    
    fetched = repo.get_interest_from_name("Machine Learning")
    assert fetched is not None
    assert fetched.id == interest.id
    
    assert repo.get_interest_from_name("NonExistent") is None


def test_get_all_interests(db_session):
    repo = InterestRepository(db_session)
    
    i1 = Interest(name="Python", parent=None)
    i2 = Interest(name="React", parent=None)
    db_session.add(i1)
    db_session.add(i2)
    db_session.commit()
    
    interests = repo.get_all_interests()
    assert len(interests) == 2
    assert {i.name for i in interests} == {"Python", "React"}


def test_get_interests_for_contact(db_session):
    repo = InterestRepository(db_session)
    
    # 1. Create a sector
    sector = Sector(code="DEV", label="Development")
    db_session.add(sector)
    db_session.commit()
    
    # 2. Create a contact in that sector
    contact = Contact(
        name="Developer Contact",
        last_name="Coder",
        first_name="Alice",
        email="alice@dev.com",
        sector_id=sector.id,
        interests={}
    )
    db_session.add(contact)
    db_session.commit()
    
    # 3. Create interests
    i1 = Interest(name="Python", parent=None)
    i2 = Interest(name="Docker", parent=None)
    i3 = Interest(name="Cooking", parent=None) # Not associated to sector
    db_session.add_all([i1, i2, i3])
    db_session.commit()
    
    # 4. Associate i1 and i2 to sector DEV
    db_session.execute(interest_sectors.insert().values(interest_id=i1.id, sector_id=sector.id))
    db_session.execute(interest_sectors.insert().values(interest_id=i2.id, sector_id=sector.id))
    db_session.commit()
    
    # 5. Fetch interests for contact
    fetched_interests = repo.get_interests_for_contact(contact.id)
    assert len(fetched_interests) == 2
    assert i1 in fetched_interests
    assert i2 in fetched_interests
    assert i3 not in fetched_interests


def test_get_prioritized_interests(db_session):
    repo = InterestRepository(db_session)
    
    # Setup interests
    root = Interest(name="Tech", parent=None)
    root.id = 1
    child1 = Interest(name="Python", parent=1)
    child1.id = 2
    child2 = Interest(name="Javascript", parent=1)
    child2.id = 3
    
    interests_secteur = [root, child1, child2]
    
    # User interests JSON has "Tech" score 0.5
    user_json = {"Tech": 0.5}
    
    sorted_non_roots, roots = repo.get_prioritized_interests(user_json, interests_secteur)
    
    # Roots should only contain Tech
    assert len(roots) == 1
    assert roots[0] == root
    
    # non-roots should contain Python and Javascript (score 0.5 * 0.5 = 0.25 due to propagation)
    assert len(sorted_non_roots) == 2
    assert child2 in sorted_non_roots  # Javascript
    assert child1 in sorted_non_roots  # Python
