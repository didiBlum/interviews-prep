"""
Currency Exchange Rate
======================
Source: Stripe onsite coding round (linkjob.ai, 2025)
LeetCode equivalent: LC 399 (Evaluate Division)

Problem:
Given a set of known currency exchange rates, compute the exchange rate
between any two currencies.

Part 1: Basic exchange rate lookup.
  - Input: list of (from_currency, to_currency, rate) tuples
  - Query: (from_currency, to_currency) -> float or -1.0 if impossible
  - Rates are transitive: if USD->EUR = 0.85 and EUR->GBP = 0.88,
    then USD->GBP = 0.85 * 0.88 = 0.748

Part 2: Handle inverse rates.
  - If USD->EUR = 0.85, then EUR->USD = 1/0.85
  - This doubles the edges in your graph.

Part 3: Find the best (maximum) exchange rate between two currencies.
  - There may be multiple paths. Find the one with the best rate.
  - Example: USD->GBP might be better direct (0.75) vs through EUR (0.748).

Complexity targets:
- Build graph: O(E) where E = number of exchange rates
- Query: O(V + E) per query using BFS/DFS
- Part 3: O(V + E) with modified BFS tracking max product
"""


def exchange_rate(
    rates: list[tuple[str, str, float]],
    query_from: str,
    query_to: str,
) -> float:
    """
    Part 1 + 2: Find exchange rate from query_from to query_to.
    Include inverse rates automatically.
    Returns -1.0 if no path exists.
    """
    # TODO: Implement
    pass


def best_exchange_rate(
    rates: list[tuple[str, str, float]],
    query_from: str,
    query_to: str,
) -> float:
    """
    Part 3: Find the BEST (maximum) exchange rate via any path.
    Returns -1.0 if no path exists.
    """
    # TODO: Implement
    pass


# HINT 1: Model as a directed graph where edge weight is the exchange rate.
#         Add both directions: (A->B, rate) and (B->A, 1/rate).

# HINT 2: BFS/DFS from source to target, multiplying rates along the path.
#         Track visited nodes to avoid cycles.

# HINT 3: For best rate, use BFS/DFS but track the MAXIMUM product to each node.
#         Similar to shortest path but with multiplication and maximization.


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
        ("EUR", "GBP", 0.88),  # USD->GBP via EUR: 0.748
        ("USD", "GBP", 0.75),  # USD->GBP direct: 0.75
    ]
    # Best is direct: 0.75
    assert abs(best_exchange_rate(rates, "USD", "GBP") - 0.75) < 1e-9

def test_best_rate_indirect():
    rates = [
        ("USD", "EUR", 0.90),
        ("EUR", "GBP", 0.95),  # USD->GBP via EUR: 0.855
        ("USD", "GBP", 0.80),  # USD->GBP direct: 0.80
    ]
    # Best is via EUR: 0.855
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
