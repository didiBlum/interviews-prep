"""
Brace Expansion — Solution
============================

Approach: Parse into groups, then compute Cartesian product.
"""

from itertools import product


def brace_expansion(pattern: str) -> list[str]:
    # Parse pattern into groups
    groups = []
    i = 0
    while i < len(pattern):
        if pattern[i] == "{":
            # Find closing brace
            j = pattern.index("}", i)
            options = sorted(pattern[i+1:j].split(","))
            groups.append(options)
            i = j + 1
        else:
            groups.append([pattern[i]])
            i += 1

    # Generate all combinations
    if not groups:
        return [""]

    results = ["".join(combo) for combo in product(*groups)]
    return sorted(results)


# ============ Alternative: Recursive Backtracking ============

def brace_expansion_recursive(pattern: str) -> list[str]:
    groups = []
    i = 0
    while i < len(pattern):
        if pattern[i] == "{":
            j = pattern.index("}", i)
            options = sorted(pattern[i+1:j].split(","))
            groups.append(options)
            i = j + 1
        else:
            groups.append([pattern[i]])
            i += 1

    results = []

    def backtrack(idx: int, current: list[str]):
        if idx == len(groups):
            results.append("".join(current))
            return
        for option in groups[idx]:
            current.append(option)
            backtrack(idx + 1, current)
            current.pop()

    backtrack(0, [])
    return results


# ============ Complexity Analysis ============
# Let G = number of groups, K = max options per group
# Time: O(K^G * G) — K^G combinations, each of length G
# Space: O(K^G * G) for storing all results
#
# Sorting each group before generating ensures lex order when
# using product (which preserves input order). Final sort is
# a safety net but technically unnecessary if groups are pre-sorted.

# ============ Common Interviewer Follow-ups ============
# Q: "What if braces can be nested: {a,{b,c}}?"
# A: Need recursive parsing. Parse inner braces first, expand, then outer.
#
# Q: "What about escape characters: \{a\}?"
# A: Track escape state, skip braces preceded by backslash.
#
# Q: "What if options can be multi-character: {ab,cd}?"
# A: Already handled! Our solution works with multi-char options.

# ============ What Interviewers Look For ============
# 1. Clean parsing (separating parse from combination generation)
# 2. Correct handling of edge cases (no braces, adjacent braces)
# 3. Using itertools.product vs manual recursion (both acceptable)
# 4. Ensuring lexicographic order (sort options before combining)
# 5. Not overcomplicating — this is a medium problem, keep it simple


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

def test_recursive_matches():
    # Verify both implementations match
    patterns = ["{a,b}c{d,e}", "a{b,c}d", "abc", "{z,a}", "{a,b}{c,d}"]
    for p in patterns:
        assert brace_expansion(p) == brace_expansion_recursive(p)


if __name__ == "__main__":
    test_basic()
    test_single_brace()
    test_no_braces()
    test_sort_within_braces()
    test_multiple_options()
    test_start_and_end_literal()
    test_empty_between()
    test_recursive_matches()
    print("All tests passed!")
