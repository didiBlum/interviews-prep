"""
AccountScheduler
================
Source: Stripe onsite coding round (linkjob.ai, 2025-2026)

Problem:
Build an account availability scheduler.

Part 1: Implement `is_available(account_id: str, t: int) -> bool`
  - Returns True if the account is not currently locked at timestamp t.
  - Initially all accounts are available.

Part 2: Add `acquire(account_id: str, t: int, duration: int) -> bool`
  - Lock the account from time t to t + duration (exclusive).
  - Returns True if acquired, False if the account is already locked at time t.
  - An account can have multiple non-overlapping locks.

Part 3: Add `acquire_any(t: int, duration: int) -> Optional[str]`
  - Select the least-recently-used available account at time t and lock it.
  - "Least recently used" = the account whose last lock ended earliest.
  - Returns the account_id, or None if no accounts are available.
  - Accounts must be registered first via `register(account_id)`.

Complexity targets:
- is_available: O(log N) where N = number of locks for that account
- acquire: O(log N)
- acquire_any: O(A) where A = number of registered accounts (naive),
  or O(log A) with a sorted structure
"""

from typing import Optional


class AccountScheduler:
    def __init__(self):
        # TODO: Implement
        pass

    def register(self, account_id: str) -> None:
        """Register an account so it can be acquired."""
        # TODO: Implement
        pass

    def is_available(self, account_id: str, t: int) -> bool:
        """Check if account is available (not locked) at time t."""
        # TODO: Implement
        pass

    def acquire(self, account_id: str, t: int, duration: int) -> bool:
        """
        Lock account from [t, t+duration).
        Returns True if successfully acquired, False if already locked.
        """
        # TODO: Implement
        pass

    def acquire_any(self, t: int, duration: int) -> Optional[str]:
        """
        Acquire the least-recently-used available account.
        Returns account_id or None.
        """
        # TODO: Implement
        pass


# HINT 1: Store locks per account as a sorted list of (start, end) intervals.
#         is_available checks if t falls within any interval.

# HINT 2: For acquire, first check is_available, then insert the new lock
#         in sorted order. Use bisect for O(log N) insertion point.

# HINT 3: For LRU, track the last lock end time per account.
#         Among available accounts, pick the one with the smallest
#         last_lock_end (or 0 if never locked).


# ============ TESTS ============

def test_basic_availability():
    sched = AccountScheduler()
    sched.register("acct1")
    assert sched.is_available("acct1", 0) == True
    assert sched.acquire("acct1", 10, 5) == True  # locked [10, 15)
    assert sched.is_available("acct1", 10) == False
    assert sched.is_available("acct1", 14) == False
    assert sched.is_available("acct1", 15) == True

def test_overlapping_acquire():
    sched = AccountScheduler()
    sched.register("acct1")
    assert sched.acquire("acct1", 10, 5) == True   # [10, 15)
    assert sched.acquire("acct1", 12, 3) == False   # overlaps
    assert sched.acquire("acct1", 15, 5) == True    # [15, 20) — no overlap

def test_multiple_locks():
    sched = AccountScheduler()
    sched.register("acct1")
    sched.acquire("acct1", 0, 5)   # [0, 5)
    sched.acquire("acct1", 10, 5)  # [10, 15)
    assert sched.is_available("acct1", 5) == True
    assert sched.is_available("acct1", 9) == True
    assert sched.is_available("acct1", 10) == False

def test_acquire_any_lru():
    sched = AccountScheduler()
    sched.register("acct1")
    sched.register("acct2")
    sched.register("acct3")

    # acct1 locked most recently
    sched.acquire("acct1", 0, 5)   # last lock ends at 5
    sched.acquire("acct2", 0, 3)   # last lock ends at 3

    # At t=5, all available. LRU order: acct3 (never locked, 0), acct2 (3), acct1 (5)
    result = sched.acquire_any(5, 2)
    assert result == "acct3"

def test_acquire_any_none_available():
    sched = AccountScheduler()
    sched.register("acct1")
    sched.acquire("acct1", 0, 10)
    assert sched.acquire_any(5, 2) is None

def test_acquire_any_skips_locked():
    sched = AccountScheduler()
    sched.register("acct1")
    sched.register("acct2")
    sched.acquire("acct1", 0, 10)  # locked until 10
    sched.acquire("acct2", 0, 3)   # locked until 3

    # At t=5, only acct2 is available
    result = sched.acquire_any(5, 2)
    assert result == "acct2"


if __name__ == "__main__":
    test_basic_availability()
    test_overlapping_acquire()
    test_multiple_locks()
    test_acquire_any_lru()
    test_acquire_any_none_available()
    test_acquire_any_skips_locked()
    print("All tests passed!")
