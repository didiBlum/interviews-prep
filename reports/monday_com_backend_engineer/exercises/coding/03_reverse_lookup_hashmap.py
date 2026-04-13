"""
Exercise 3: Reverse Lookup HashMap (BiDirectionalMap)
=====================================================
Monday.com Backend Engineer Interview Question (Real)

PROBLEM:
    Implement a BiDirectionalMap that supports O(1) lookups in BOTH directions:
      - Forward:  key -> value   (like a normal dict)
      - Reverse:  value -> key   (reverse lookup)

    The map must handle:
      - put(key, value): Insert or update a key-value pair.
      - get(key): Get the value for a key (forward lookup).
      - get_key(value): Get the key for a value (reverse lookup).
      - delete(key): Remove a key-value pair by key.
      - delete_value(value): Remove a key-value pair by value.
      - __len__: Return the number of entries.
      - __contains__: Support `key in bimap` syntax.

    IMPORTANT EDGE CASES:
      - When a key is updated with a new value, the old reverse mapping must be
        removed and the new one added.
      - When a new key is assigned a value that already exists for another key,
        the old key must be evicted (values must be unique in a bidirectional map).
      - Deletions must clean up both forward and reverse mappings.

CONSTRAINTS:
    - All operations: O(1) average time
    - Space: O(N) where N = number of entries
    - Values must be unique (one-to-one mapping)

DIFFICULTY: Medium
"""

from typing import Any, Optional


class BiDirectionalMap:
    """A bidirectional (one-to-one) map with O(1) forward and reverse lookups."""

    def __init__(self) -> None:
        # TODO: Initialize data structures for forward and reverse lookups
        pass

    def put(self, key: Any, value: Any) -> None:
        """Insert or update a key-value pair.

        If the key already exists, update its value (remove old reverse mapping).
        If the value already belongs to a different key, evict that old key.

        Time: O(1)
        """
        # TODO: Implement
        pass

    def get(self, key: Any) -> Optional[Any]:
        """Forward lookup: return the value for the given key, or None.

        Time: O(1)
        """
        # TODO: Implement
        pass

    def get_key(self, value: Any) -> Optional[Any]:
        """Reverse lookup: return the key for the given value, or None.

        Time: O(1)
        """
        # TODO: Implement
        pass

    def delete(self, key: Any) -> bool:
        """Delete a mapping by key. Returns True if the key existed.

        Must clean up both forward and reverse mappings.

        Time: O(1)
        """
        # TODO: Implement
        pass

    def delete_value(self, value: Any) -> bool:
        """Delete a mapping by value. Returns True if the value existed.

        Must clean up both forward and reverse mappings.

        Time: O(1)
        """
        # TODO: Implement
        pass

    def __len__(self) -> int:
        """Return the number of key-value pairs."""
        # TODO: Implement
        pass

    def __contains__(self, key: Any) -> bool:
        """Support `key in bimap` syntax (checks forward map)."""
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# TESTS -- run with: pytest 03_reverse_lookup_hashmap.py -v
# ---------------------------------------------------------------------------
import pytest


class TestBiDirectionalMap:

    def test_basic_put_and_get(self):
        """Basic forward and reverse lookups."""
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("b", 2)
        bm.put("c", 3)
        assert bm.get("a") == 1
        assert bm.get("b") == 2
        assert bm.get_key(1) == "a"
        assert bm.get_key(3) == "c"

    def test_update_existing_key(self):
        """Updating a key's value should remove the old reverse mapping."""
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("a", 2)  # Update: a now maps to 2 instead of 1
        assert bm.get("a") == 2
        assert bm.get_key(2) == "a"
        assert bm.get_key(1) is None  # Old reverse mapping removed
        assert len(bm) == 1

    def test_value_collision_evicts_old_key(self):
        """Assigning a value that belongs to another key should evict the old key."""
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("b", 1)  # Value 1 was owned by "a", now reassigned to "b"
        assert bm.get("b") == 1
        assert bm.get_key(1) == "b"
        assert bm.get("a") is None  # "a" was evicted
        assert len(bm) == 1

    def test_delete_by_key(self):
        """Delete by key should remove both forward and reverse mappings."""
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("b", 2)
        assert bm.delete("a") is True
        assert bm.get("a") is None
        assert bm.get_key(1) is None
        assert len(bm) == 1
        assert bm.delete("nonexistent") is False

    def test_delete_by_value(self):
        """Delete by value should remove both forward and reverse mappings."""
        bm = BiDirectionalMap()
        bm.put("x", 100)
        bm.put("y", 200)
        assert bm.delete_value(100) is True
        assert bm.get("x") is None
        assert bm.get_key(100) is None
        assert len(bm) == 1
        assert bm.delete_value(999) is False

    def test_contains(self):
        """The 'in' operator should check the forward map."""
        bm = BiDirectionalMap()
        bm.put("a", 1)
        assert "a" in bm
        assert "z" not in bm

    def test_get_nonexistent(self):
        """Getting a nonexistent key/value should return None."""
        bm = BiDirectionalMap()
        assert bm.get("nothing") is None
        assert bm.get_key("nothing") is None

    def test_put_same_key_same_value(self):
        """Putting the same key-value pair again should be a no-op."""
        bm = BiDirectionalMap()
        bm.put("a", 1)
        bm.put("a", 1)  # Same pair
        assert bm.get("a") == 1
        assert bm.get_key(1) == "a"
        assert len(bm) == 1

    def test_complex_sequence(self):
        """A complex sequence of operations to test consistency."""
        bm = BiDirectionalMap()
        bm.put("user_1", "alice@example.com")
        bm.put("user_2", "bob@example.com")
        bm.put("user_3", "charlie@example.com")

        # Reassign alice's email to user_3 (evicts user_1)
        bm.put("user_3", "alice@example.com")
        assert bm.get("user_1") is None  # evicted
        assert bm.get("user_3") == "alice@example.com"
        assert bm.get_key("alice@example.com") == "user_3"
        assert bm.get_key("charlie@example.com") is None  # overwritten
        assert len(bm) == 2  # user_2 and user_3


# Complexity targets:
# Time:  O(1) average for all operations (put, get, get_key, delete, delete_value)
# Space: O(N) where N = number of key-value pairs (two dicts of size N)

# HINT 1: Maintain TWO dictionaries: one for forward (key->value) and one for
#          reverse (value->key). Keep them in sync on every operation.

# HINT 2: In put(key, value), handle three cases before inserting:
#          (a) If key already exists with a different value, remove the old value
#              from the reverse dict.
#          (b) If value already exists with a different key, remove that old key
#              from the forward dict.
#          (c) Then insert into both dicts.

# HINT 3: In delete(key), first look up the value via forward dict, then remove
#          from both dicts. delete_value is the mirror: look up the key via
#          reverse dict, then remove from both.
