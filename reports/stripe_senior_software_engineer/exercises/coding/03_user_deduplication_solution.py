"""
User Deduplication — Solution
==============================

Part 1: Pairwise comparison with weighted scoring.
Part 2: BFS/DFS from adjacency list for 1-hop groups.
Part 3: Union-Find with path compression and union by rank.
"""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str
    email: str
    company: str


WEIGHTS = {"name": 0.3, "email": 0.5, "company": 0.2}


def _similarity_score(u1: User, u2: User) -> float:
    score = 0.0
    if u1.name == u2.name:
        score += WEIGHTS["name"]
    if u1.email == u2.email:
        score += WEIGHTS["email"]
    if u1.company == u2.company:
        score += WEIGHTS["company"]
    return score


def find_similar_pairs(
    users: list[User], threshold: float
) -> list[tuple[str, str]]:
    pairs = []
    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            if _similarity_score(users[i], users[j]) >= threshold:
                a, b = sorted([users[i].id, users[j].id])
                pairs.append((a, b))
    return pairs


def find_linked_groups_one_hop(
    users: list[User], threshold: float
) -> list[set[str]]:
    pairs = find_similar_pairs(users, threshold)

    # Build adjacency list
    adj = defaultdict(set)
    for a, b in pairs:
        adj[a].add(b)
        adj[b].add(a)

    # BFS from each node, depth limited to 1 hop
    visited = set()
    groups = []

    for node in adj:
        if node in visited:
            continue
        # BFS
        group = set()
        queue = [node]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            group.add(current)
            for neighbor in adj[current]:
                if neighbor not in visited:
                    queue.append(neighbor)
        if len(group) > 1:
            groups.append(group)

    return groups


class UnionFind:
    def __init__(self, elements: list[str]):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}

    def find(self, x: str) -> str:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: str, y: str) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        # union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


def find_connected_components(
    users: list[User], threshold: float
) -> list[set[str]]:
    ids = [u.id for u in users]
    uf = UnionFind(ids)

    pairs = find_similar_pairs(users, threshold)
    for a, b in pairs:
        uf.union(a, b)

    # Group by root
    components = defaultdict(set)
    for uid in ids:
        root = uf.find(uid)
        components[root].add(uid)

    return [c for c in components.values() if len(c) > 1]


# ============ Complexity Analysis ============
# Part 1: O(N^2) — must compare all pairs
# Part 2: O(N^2 + V + E) — pairs + BFS
# Part 3: O(N^2 * alpha(N)) — pairs + union-find operations
#   alpha(N) is the inverse Ackermann function, effectively constant

# ============ Common Interviewer Follow-ups ============
# Q: "What if fields have fuzzy matching (e.g., 'Alice' vs 'alice')?"
# A: Normalize (lowercase, strip whitespace). For partial matches,
#    use edit distance or Jaccard similarity with fractional scores.
#
# Q: "How would you scale this to millions of users?"
# A: Blocking/bucketing: only compare users that share at least one
#    field value (e.g., same email domain). Reduces O(N^2) to O(N*B).
#    LSH (Locality-Sensitive Hashing) for approximate nearest neighbors.
#
# Q: "What about incremental updates (new users arriving)?"
# A: Compare new user against existing users only. Update union-find
#    incrementally. Don't reprocess all pairs.

# ============ What Interviewers Look For ============
# 1. Clean separation of scoring vs. grouping logic
# 2. Correct Union-Find implementation (path compression + rank)
# 3. Understanding that Part 2 (1-hop) is really just BFS/connected components
# 4. Edge case handling: no matches, all users identical
# 5. Discussing scalability beyond the naive O(N^2)


# ============ TESTS ============

def test_similar_pairs():
    users = [
        User("1", "Alice", "alice@stripe.com", "Stripe"),
        User("2", "Alice", "alice@gmail.com", "Stripe"),
        User("3", "Bob", "bob@stripe.com", "Stripe"),
        User("4", "Alice", "alice@stripe.com", "Google"),
    ]
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
        User("3", "Bob", "alice@gmail.com", "Google"),
    ]
    groups = find_linked_groups_one_hop(users, threshold=0.5)
    assert len(groups) == 1
    assert groups[0] == {"1", "2", "3"}

def test_connected_components():
    users = [
        User("1", "Alice", "a@x.com", "Stripe"),
        User("2", "Alice", "b@x.com", "Stripe"),
        User("3", "Bob", "c@x.com", "Stripe"),
        User("4", "Bob", "c@x.com", "Google"),
    ]
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
