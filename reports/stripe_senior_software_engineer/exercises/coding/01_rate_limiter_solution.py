"""
Rate Limiter — Solution
=======================

Approach: Sliding window using a deque of timestamps per user.
- On each request, remove expired timestamps from the front of the deque.
- If count < max_requests, allow and append. Otherwise reject.

Time: O(1) amortized — each timestamp is added and removed exactly once.
Space: O(max_requests) per user — deque never exceeds the limit.
"""

from collections import deque


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: dict[str, deque[int]] = {}

    def _cleanup(self, user_id: str, timestamp: int):
        """Remove timestamps outside the current window."""
        if user_id not in self.user_requests:
            return
        dq = self.user_requests[user_id]
        cutoff = timestamp - self.window_seconds
        while dq and dq[0] < cutoff:
            dq.popleft()

    def is_allowed(self, user_id: str, timestamp: int) -> bool:
        self._cleanup(user_id, timestamp)
        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(timestamp)
            return True
        return False

    def get_remaining(self, user_id: str, timestamp: int) -> int:
        self._cleanup(user_id, timestamp)
        current = len(self.user_requests.get(user_id, deque()))
        return max(0, self.max_requests - current)


class TieredRateLimiter:
    TIER_LIMITS = {
        "free": (5, 60),
        "pro": (20, 60),
        "enterprise": (100, 60),
    }

    def __init__(self):
        self.user_tiers: dict[str, str] = {}
        self.user_requests: dict[str, deque[int]] = {}

    def set_tier(self, user_id: str, tier: str) -> None:
        if tier not in self.TIER_LIMITS:
            raise ValueError(f"Unknown tier: {tier}")
        self.user_tiers[user_id] = tier

    def _get_limits(self, user_id: str) -> tuple[int, int]:
        tier = self.user_tiers.get(user_id, "free")
        return self.TIER_LIMITS[tier]

    def is_allowed(self, user_id: str, timestamp: int) -> bool:
        max_requests, window = self._get_limits(user_id)

        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        dq = self.user_requests[user_id]
        cutoff = timestamp - window
        while dq and dq[0] <= cutoff:
            dq.popleft()

        if len(dq) < max_requests:
            dq.append(timestamp)
            return True
        return False


# ============ Complexity Analysis ============
# Time: O(1) amortized per is_allowed call
#   - Each timestamp enters the deque once and leaves once
#   - Cleanup is amortized across all calls
# Space: O(U * N) where U = users, N = max_requests per user
#   - Deque never exceeds max_requests entries per user

# ============ Common Interviewer Follow-ups ============
# Q: "What if timestamps aren't monotonically increasing?"
# A: Need to sort or use a different data structure (sorted list).
#    Could use a sorted container, but at the cost of O(log N) insertion.
#
# Q: "How would you handle this in a distributed system?"
# A: Use Redis with sorted sets (ZRANGEBYSCORE for cleanup, ZADD for insert).
#    Or use a token bucket algorithm which is more cache-friendly.
#
# Q: "What about memory for millions of users?"
# A: Evict inactive users periodically. Use TTL on Redis keys.
#    Consider approximate algorithms (token bucket uses fixed memory per user).

# ============ What Interviewers Look For ============
# 1. Choosing the right data structure (deque for O(1) popleft)
# 2. Handling the window boundary correctly (> vs >=)
# 3. Not recording rejected requests (common mistake)
# 4. Clean API design with separation of concerns
# 5. Discussing trade-offs: exact vs approximate, memory vs accuracy

# ============ Alternative Approaches ============
# 1. Token Bucket: Fixed memory per user, but approximate.
#    Refill tokens at a fixed rate. Simpler but less precise.
#    Trade-off: O(1) time and space, but allows brief bursts.
#
# 2. Fixed Window Counter: Simple counter per time window.
#    Trade-off: Boundary problem (2x burst at window edges).
#
# 3. Sliding Window Counter: Weighted combination of current + previous window.
#    Trade-off: Approximate but very memory-efficient.


# ============ TESTS ============

def test_basic_rate_limiting():
    rl = RateLimiter(max_requests=3, window_seconds=10)
    assert rl.is_allowed("user1", 1) == True
    assert rl.is_allowed("user1", 2) == True
    assert rl.is_allowed("user1", 3) == True
    assert rl.is_allowed("user1", 4) == False
    assert rl.is_allowed("user1", 11) == False
    assert rl.is_allowed("user1", 12) == True

def test_independent_users():
    rl = RateLimiter(max_requests=2, window_seconds=5)
    assert rl.is_allowed("alice", 1) == True
    assert rl.is_allowed("bob", 1) == True
    assert rl.is_allowed("alice", 2) == True
    assert rl.is_allowed("alice", 3) == False
    assert rl.is_allowed("bob", 3) == True

def test_window_expiration():
    rl = RateLimiter(max_requests=1, window_seconds=5)
    assert rl.is_allowed("user1", 1) == True
    assert rl.is_allowed("user1", 5) == False
    assert rl.is_allowed("user1", 6) == True

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

    for t in range(1, 6):
        assert trl.is_allowed("free_user", t) == True
    assert trl.is_allowed("free_user", 6) == False

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
