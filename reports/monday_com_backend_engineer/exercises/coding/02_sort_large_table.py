"""
Exercise 2: Sort Table with Millions of Rows (Fractional Indexing)
===================================================================
Monday.com Backend Engineer Interview Question (Real)

PROBLEM:
    You are building a table view for Monday.com that can hold millions of rows.
    Users need to:
      1. Sort the entire table by a column (initial sort).
      2. Drag-and-drop any row to a new position (reorder).
      3. Query the current sorted order efficiently.

    The naive approach of storing integer positions (1, 2, 3, ...) requires
    updating ALL rows after the insertion point when a single row is moved.
    With millions of rows, this is unacceptable.

    Your task: implement a SortableTable class that uses FRACTIONAL INDEXING
    to achieve O(1) row moves and O(N log N) initial sort.

    Fractional indexing assigns each row a floating-point "sort_key". To insert
    a row between two neighbors, you compute the midpoint of their sort_keys.
    No other rows need updating.

    Example:
        Rows sorted: A(1.0), B(2.0), C(3.0)
        Move C between A and B -> C gets sort_key = 1.5
        New order: A(1.0), C(1.5), B(2.0)

    Handle the edge case where repeated bisection exhausts floating-point
    precision by implementing a rebalance operation.

CONSTRAINTS:
    - Initial sort: O(N log N)
    - Move a row: O(1) amortized (O(N) when rebalance triggers)
    - Get sorted order: O(N log N)
    - Space: O(N)

DIFFICULTY: Medium-Hard
"""

from typing import Any, Dict, List, Optional, Tuple


class Row:
    """Represents a single table row."""

    def __init__(self, row_id: str, data: Dict[str, Any]):
        self.row_id = row_id
        self.data = data
        self.sort_key: float = 0.0

    def __repr__(self) -> str:
        return f"Row({self.row_id}, sort_key={self.sort_key:.6f})"


class SortableTable:
    """A table supporting efficient sort, move, and query operations.

    Uses fractional indexing so that moving a single row does NOT require
    updating sort keys for all other rows.
    """

    # Minimum gap between sort keys before triggering rebalance
    MIN_GAP = 1e-10

    def __init__(self) -> None:
        # TODO: Initialize internal data structures
        # You need:
        #   - A way to look up a Row by its row_id in O(1)
        #   - A collection of all rows
        pass

    def add_row(self, row_id: str, data: Dict[str, Any]) -> Row:
        """Add a new row to the table. Assign it the largest sort_key + 1.

        Returns the created Row.
        """
        # TODO: Implement
        pass

    def sort_by_column(self, column: str, reverse: bool = False) -> None:
        """Sort all rows by the given column and reassign sort_keys.

        After sorting, sort_keys should be evenly spaced (e.g., 1.0, 2.0, 3.0, ...).
        This is the initial sort or a full re-sort.

        Time: O(N log N)
        """
        # TODO: Implement
        pass

    def move_row(self, row_id: str, after_id: Optional[str], before_id: Optional[str]) -> None:
        """Move a row to a new position between `after_id` and `before_id`.

        Cases:
          - after_id=None, before_id=X   -> move to the very beginning (before X)
          - after_id=X, before_id=None    -> move to the very end (after X)
          - after_id=X, before_id=Y       -> move between X and Y

        Assign a new sort_key that is the midpoint of the neighbors' sort_keys.
        If the gap is smaller than MIN_GAP, trigger a rebalance.

        Time: O(1) amortized
        """
        # TODO: Implement
        pass

    def get_sorted_rows(self) -> List[Row]:
        """Return all rows sorted by their current sort_key.

        Time: O(N log N)
        """
        # TODO: Implement
        pass

    def _rebalance(self) -> None:
        """Reassign sort_keys with even spacing (1.0, 2.0, 3.0, ...).

        Called when fractional keys get too close together.
        Time: O(N)
        """
        # TODO: Implement
        pass


# ---------------------------------------------------------------------------
# TESTS -- run with: pytest 02_sort_large_table.py -v
# ---------------------------------------------------------------------------
import pytest


