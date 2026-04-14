"""
User Deduplication
==================
Source: Stripe phone screen (linkjob.ai, 2025-2026)

Problem:
Given user records with fields {id, name, email, company}, identify duplicate users.

Part 1: Two users are "similar" if their weighted similarity score exceeds a threshold.
  - Weights: name=0.3, email=0.5, company=0.2
  - Field similarity: 1.0 if exact match, 0.0 otherwise
  - Score = sum(weight * similarity for each field)
  - Return all pairs of user IDs where score >= threshold.

Part 2: Find 1-hop linked groups.
  - If A matches B and B matches C, return {A, B, C} as one group.
  - But only follow 1 hop: if A-B match and B-C match, A and C are in the same
    group even if A-C don't directly match.

Part 3: Find full connected components (unlimited hops).
  - Use Union-Find to group all transitively connected users.

Complexity targets:
- Part 1: O(N^2) comparisons (unavoidable for pairwise)
- Part 3: O(N^2 * alpha(N)) with union-find, near-linear per operation
"""

from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str
    email: str
    company: str


def find_similar_pairs(
    users: list[User], threshold: float
) -> list[tuple[str, str]]:
    """
    Part 1: Find all pairs of users with similarity score >= threshold.

    Returns list of (user_id_1, user_id_2) tuples, with id_1 < id_2.
    """
    # TODO: Implement
    pass


def find_linked_groups_one_hop(
    users: list[User], threshold: float
) -> list[set[str]]:
    """
    Part 2: Find groups of users connected within 1 hop.

    Returns list of sets, each containing connected user IDs.
    Singletons (users with no matches) are excluded.
    """
    # TODO: Implement
    pass


def find_connected_components(
    users: list[User], threshold: float
) -> list[set[str]]:
    """
    Part 3: Find full connected components using Union-Find.

    Returns list of sets, each containing user IDs in one component.
    Singletons (users with no matches) are excluded.
    """
    # TODO: Implement Union-Find
    pass


# HINT 1: For similarity score, compare each field separately.
#         weighted_score = 0.3*(name match) + 0.5*(email match) + 0.2*(company match)

# HINT 2: For 1-hop groups, build an adjacency list from pairs,
#         then for each node, collect its neighbors + neighbors' neighbors.

# HINT 3: For Union-Find, implement find() with path compression
#         and union() with rank. Process all similar pairs.


# ============ TESTS ============

def test_similar_pairs():
    users = [
        User("1", "Alice", "alice@stripe.com", "Stripe"),
        User("2", "Alice", "alice@gmail.com", "Stripe"),  # name + company match
        User("3", "Bob", "bob@stripe.com", "Stripe"),     # only company matches
        User("4", "Alice", "alice@stripe.com", "Google"),  # name + email match
    ]
    # 1-2: name(0.3) + company(0.2) = 0.5
    # 1-3: company(0.2) = 0.2
    # 1-4: name(0.3) + email(0.5) = 0.8
    # 2-3: company(0.2) = 0.2
    # 2-4: name(0.3) = 0.3
    # 3-4: none = 0.0
    pairs = find_similar_pairs(users, threshold=0.5)
    assert ("1", "2") in pairs
    assert ("1", "4") in pairs
    assert len(pairs) == 2

def test_no_matches():
    users = [
        User("1", "Alice", "alice@a.com", "CompA"),
        User("2", "Bob", "bob@b.com", "CompB"),
    ]
    assert find_similar_pairs(users, threshold=0.5) == []

def test_one_hop_groups():
    users = [
        User("1", "Alice", "alice@stripe.com", "Stripe"),
        User("2", "Alice", "alice@gmail.com", "Stripe"),
        User("3", "Bob", "alice@gmail.com", "Google"),  # matches 2 via email
    ]
    # 1-2 match (name + company = 0.5), 2-3 match (email = 0.5)
    groups = find_linked_groups_one_hop(users, threshold=0.5)
    assert len(groups) == 1
    assert groups[0] == {"1", "2", "3"}

def test_connected_components():
    users = [
        User("1", "Alice", "a@x.com", "Stripe"),
        User("2", "Alice", "b@x.com", "Stripe"),  # matches 1 (name+company=0.5)
        User("3", "Bob", "c@x.com", "Stripe"),     # doesn't match 1 or 2
        User("4", "Bob", "c@x.com", "Google"),      # matches 3 (name+email=0.8)
    ]
    # Components: {1,2} and {3,4}
    components = find_connected_components(users, threshold=0.5)
    assert len(components) == 2
    ids = [sorted(c) for c in components]
    ids.sort()
    assert ids == [["1", "2"], ["3", "4"]]

def test_single_component():
    users = [
        User("1", "Alice", "alice@stripe.com", "Stripe"),
        User("2", "Alice", "alice@gmail.com", "Stripe"),
        User("3", "Bob", "alice@gmail.com", "Stripe"),
        User("4", "Bob", "bob@google.com", "Stripe"),
    ]
    # 1-2: name+company=0.5, 2-3: email+company=0.7, 3-4: name+company=0.5
    # Chain: 1-2-3-4 all connected
    components = find_connected_components(users, threshold=0.5)
    assert len(components) == 1
    assert components[0] == {"1", "2", "3", "4"}


if __name__ == "__main__":
    test_similar_pairs()
    test_no_matches()
    test_one_hop_groups()
    test_connected_components()
    test_single_component()
    print("All tests passed!")
