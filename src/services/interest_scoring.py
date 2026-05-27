"""Scoring helpers for contact interests.

This module provides pure functions to parse stored interest data, build
indexes from `Interest` objects, compute propagated scores (parent ->
children and siblings) and sort/filter results for presentation.
"""

from typing import Dict, List, Tuple
from collections import defaultdict
import json
import logging

from src.models.interest import Interest

logger = logging.getLogger(__name__)


def extract_interests(user_json) -> Dict[str, float]:
    """Safely extract a mapping of interest name -> score from stored data.

    The stored representation may be a JSON string or a dict. This helper
    normalizes both into a `dict[str, float]` suitable for downstream
    computations; malformed input yields an empty dict.
    """
    if not user_json:
        return {}
    if isinstance(user_json, str):
        try:
            return json.loads(user_json)
        except json.JSONDecodeError:
            return {}
    if isinstance(user_json, dict):
        return dict(user_json)
    return {}


def build_indexes(interests: List[Interest]) -> Tuple[dict, dict, dict, list]:
    """Build in-memory indexes from a list of `Interest` objects.

    Returns a tuple `(by_name, by_id, children, roots)` where `by_name` maps
    interest name to object, `by_id` maps id to object, `children` maps a
    parent id to a list of child `Interest` objects and `roots` is the list
    of top-level interests.
    """
    by_name: dict[str, Interest] = {}
    by_id: dict[int, Interest] = {}
    children: dict[int, list[Interest]] = defaultdict(list)
    roots: list[Interest] = []

    for item in interests:
        by_name[item.name] = item
        by_id[item.id] = item
        if item.parent is not None:
            children[item.parent].append(item)
        else:
            roots.append(item)

    return by_name, by_id, children, roots


def compute_propagated_scores(
    user_interests_dict: Dict[str, float],
    by_name: dict[str, Interest],
    children: dict[int, list[Interest]],
) -> Dict[str, float]:
    """Compute base + propagated scores (parent -> children and siblings).

    Scoring rules:
    - Explicit scores from `user_interests_dict` are preserved.
    - Parents propagate 50% of their score to children, capped at 0.2.
    - Siblings receive 20% of the score, capped at 0.1.
    - Final scores are clamped to 1.0.

    The function is pure and side-effect free to allow simple unit testing.
    """
    result_scores: Dict[str, float] = {}

    # Scores de la DB
    for name, score in user_interests_dict.items():
        if name in by_name:
            result_scores[name] = score

    # Ajout de bonus des parents et des frères pour mettre en avant les enfants (en haut dans le mail)
    for name, score in user_interests_dict.items():
        if name not in by_name:
            continue

        node = by_name[name]

        # Parent : 50% du score parent, avec un maximum à 0.2)
        for c in children.get(node.id, []):
            bonus_parent = min(score * 0.5, 0.2)
            result_scores[c.name] = result_scores.get(c.name, 0.0) + bonus_parent

        # Siblings : 20% du score, avec un maximum à 0.1)
        if node.parent is not None:
            for s in children.get(node.parent, []):
                if s.id != node.id:
                    bonus_sibling = min(score * 0.2, 0.1)
                    result_scores[s.name] = result_scores.get(s.name, 0.0) + bonus_sibling

    # Remise à 1.0 si supérieur
    for key in list(result_scores.keys()):
        result_scores[key] = min(result_scores[key], 1.0)

    logger.debug("Computed propagated scores: %s", result_scores)
    return result_scores


def sort_and_filter_interests(
    result_scores: Dict[str, float],
    by_name: dict[str, Interest],
    roots: List[Interest],
) -> List[Interest]:
    """Return Interest objects (non-root) sorted by score desc then name.

    Roots are excluded from the returned list because they represent grouping
    nodes rather than selectable leaf interests.
    """
    root_names = {r.name for r in roots}

    matched_interest_objects = [
        by_name[name] for name in result_scores.keys() if name not in root_names
    ]

    return sorted(
        matched_interest_objects, key=lambda interest: (-result_scores[interest.name], interest.name)
    )
