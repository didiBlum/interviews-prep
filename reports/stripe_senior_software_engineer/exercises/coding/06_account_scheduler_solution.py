"""
AccountScheduler — Solution
=============================

Approach:
- Store locks per account as sorted list of (start, end) intervals.
- Use bisect for efficient overlap checking.
- Track last_lock_end per account for LRU selection.
"""

import bisect
from typing import Optional


class AccountScheduler:
    def __init__(self):
        self.locks: dict[str, list[tuple[int, int]]] = {}
        self.last_lock_end: dict[str, int] = {}

    def register(self, account_id: str) -> None:
        if account_id not in self.locks:
            self.locks[account_id] = []
            self.last_lock_end[account_id] = 0

    def is_available(self, account_id: str, t: int) -> bool:
        if account_id not in self.locks:
            return True
        for start, end in self.locks[account_id]:
            if start <= t < end:
                return False
        return True

    def acquire(self, account_id: str, t: int, duration: int) -> bool:
        if not self.is_available(account_id, t):
            return False

        new_lock = (t, t + duration)

        # Check that the new lock doesn't overlap with any existing lock
        for start, end in self.locks[account_id]:
            if new_lock[0] < end and new_lock[1] > start:
                return False

        # Insert in sorted order
        bisect.insort(self.locks[account_id], new_lock)

        # Update LRU tracking
        if t + duration > self.last_lock_end[account_id]:
            self.last_lock_end[account_id] = t + duration

        return True

    def acquire_any(self, t: int, duration: int) -> Optional[str]:
        # Find all available accounts at time t
        available = []
        for account_id in self.locks:
            if self.is_available(account_id, t):
                available.append((self.last_lock_end[account_id], account_id))

        if not available:
            return None

        # Pick LRU (smallest last_lock_end)
        available.sort()
        chosen_id = available[0][1]

        self.acquire(chosen_id, t, duration)
        return chosen_id


# ============ Complexity Analysis ============
# is_available: O(N) worst case scanning all locks for an account.
#   Could be O(log N) with binary search on sorted intervals.
# acquire: O(N) for overlap check + O(N) for bisect insert.
# acquire_any: O(A * N) where A = accounts, N = max locks per account.
#   Could be O(A log A) with a heap for LRU tracking.
# Space: O(total locks across all accounts)

# ============ Common Interviewer Follow-ups ============
# Q: "How would you make is_available O(log N)?"
# A: Use an interval tree or binary search on sorted non-overlapping intervals.
#    Since our locks are non-overlapping and sorted, binary search on start
#    times to find the nearest interval.
#
# Q: "How would you make acquire_any O(log A)?"
# A: Use a min-heap keyed by last_lock_end. Pop, check availability,
#    re-insert after acquiring. Lazy deletion for stale entries.
#
# Q: "What about concurrent access?"
# A: Per-account locks for is_available/acquire. Global lock or CAS for
#    acquire_any to prevent two callers grabbing the same account.

# ============ What Interviewers Look For ============
# 1. Correct interval overlap detection (half-open intervals [start, end))
# 2. Clean separation of availability check vs. acquisition
# 3. Understanding LRU as "least recently USED" not "least recently registered"
# 4. Handling edge cases: acquire at exact end time, no available accounts
# 5. Discussing optimization paths (interval trees, heaps) even if not implementing


# ============ TESTS ============

def test_basic_availability():
    sched = AccountScheduler()
    sched.register("acct1")
    assert sched.is_available("acct1", 0) == True
    assert sched.acquire("acct1", 10, 5) == True
    assert sched.is_available("acct1", 10) == False
    assert sched.is_available("acct1", 14) == False
    assert sched.is_available("acct1", 15) == True

def test_overlapping_acquire():
    sched = AccountScheduler()
    sched.register("acct1")
    assert sched.acquire("acct1", 10, 5) == True
    assert sched.acquire("acct1", 12, 3) == False
    assert sched.acquire("acct1", 15, 5) == True

def test_multiple_locks():
    sched = AccountScheduler()
    sched.register("acct1")
    sched.acquire("acct1", 0, 5)
    sched.acquire("acct1", 10, 5)
    assert sched.is_available("acct1", 5) == True
    assert sched.is_available("acct1", 9) == True
    assert sched.is_available("acct1", 10) == False

def test_acquire_any_lru():
    sched = AccountScheduler()
    sched.register("acct1")
    sched.register("acct2")
    sched.register("acct3")
    sched.acquire("acct1", 0, 5)
    sched.acquire("acct2", 0, 3)
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
    sched.acquire("acct1", 0, 10)
    sched.acquire("acct2", 0, 3)
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
