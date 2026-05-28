# pyrefly: ignore [missing-import]
import pytest
from types import SimpleNamespace
from src.services.contact_service import increment_interest


def test_increment_interest_basic():
    # Simple object mimicking a Contact instance
    contact = SimpleNamespace(id=1, interests={"AI": 0.5})
    increment_interest(contact, "AI", 0.2)
    assert contact.interests["AI"] == pytest.approx(0.7)


def test_increment_interest_default_step():
    contact = SimpleNamespace(id=1, interests={"AI": 0.5})
    increment_interest(contact, "AI")
    assert contact.interests["AI"] == pytest.approx(0.6)


def test_increment_interest_missing_key():
    contact = SimpleNamespace(id=1, interests={})
    increment_interest(contact, "AI", 0.3)
    assert contact.interests["AI"] == pytest.approx(0.3)


def test_increment_interest_missing_dict():
    contact = SimpleNamespace(id=1, interests=None)
    increment_interest(contact, "AI", 0.4)
    assert isinstance(contact.interests, dict)
    assert contact.interests["AI"] == pytest.approx(0.4)


def test_increment_interest_clamping():
    contact = SimpleNamespace(id=1, interests={"AI": 0.95})
    increment_interest(contact, "AI", 0.1)
    assert contact.interests["AI"] == 1.0