class TestSortableTable:

    def _make_table(self) -> SortableTable:
        table = SortableTable()
        table.add_row("r1", {"name": "Charlie", "age": 30})
        table.add_row("r2", {"name": "Alice", "age": 25})
        table.add_row("r3", {"name": "Bob", "age": 35})
        table.add_row("r4", {"name": "Diana", "age": 28})
        table.add_row("r5", {"name": "Eve", "age": 22})
        return table

    def test_initial_sort_by_name(self):
        """Sort by name column should produce alphabetical order."""
        table = self._make_table()
        table.sort_by_column("name")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Alice", "Bob", "Charlie", "Diana", "Eve"]

    def test_sort_by_age_descending(self):
        """Sort by age descending."""
        table = self._make_table()
        table.sort_by_column("age", reverse=True)
        ages = [r.data["age"] for r in table.get_sorted_rows()]
        assert ages == [35, 30, 28, 25, 22]

    def test_move_row_to_beginning(self):
        """Move a row to the very beginning of the table."""
        table = self._make_table()
        table.sort_by_column("name")  # Alice, Bob, Charlie, Diana, Eve
        # Move Eve to the beginning (before Alice)
        table.move_row("r5", after_id=None, before_id="r2")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Eve", "Alice", "Bob", "Charlie", "Diana"]

    def test_move_row_to_end(self):
        """Move a row to the very end of the table."""
        table = self._make_table()
        table.sort_by_column("name")  # Alice, Bob, Charlie, Diana, Eve
        # Move Alice to the end (after Eve)
        table.move_row("r2", after_id="r5", before_id=None)
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Bob", "Charlie", "Diana", "Eve", "Alice"]

    def test_move_row_between_two(self):
        """Move a row between two other rows."""
        table = self._make_table()
        table.sort_by_column("name")  # Alice, Bob, Charlie, Diana, Eve
        # Move Eve between Alice and Bob
        table.move_row("r5", after_id="r2", before_id="r3")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Alice", "Eve", "Bob", "Charlie", "Diana"]

    def test_multiple_moves_preserve_order(self):
        """Multiple successive moves should all be reflected correctly."""
        table = self._make_table()
        table.sort_by_column("name")  # Alice, Bob, Charlie, Diana, Eve
        table.move_row("r5", after_id="r2", before_id="r3")  # Alice, Eve, Bob, Charlie, Diana
        table.move_row("r4", after_id=None, before_id="r2")  # Diana, Alice, Eve, Bob, Charlie
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Diana", "Alice", "Eve", "Bob", "Charlie"]

    def test_rebalance_after_many_moves(self):
        """After many moves to the same spot, rebalance should maintain order."""
        table = SortableTable()
        table.add_row("a", {"val": "A"})
        table.add_row("b", {"val": "B"})
        table.sort_by_column("val")  # A(1.0), B(2.0)

        # Keep inserting between A and the next item -- this will exhaust precision
        prev_id = "a"
        next_id = "b"
        for i in range(60):
            new_id = f"x{i}"
            table.add_row(new_id, {"val": f"X{i}"})
            table.move_row(new_id, after_id=prev_id, before_id=next_id)
            next_id = new_id  # next insertion goes between A and the latest

        # The table should still return a consistent sorted order
        rows = table.get_sorted_rows()
        keys = [r.sort_key for r in rows]
        # Sort keys must be strictly increasing
        for i in range(len(keys) - 1):
            assert keys[i] < keys[i + 1], f"Sort keys not strictly increasing at index {i}"


# Complexity targets:
# - sort_by_column: O(N log N) -- standard sort
# - move_row:       O(1) amortized -- just compute midpoint of two floats
# - get_sorted_rows: O(N log N) -- sort by sort_key
# - rebalance:      O(N) -- reassign evenly spaced keys

# HINT 1: In __init__, use a dict {row_id: Row} for O(1) lookups.
#          In add_row, set sort_key = current_max + 1.0 so new rows go to the end.

# HINT 2: In move_row, compute the new sort_key as the midpoint:
#          - Between two rows: (after.sort_key + before.sort_key) / 2
#          - At the beginning: before.sort_key - 1.0
#          - At the end: after.sort_key + 1.0
#          Then check if the gap is < MIN_GAP and rebalance if needed.

# HINT 3: In _rebalance, get_sorted_rows() then reassign sort_keys as 1.0, 2.0, 3.0, ...
#          This is O(N) and resets the spacing so future moves have room.
