"""
Currency Exchange Rate — Solution
===================================

Approach: Weighted directed graph + BFS.
"""

from collections import defaultdict, deque


def _build_graph(
    rates: list[tuple[str, str, float]],
) -> dict[str, list[tuple[str, float]]]:
    """Build adjacency list with both directions."""
    graph = defaultdict(list)
    for src, dst, rate in rates:
        graph[src].append((dst, rate))
        graph[dst].append((src, 1.0 / rate))
    return graph


def exchange_rate(
    rates: list[tuple[str, str, float]],
    query_from: str,
    query_to: str,
) -> float:
    if query_from == query_to:
        # Check if currency exists in any rate
        all_currencies = set()
        for src, dst, _ in rates:
            all_currencies.add(src)
            all_currencies.add(dst)
        return 1.0 if query_from in all_currencies else -1.0

    graph = _build_graph(rates)

    if query_from not in graph:
        return -1.0

    # BFS
    visited = {query_from}
    queue = deque([(query_from, 1.0)])

    while queue:
        node, cumulative_rate = queue.popleft()

        for neighbor, rate in graph[node]:
            if neighbor == query_to:
                return cumulative_rate * rate

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, cumulative_rate * rate))

    return -1.0


def best_exchange_rate(
    rates: list[tuple[str, str, float]],
    query_from: str,
    query_to: str,
) -> float:
    if query_from == query_to:
        all_currencies = set()
        for src, dst, _ in rates:
            all_currencies.add(src)
            all_currencies.add(dst)
        return 1.0 if query_from in all_currencies else -1.0

    graph = _build_graph(rates)

    if query_from not in graph:
        return -1.0

    # DFS exploring all simple (cycle-free) paths, tracking max product
    best_result = [-1.0]

    def dfs(node: str, cumulative: float, visited: set[str]):
        if node == query_to:
            best_result[0] = max(best_result[0], cumulative)
            return
        for neighbor, rate in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                dfs(neighbor, cumulative * rate, visited)
                visited.remove(neighbor)

    visited = {query_from}
    dfs(query_from, 1.0, visited)
    return best_result[0]


# ============ Complexity Analysis ============
# Build graph: O(E)
# exchange_rate (BFS): O(V + E) per query
# best_exchange_rate: O(V + E) — similar to Bellman-Ford for max product
#   Note: for truly optimal with negative cycles, need more care.
#   Exchange rates are positive, so max-product BFS works correctly.
# Space: O(V + E) for the graph

# ============ Common Interviewer Follow-ups ============
# Q: "What about triangular arbitrage (cycles with product > 1)?"
# A: Detect cycles where the product of rates > 1. This is equivalent
#    to finding negative cycles in log-transformed graph (Bellman-Ford).
#
# Q: "How would you handle real-time rate updates?"
# A: Maintain the graph, update edge weights. Invalidate cached paths.
#    For live trading, precompute all-pairs rates (Floyd-Warshall) and
#    update incrementally.
#
# Q: "What about precision issues with floating point?"
# A: Use Decimal for financial calculations. Or work in log-space
#    (sum of logs instead of product) to avoid underflow/overflow.

# ============ What Interviewers Look For ============
# 1. Correctly modeling as a graph with bidirectional edges
# 2. Using BFS (not just DFS) for shortest/best path
# 3. Handling edge cases: same currency, unknown currency, no path
# 4. Multiplying (not adding) weights along the path
# 5. Discussing precision and financial accuracy concerns


# ============ TESTS ============

def test_direct_rate():
    rates = [("USD", "EUR", 0.85)]
    assert abs(exchange_rate(rates, "USD", "EUR") - 0.85) < 1e-9

def test_inverse_rate():
    rates = [("USD", "EUR", 0.85)]
    assert abs(exchange_rate(rates, "EUR", "USD") - 1/0.85) < 1e-9

def test_transitive_rate():
    rates = [("USD", "EUR", 0.85), ("EUR", "GBP", 0.88)]
    expected = 0.85 * 0.88
    assert abs(exchange_rate(rates, "USD", "GBP") - expected) < 1e-9

def test_no_path():
    rates = [("USD", "EUR", 0.85)]
    assert exchange_rate(rates, "USD", "JPY") == -1.0

def test_same_currency():
    rates = [("USD", "EUR", 0.85)]
    assert abs(exchange_rate(rates, "USD", "USD") - 1.0) < 1e-9

def test_unknown_currency():
    rates = [("USD", "EUR", 0.85)]
    assert exchange_rate(rates, "XYZ", "EUR") == -1.0

def test_best_rate():
    rates = [
        ("USD", "EUR", 0.85),
        ("EUR", "GBP", 0.88),
        ("USD", "GBP", 0.75),
    ]
    assert abs(best_exchange_rate(rates, "USD", "GBP") - 0.75) < 1e-9

def test_best_rate_indirect():
    rates = [
        ("USD", "EUR", 0.90),
        ("EUR", "GBP", 0.95),
        ("USD", "GBP", 0.80),
    ]
    assert abs(best_exchange_rate(rates, "USD", "GBP") - 0.855) < 1e-9


if __name__ == "__main__":
    test_direct_rate()
    test_inverse_rate()
    test_transitive_rate()
    test_no_path()
    test_same_currency()
    test_unknown_currency()
    test_best_rate()
    test_best_rate_indirect()
    print("All tests passed!")
