"""
Transaction Ledger / Account Balance Manager
=============================================
Source: Stripe onsite coding round (linkjob.ai, 2025-2026)

Problem:
You are building a simplified transaction processing system.

Part 1: Given a list of transactions, calculate the non-zero balance for each account.
  - Each transaction is: (account_id, amount)
  - amount > 0 is a deposit, amount < 0 is a withdrawal
  - Return a dict of {account_id: balance} for all non-zero balances

Part 2: Track rejected transactions.
  - A withdrawal is rejected if it would make the account balance negative.
  - Process transactions in order. Return (balances, rejected_transactions).

Part 3: Platform lending.
  - There is a special "platform_reserve" account with an initial balance.
  - If a non-platform account would go negative, it borrows from the platform reserve.
  - Track the maximum amount borrowed from the platform reserve at any point.
  - Return (balances, max_reserve_borrowed).

Complexity targets:
- O(N) time where N = number of transactions
- O(A) space where A = number of unique accounts
"""

from typing import Optional


def calculate_balances(transactions: list[tuple[str, int]]) -> dict[str, int]:
    """
    Part 1: Calculate non-zero balances from a list of transactions.

    Args:
        transactions: List of (account_id, amount) tuples.
    Returns:
        Dict mapping account_id to balance, excluding zero balances.
    """
    # TODO: Implement
    pass


def process_with_rejections(
    transactions: list[tuple[str, int]],
) -> tuple[dict[str, int], list[tuple[str, int]]]:
    """
    Part 2: Process transactions, rejecting those that would cause negative balances.

    Returns:
        Tuple of (balances_dict, list_of_rejected_transactions)
    """
    # TODO: Implement
    pass


def process_with_lending(
    transactions: list[tuple[str, int]],
    initial_reserve: int,
) -> tuple[dict[str, int], int]:
    """
    Part 3: Process transactions with platform reserve lending.

    If a withdrawal would make an account negative, borrow the shortfall
    from the platform reserve. The platform reserve CAN go negative.

    Args:
        transactions: List of (account_id, amount) tuples.
        initial_reserve: Starting balance of the platform reserve.
    Returns:
        Tuple of (balances_dict, max_amount_borrowed_from_reserve)
    """
    # TODO: Implement
    pass


# HINT 1: Use a defaultdict(int) for account balances. Iterate once through
#         transactions, accumulating amounts per account.

# HINT 2: For rejections, check if balance + amount < 0 before applying.
#         Only reject withdrawals (amount < 0), not deposits.

# HINT 3: For lending, when balance + amount < 0, the shortfall is
#         abs(balance + amount). Deduct that from the reserve and set
#         the account to 0. Track cumulative borrowing, not per-transaction.


# ============ TESTS ============

def test_calculate_balances():
    txns = [("A", 100), ("B", 200), ("A", -30), ("B", -200), ("C", 50)]
    result = calculate_balances(txns)
    assert result == {"A": 70, "C": 50}  # B is zero, excluded

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
    # First withdrawal: 100 - 60 = 40. Second: 40 - 60 < 0, rejected.
    assert balances == {"A": 40}
    assert rejected == [("A", -60)]

def test_lending_basic():
    txns = [("A", 100), ("A", -150)]
    balances, max_borrowed = process_with_lending(txns, initial_reserve=1000)
    # A tries to withdraw 150 with balance 100. Shortfall = 50.
    # Borrow 50 from reserve. A balance = 0, reserve = 950.
    assert balances == {"A": 0}
    assert max_borrowed == 50

def test_lending_multiple():
    txns = [("A", 100), ("A", -200), ("B", 50), ("B", -100)]
    balances, max_borrowed = process_with_lending(txns, initial_reserve=500)
    # A: balance 100, withdraw 200 -> shortfall 100 -> borrow 100, reserve=400
    # B: balance 50, withdraw 100 -> shortfall 50 -> borrow 50, reserve=350
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
