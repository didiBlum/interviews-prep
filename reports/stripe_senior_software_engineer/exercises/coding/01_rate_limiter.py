"""
Rate Limiter
============
Source: Stripe onsite coding round (confirmed by multiple candidates 2024-2026)

Problem:
Design a function that implements a sliding-window rate limiter.

Part 1: Implement `is_allowed(user_id: str, timestamp: int) -> bool`
- Allow at most N requests per user per W-second window.
- The window slides (it's not fixed intervals).

Part 2: Add `get_remaining(user_id: str, timestamp: int) -> int`
- Return how many requests the user can still make in the current window.

Part 3: Support different rate limits per user tier.
- "free" users: 5 requests per 60 seconds
- "pro" users: 20 requests per 60 seconds
- "enterprise" users: 100 requests per 60 seconds

Complexity targets:
- is_allowed: O(1) amortized time, O(N) space per user where N = max requests
- Hint: cleanup old timestamps lazily

Constraints:
- Timestamps are given in seconds, always non-decreasing.
- user_id is a non-empty string.
"""

from collections import deque


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the window.
            window_seconds: Size of the sliding window in seconds.
        """
        # TODO: Implement initialization
        pass

    def is_allowed(self, user_id: str, timestamp: int) -> bool:
        """
        Check if a request from user_id at the given timestamp is allowed.
        If allowed, record the request. If not, reject it.

        Returns True if allowed, False if rate-limited.
        """
        # TODO: Implement sliding window rate limiting
        pass

    def get_remaining(self, user_id: str, timestamp: int) -> int:
        """
        Return the number of requests the user can still make
        within the current window ending at timestamp.
        """
        # TODO: Implement remaining count
        pass


class TieredRateLimiter:
    """
    Part 3: Rate limiter with per-tier limits.
    Tiers: "free" (5/60s), "pro" (20/60s), "enterprise" (100/60s)
    """

    TIER_LIMITS = {
        "free": (5, 60),
        "pro": (20, 60),
        "enterprise": (100, 60),
    }

    def __init__(self):
        # TODO: Implement initialization
        pass

    def set_tier(self, user_id: str, tier: str) -> None:
        """Set the tier for a user. Default tier is 'free'."""
        # TODO: Implement tier assignment
        pass

    def is_allowed(self, user_id: str, timestamp: int) -> bool:
        """Check if request is allowed based on user's tier."""
        # TODO: Implement tiered rate limiting
        pass


# HINT 1: Use a deque (double-ended queue) of timestamps per user.
#         Remove timestamps from the front that are outside the window.

# HINT 2: For is_allowed, first clean up expired timestamps, then check
#         if the current count is below the limit before adding.

# HINT 3: For tiered limits, look up the user's tier to get (max_requests, window)
#         and delegate to the same sliding-window logic.


# ============ TESTS ============

def test_basic_rate_limiting():
    rl = RateLimiter(max_requests=3, window_seconds=10)
    assert rl.is_allowed("user1", 1) == True
    assert rl.is_allowed("user1", 2) == True
    assert rl.is_allowed("user1", 3) == True
    assert rl.is_allowed("user1", 4) == False  # 4th request within 10s
    assert rl.is_allowed("user1", 11) == False  # ts=1 just expired, but 2,3 still in window
    assert rl.is_allowed("user1", 12) == True   # ts=1,2 expired; only ts=3 in window

def test_independent_users():
    rl = RateLimiter(max_requests=2, window_seconds=5)
    assert rl.is_allowed("alice", 1) == True
    assert rl.is_allowed("bob", 1) == True
    assert rl.is_allowed("alice", 2) == True
    assert rl.is_allowed("alice", 3) == False
    assert rl.is_allowed("bob", 3) == True  # bob only has 1 request

def test_window_expiration():
    rl = RateLimiter(max_requests=1, window_seconds=5)
    assert rl.is_allowed("user1", 1) == True
    assert rl.is_allowed("user1", 5) == False  # ts=1 is still in [1, 5]
    assert rl.is_allowed("user1", 6) == True   # ts=1 is now outside [2, 6]

def test_get_remaining():
    rl = RateLimiter(max_requests=3, window_seconds=10)
    assert rl.get_remaining("user1", 1) == 3
    rl.is_allowed("user1", 1)
    assert rl.get_remaining("user1", 2) == 2
    rl.is_allowed("user1", 2)
    rl.is_allowed("user1", 3)
    assert rl.get_remaining("user1", 4) == 0

def test_tiered_rate_limiter():
    trl = TieredRateLimiter()
    trl.set_tier("free_user", "free")
    trl.set_tier("pro_user", "pro")

    # Free user: 5 requests per 60s
    for t in range(1, 6):
        assert trl.is_allowed("free_user", t) == True
    assert trl.is_allowed("free_user", 6) == False

    # Pro user: 20 requests per 60s
    for t in range(1, 21):
        assert trl.is_allowed("pro_user", t) == True
    assert trl.is_allowed("pro_user", 21) == False


if __name__ == "__main__":
    test_basic_rate_limiting()
    test_independent_users()
    test_window_expiration()
    test_get_remaining()
    test_tiered_rate_limiter()
    print("All tests passed!")
