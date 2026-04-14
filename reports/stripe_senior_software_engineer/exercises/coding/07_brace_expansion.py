"""
Brace Expansion
===============
Source: Stripe onsite coding round (codinginterview.com, 2024-2025)
LeetCode equivalent: LC 1087

Problem:
Given a string pattern with curly braces representing choices, generate
all possible words in lexicographic order.

Rules:
- `{a,b,c}` means choose one of a, b, c
- Characters outside braces are literal
- Braces do not nest
- Output must be in sorted (lexicographic) order

Examples:
  "{a,b}c{d,e}" -> ["acd", "ace", "bcd", "bce"]
  "a{b,c}d" -> ["abd", "acd"]
  "abc" -> ["abc"]
  "{z,a}" -> ["a", "z"]

Complexity targets:
- Time: O(P * N log N) where P = number of combinations, N = pattern length
- Space: O(P * N) for storing all combinations
"""


def brace_expansion(pattern: str) -> list[str]:
    """
    Generate all possible words from the pattern in lexicographic order.
    """
    # TODO: Implement
    pass


# HINT 1: Parse the pattern into a list of "groups". Each group is either
#         a single character [c] or a list of options [a, b, c].

# HINT 2: Use itertools.product or recursive backtracking to generate
#         all combinations from the groups.

# HINT 3: Sort each group's options before generating combinations —
#         this ensures lexicographic output order naturally.


# ============ TESTS ============

def test_basic():
    assert brace_expansion("{a,b}c{d,e}") == ["acd", "ace", "bcd", "bce"]

def test_single_brace():
    assert brace_expansion("a{b,c}d") == ["abd", "acd"]

def test_no_braces():
    assert brace_expansion("abc") == ["abc"]

def test_sort_within_braces():
    assert brace_expansion("{z,a}") == ["a", "z"]

def test_multiple_options():
    assert brace_expansion("{a,b,c}") == ["a", "b", "c"]

def test_start_and_end_literal():
    result = brace_expansion("x{a,b}y{c,d}z")
    assert result == ["xaycz", "xaydz", "xbycz", "xbydz"]

def test_empty_between():
    assert brace_expansion("{a,b}{c,d}") == ["ac", "ad", "bc", "bd"]


if __name__ == "__main__":
    test_basic()
    test_single_brace()
    test_no_braces()
    test_sort_within_braces()
    test_multiple_options()
    test_start_and_end_literal()
    test_empty_between()
    print("All tests passed!")
