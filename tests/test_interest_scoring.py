# pyrefly: ignore [missing-import]
import pytest
from src.models.interest import Interest
from src.services.interest_scoring import (
    extract_interests,
    build_indexes,
    compute_propagated_scores,
    sort_and_filter_interests,
)


def test_extract_interests_none():
    assert extract_interests(None) == {}


def test_extract_interests_dict():
    input_dict = {"AI": 0.8, "Web": 0.5}
    assert extract_interests(input_dict) == input_dict


def test_extract_interests_valid_json_string():
    input_str = '{"AI": 0.8, "Web": 0.5}'
    assert extract_interests(input_str) == {"AI": 0.8, "Web": 0.5}


def test_extract_interests_invalid_json_string():
    input_str = '{"AI": 0.8,'
    assert extract_interests(input_str) == {}


def test_extract_interests_invalid_type():
    assert extract_interests([1, 2, 3]) == {}


def test_build_indexes():
    # Setup test interests
    root = Interest(name="Technology", parent=None)
    root.id = 1
    
    child1 = Interest(name="Python", parent=1)
    child1.id = 2
    
    child2 = Interest(name="Javascript", parent=1)
    child2.id = 3
    
    other_root = Interest(name="Marketing", parent=None)
    other_root.id = 4
    
    interests = [root, child1, child2, other_root]
    
    by_name, by_id, children, roots = build_indexes(interests)
    
    # Assertions
    assert len(by_name) == 4
    assert by_name["Python"] == child1
    assert by_id[4] == other_root
    assert len(roots) == 2
    assert root in roots
    assert other_root in roots
    assert len(children[1]) == 2
    assert child1 in children[1]
    assert child2 in children[1]


def test_compute_propagated_scores():
    # Setup hierarchy: Root (1) -> Child1 (2), Child2 (3)
    root = Interest(name="Tech", parent=None)
    root.id = 1
    child1 = Interest(name="Python", parent=1)
    child1.id = 2
    child2 = Interest(name="Javascript", parent=1)
    child2.id = 3
    
    interests = [root, child1, child2]
    by_name, by_id, children, roots = build_indexes(interests)
    
    # Test case 1: Propagation from parent to children (50% bonus, capped at 0.2)
    user_scores_1 = {"Tech": 0.3}
    res_1 = compute_propagated_scores(user_scores_1, by_name, children)
    assert res_1["Tech"] == 0.3
    # 0.3 * 0.5 = 0.15 (under 0.2 cap)
    assert res_1["Python"] == pytest.approx(0.15)
    assert res_1["Javascript"] == pytest.approx(0.15)
    
    # Test case 2: Parent propagation capped at 0.2
    user_scores_2 = {"Tech": 0.6}
    res_2 = compute_propagated_scores(user_scores_2, by_name, children)
    assert res_2["Tech"] == 0.6
    # 0.6 * 0.5 = 0.3 (capped at 0.2)
    assert res_2["Python"] == pytest.approx(0.2)
    
    # Test case 3: Sibling propagation (20% score, capped at 0.1)
    user_scores_3 = {"Python": 0.4}
    res_3 = compute_propagated_scores(user_scores_3, by_name, children)
    assert res_3["Python"] == 0.4
    # Sibling of Python is Javascript. Sibling bonus: 0.4 * 0.2 = 0.08 (under 0.1 cap)
    assert res_3["Javascript"] == pytest.approx(0.08)
    assert "Tech" not in res_3  # Parents do not receive sibling/child bonus
    
    # Test case 4: Clamping to 1.0
    user_scores_4 = {"Python": 1.2}
    res_4 = compute_propagated_scores(user_scores_4, by_name, children)
    assert res_4["Python"] == 1.0


def test_sort_and_filter_interests():
    # Setup hierarchy
    root = Interest(name="Tech", parent=None)
    root.id = 1
    child1 = Interest(name="Python", parent=1)
    child1.id = 2
    child2 = Interest(name="Javascript", parent=1)
    child2.id = 3
    
    interests = [root, child1, child2]
    by_name, by_id, children, roots = build_indexes(interests)
    
    # Score Javascript high, Python lower, and root Tech is also present
    result_scores = {
        "Tech": 0.9,
        "Python": 0.4,
        "Javascript": 0.7
    }
    
    sorted_interests = sort_and_filter_interests(result_scores, by_name, roots)
    
    # Roots must be excluded ("Tech")
    # Remaining sorted by score desc, so "Javascript" (0.7) then "Python" (0.4)
    assert len(sorted_interests) == 2
    assert sorted_interests[0] == child2
    assert sorted_interests[1] == child1
    
    # Test sorting by name if scores are equal
    result_scores_equal = {
        "Python": 0.5,
        "Javascript": 0.5
    }
    sorted_equal = sort_and_filter_interests(result_scores_equal, by_name, roots)
    # Sorted alphabetically: "Javascript" before "Python"
    assert sorted_equal[0] == child2
    assert sorted_equal[1] == child1
