"""Helpers to mutate `Contact` domain objects in a predictable way.

These helpers are pure (no DB interaction) and designed to be unit tested.
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)


def increment_interest(contact: Any, interest_name: str, increment: float = 0.1) -> None:
    """Increment (and clamp) an interest score on a contact.

    Args:
        contact: the `Contact` instance with an `interests` mapping.
        interest_name: key for the interest to increment.
        increment: step to add to the existing score (default 0.1).

    The function ensures `contact.interests` is a dict and clamps the value
    to `1.0` after incrementing.
    """
    if not isinstance(contact.interests, dict):
        contact.interests = {}

    contact.interests.setdefault(interest_name, 0.0)

    contact.interests[interest_name] = min(1.0, contact.interests[interest_name] + increment)
    logger.debug(
        "Contact %s interest '%s' updated to %s",
        getattr(contact, "id", None),
        interest_name,
        contact.interests[interest_name],
    )
