"""
Solution: Reverse Lookup HashMap (BiDirectionalMap)
====================================================
Monday.com Backend Engineer Interview Question (Real)

Complexity Analysis:
    Time:  O(1) average for all operations (put, get, get_key, delete, delete_value)
    Space: O(N) where N = number of entries. Two dicts of size N each -> O(2N) = O(N).

Approach:
    Maintain two synchronized dictionaries:
      - _forward: key -> value  (standard dict)
      - _reverse: value -> key  (inverted dict)

    Every mutation (put, delete) must update BOTH dicts to keep them consistent.
    The tricky part is handling the edge cases in put():
      - Updating an existing key: must remove the old value from _reverse.
      - Value collision: must evict the old key from _forward.
"""

from typing import Any, Optional


class BiDirectionalMap:
    """A bidirectional (one-to-one) map with O(1) forward and reverse lookups."""

    def __init__(self) -> None:
        self._forward: dict = {}  # key -> value
        self._reverse: dict = {}  # value -> key

    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair.

        Handles three edge cases:
        1. Key exists with a different value -> remove old reverse mapping
        2. Value exists with a different key -> evict old key (forward mapping)
        3. Same key-value pair already exists -> no-op
        """
        # Case 1: If this key already maps to a different value, clean up old reverse
        if key in self._forward:
            old_value = self._forward[key]
            if old_value != value:
                del self._reverse[old_value]

        # Case 2: If this value already belongs to a different key, evict that key
        if value in self._reverse:
            old_key = self._reverse[value]
            if old_key != key:
                del self._forward[old_key]

        # Now insert into both maps
        self._forward[key] = value
        self._reverse[value] = key

    def get(self, key: Any) -> Optional[Any]:
        """Forward lookup: key -> value. Returns None if key not found."""
        return self._forward.get(key)

    def get_key(self, value: Any) -> Optional[Any]:
        """Reverse lookup: value -> key. Returns None if value not found."""
        return self._reverse.get(value)

    def delete(self, key: Any) -> bool:
        """Delete by key. Cleans up both forward and reverse mappings."""
        if key not in self._forward:
            return False
        value = self._forward.pop(key)
        del self._reverse[value]
        return True

    def delete_value(self, value: Any) -> bool:
        """Delete by value. Cleans up both forward and reverse mappings."""
        if value not in self._reverse:
            return False
        key = self._reverse.pop(value)
        del self._forward[key]
        return True

    def __len__(self) -> int:
        return len(self._forward)

    def __contains__(self, key: Any) -> bool:
        return key in self._forward

    def __repr__(self) -> str:
        return f"BiDirectionalMap({self._forward})"


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------
import pytest


class TestBiDirectionalMap:

    def test_basic_put_and_get(self):
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("b", 2)
        bm.put("c", 3)
        assert bm.get("a") == 1
        assert bm.get("b") == 2
        assert bm.get_key(1) == "a"
        assert bm.get_key(3) == "c"

    def test_update_existing_key(self):
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("a", 2)
        assert bm.get("a") == 2
        assert bm.get_key(2) == "a"
        assert bm.get_key(1) is None
        assert len(bm) == 1

    def test_value_collision_evicts_old_key(self):
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("b", 1)
        assert bm.get("b") == 1
        assert bm.get_key(1) == "b"
        assert bm.get("a") is None
        assert len(bm) == 1

    def test_delete_by_key(self):
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("b", 2)
        assert bm.delete("a") is True
        assert bm.get("a") is None
        assert bm.get_key(1) is None
        assert len(bm) == 1
        assert bm.delete("nonexistent") is False

    def test_delete_by_value(self):
        bm = BiDirectionalMap()
        bm.put("x", 100)
        bm.put("y", 200)
        assert bm.delete_value(100) is True
        assert bm.get("x") is None
        assert bm.get_key(100) is None
        assert len(bm) == 1
        assert bm.delete_value(999) is False

    def test_contains(self):
        bm = BiDirectionalMap()
        bm.put("a", 1)
        assert "a" in bm
        assert "z" not in bm

    def test_get_nonexistent(self):
        bm = BiDirectionalMap()
        assert bm.get("nothing") is None
        assert bm.get_key("nothing") is None

    def test_put_same_key_same_value(self):
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("a", 1)
        assert bm.get("a") == 1
        assert bm.get_key(1) == "a"
        assert len(bm) == 1

    def test_complex_sequence(self):
        bm = BiDirectionalMap()
        bm.put("user_1", "alice@example.com")
        bm.put("user_2", "bob@example.com")
        bm.put("user_3", "charlie@example.com")
        bm.put("user_3", "alice@example.com")
        assert bm.get("user_1") is None
        assert bm.get("user_3") == "alice@example.com"
        assert bm.get_key("alice@example.com") == "user_3"
        assert bm.get_key("charlie@example.com") is None
        assert len(bm) == 2


# ---------------------------------------------------------------------------
# COMMON INTERVIEWER FOLLOW-UPS:
#
# 1. "What if values are NOT unique (many-to-one, like a regular dict)?"
#    -> The reverse map becomes value -> set(keys). get_key returns a set.
#       put() appends to the set; delete() removes from the set.
#       This changes reverse lookup from O(1) to O(1) for "get any key"
#       or O(K) for "get all keys" where K = number of keys with that value.
#
# 2. "How would you make this thread-safe?"
#    -> Wrap mutations in a threading.Lock or use a ReadWriteLock for
#       concurrent reads. Alternatively, use an immutable/persistent data
#       structure for lock-free reads.
#
# 3. "What about memory efficiency?"
#    -> Two full dicts doubles memory. If values are large objects, store
#       references (both dicts point to the same object). For extreme cases,
#       consider a single sorted structure with two index views.
#
# 4. "Can you implement iteration?"
#    -> Add __iter__ that yields (key, value) tuples from _forward.
#       Add items(), keys(), values() methods mirroring dict API.
#
# 5. "What about hashability requirements?"
#    -> Both keys AND values must be hashable (since values are dict keys
#       in _reverse). This means lists, dicts, sets cannot be values.
#       Document this constraint clearly.
#
# ---------------------------------------------------------------------------
# ALTERNATIVE APPROACHES:
#
# A) Single dict + linear scan for reverse lookup
#    - Forward: O(1), Reverse: O(N)
#    - Pro: Half the memory
#    - Con: Unacceptable for large N -- defeats the purpose
#
# B) Sorted list with binary search
#    - Forward: O(log N), Reverse: O(log N)
#    - Pro: Memory efficient, supports range queries
#    - Con: O(N) insertion/deletion due to shifting
#
# C) Two dicts (this solution)
#    - Forward: O(1), Reverse: O(1)
#    - Pro: Optimal time complexity
#    - Con: 2x memory; values must be hashable
#    - This is the expected answer in an interview
#
# ---------------------------------------------------------------------------
# WHAT INTERVIEWERS LOOK FOR:
#
# - Immediately recognizing that two synchronized dicts solve the problem
# - Careful handling of the update edge case (key exists with different value)
# - Careful handling of the collision edge case (value exists for different key)
# - Clean, Pythonic code (use of .get(), .pop(), __contains__, __len__)
# - Awareness of the hashability constraint on values
# - Discussion of thread safety if prompted
# - Good test coverage including edge cases
# ---------------------------------------------------------------------------
