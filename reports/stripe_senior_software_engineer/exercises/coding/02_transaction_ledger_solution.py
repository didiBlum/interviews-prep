"""
Transaction Ledger — Solution
==============================

Approach: Single-pass iteration with a balance dict.
- Part 1: Accumulate, filter non-zero.
- Part 2: Check before applying withdrawals.
- Part 3: Compute shortfall, borrow from reserve, track max borrowed.

Time: O(N) for all parts.
Space: O(A) where A = unique accounts.
"""

from collections import defaultdict


def calculate_balances(transactions: list[tuple[str, int]]) -> dict[str, int]:
    balances = defaultdict(int)
    for account_id, amount in transactions:
        balances[account_id] += amount
    return {k: v for k, v in balances.items() if v != 0}


def process_with_rejections(
    transactions: list[tuple[str, int]],
) -> tuple[dict[str, int], list[tuple[str, int]]]:
    balances = defaultdict(int)
    rejected = []

    for account_id, amount in transactions:
        if amount < 0 and balances[account_id] + amount < 0:
            rejected.append((account_id, amount))
        else:
            balances[account_id] += amount

    non_zero = {k: v for k, v in balances.items() if v != 0}
    return non_zero, rejected


def process_with_lending(
    transactions: list[tuple[str, int]],
    initial_reserve: int,
) -> tuple[dict[str, int], int]:
    balances = defaultdict(int)
    reserve = initial_reserve
    total_borrowed = 0

    for account_id, amount in transactions:
        new_balance = balances[account_id] + amount

        if new_balance < 0:
            shortfall = abs(new_balance)
            reserve -= shortfall
            total_borrowed += shortfall
            balances[account_id] = 0
        else:
            balances[account_id] = new_balance

    active = {k: v for k, v in balances.items()}
    return active, total_borrowed


# ============ Complexity Analysis ============
# Time: O(N) — single pass through transactions for all parts
# Space: O(A) — one balance entry per unique account
#
# Note: "max_borrowed" in Part 3 is cumulative total borrowed, not
# the peak outstanding balance. If the problem asks for peak outstanding,
# you'd need to track repayments too.

# ============ Common Interviewer Follow-ups ============
# Q: "What if transactions can arrive out of order?"
# A: Need a timestamp and sorting, or process in batches.
#
# Q: "How would you make this concurrent?"
# A: Per-account locks (fine-grained locking) or optimistic concurrency
#    with version numbers. The reserve needs its own lock or atomic ops.
#
# Q: "What about idempotency?"
# A: Add a transaction_id. Use a set to track processed IDs and skip
#    duplicates. Critical for Stripe's real payment system.

# ============ What Interviewers Look For ============
# 1. Using defaultdict for clean accumulation (not manual key checks)
# 2. Handling the zero-balance filter correctly
# 3. Not rejecting deposits (only withdrawals can be rejected)
# 4. Correct shortfall calculation in Part 3
# 5. Clear separation between the three parts (good API design)

# ============ Alternative Approaches ============
# For Part 3, an alternative is to never let accounts go negative and
# instead track "credit lines" separately. This models real-world lending
# more accurately but adds complexity.


# ============ TESTS ============

def test_calculate_balances():
    txns = [("A", 100), ("B", 200), ("A", -30), ("B", -200), ("C", 50)]
    result = calculate_balances(txns)
    assert result == {"A": 70, "C": 50}

def test_empty_transactions():
    assert calculate_balances([]) == {}

def test_all_zero_balances():
    txns = [("A", 100), ("A", -100)]
    assert calculate_balances(txns) == {}

def test_rejections_basic():
    txns = [("A", 100), ("A", -150), ("A", -50), ("B", 200), ("B", -300)]
    balances, rejected = process_with_rejections(txns)
    assert balances == {"A": 50, "B": 200}
    assert rejected == [("A", -150), ("B", -300)]

def test_rejections_order_matters():
    txns = [("A", 100), ("A", -60), ("A", -60)]
    balances, rejected = process_with_rejections(txns)
    assert balances == {"A": 40}
    assert rejected == [("A", -60)]

def test_lending_basic():
    txns = [("A", 100), ("A", -150)]
    balances, max_borrowed = process_with_lending(txns, initial_reserve=1000)
    assert balances == {"A": 0}
    assert max_borrowed == 50

def test_lending_multiple():
    txns = [("A", 100), ("A", -200), ("B", 50), ("B", -100)]
    balances, max_borrowed = process_with_lending(txns, initial_reserve=500)
    assert balances == {"A": 0, "B": 0}
    assert max_borrowed == 150


if __name__ == "__main__":
    test_calculate_balances()
    test_empty_transactions()
    test_all_zero_balances()
    test_rejections_basic()
    test_rejections_order_matters()
    test_lending_basic()
    test_lending_multiple()
    print("All tests passed!")
