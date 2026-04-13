"""
Solution: Sort Table with Millions of Rows (Fractional Indexing)
================================================================
Monday.com Backend Engineer Interview Question (Real)

Complexity Analysis:
    sort_by_column:  O(N log N) -- standard sort + O(N) key assignment
    move_row:        O(1) amortized -- midpoint computation; O(N) on rebalance
    get_sorted_rows: O(N log N) -- sort all rows by sort_key
    rebalance:       O(N) -- linear scan to reassign keys
    Space:           O(N) -- one sort_key per row + dict lookup

Key Insight:
    Fractional indexing avoids the "shift all positions" problem. Instead of
    storing integer positions (1, 2, 3, ...) and renumbering on every move,
    we assign floating-point sort_keys. Moving a row between two neighbors
    just takes the average of their keys. No other rows are touched.

    This is exactly how Monday.com, Notion, Linear, and similar tools handle
    drag-and-drop reordering in databases. In production, string-based
    fractional indices (e.g., the "fractional-indexing" npm package) are used
    instead of floats to avoid precision limits entirely.
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
    """A table supporting efficient sort, move, and query operations
    using fractional indexing."""

    MIN_GAP = 1e-10

    def __init__(self) -> None:
        # O(1) lookup by row_id
        self._rows: Dict[str, Row] = {}
        # Track the maximum sort_key for appending new rows
        self._max_key: float = 0.0

    def add_row(self, row_id: str, data: Dict[str, Any]) -> Row:
        """Add a new row. Assign it sort_key = max + 1 so it appears at the end."""
        row = Row(row_id, data)
        self._max_key += 1.0
        row.sort_key = self._max_key
        self._rows[row_id] = row
        return row

    def sort_by_column(self, column: str, reverse: bool = False) -> None:
        """Sort all rows by the given column and reassign evenly-spaced sort_keys.

        This is a full re-sort. After this, sort_keys are 1.0, 2.0, 3.0, ...
        which gives maximum room for future fractional insertions.
        """
        # Sort rows by the column value
        sorted_rows = sorted(
            self._rows.values(),
            key=lambda r: r.data[column],
            reverse=reverse,
        )
        # Reassign evenly spaced sort_keys
        for i, row in enumerate(sorted_rows, start=1):
            row.sort_key = float(i)
        self._max_key = float(len(sorted_rows))

    def move_row(self, row_id: str, after_id: Optional[str], before_id: Optional[str]) -> None:
        """Move a row to a new position using fractional indexing.

        Computes the midpoint of the neighbors' sort_keys. If precision is
        exhausted (gap < MIN_GAP), triggers a full rebalance.
        """
        row = self._rows[row_id]

        if after_id is None and before_id is not None:
            # Move to the very beginning -- place before the 'before' row
            before_row = self._rows[before_id]
            row.sort_key = before_row.sort_key - 1.0
        elif after_id is not None and before_id is None:
            # Move to the very end -- place after the 'after' row
            after_row = self._rows[after_id]
            row.sort_key = after_row.sort_key + 1.0
            self._max_key = max(self._max_key, row.sort_key)
        elif after_id is not None and before_id is not None:
            # Move between two rows -- take the midpoint
            after_row = self._rows[after_id]
            before_row = self._rows[before_id]
            new_key = (after_row.sort_key + before_row.sort_key) / 2.0
            row.sort_key = new_key

            # Check if we've exhausted floating-point precision
            gap = min(
                abs(new_key - after_row.sort_key),
                abs(before_row.sort_key - new_key),
            )
            if gap < self.MIN_GAP:
                self._rebalance()

    def get_sorted_rows(self) -> List[Row]:
        """Return all rows sorted by their current sort_key."""
        return sorted(self._rows.values(), key=lambda r: r.sort_key)

    def _rebalance(self) -> None:
        """Reassign sort_keys with even spacing to restore precision headroom.

        This is O(N) and is called rarely -- only when repeated insertions
        at the same position exhaust the floating-point gap.
        """
        sorted_rows = self.get_sorted_rows()
        for i, row in enumerate(sorted_rows, start=1):
            row.sort_key = float(i)
        self._max_key = float(len(sorted_rows))


# ---------------------------------------------------------------------------
# TESTS
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
        table = self._make_table()
        table.sort_by_column("name")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Alice", "Bob", "Charlie", "Diana", "Eve"]

    def test_sort_by_age_descending(self):
        table = self._make_table()
        table.sort_by_column("age", reverse=True)
        ages = [r.data["age"] for r in table.get_sorted_rows()]
        assert ages == [35, 30, 28, 25, 22]

    def test_move_row_to_beginning(self):
        table = self._make_table()
        table.sort_by_column("name")
        table.move_row("r5", after_id=None, before_id="r2")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Eve", "Alice", "Bob", "Charlie", "Diana"]

    def test_move_row_to_end(self):
        table = self._make_table()
        table.sort_by_column("name")
        table.move_row("r2", after_id="r5", before_id=None)
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Bob", "Charlie", "Diana", "Eve", "Alice"]

    def test_move_row_between_two(self):
        table = self._make_table()
        table.sort_by_column("name")
        table.move_row("r5", after_id="r2", before_id="r3")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Alice", "Eve", "Bob", "Charlie", "Diana"]

    def test_multiple_moves_preserve_order(self):
        table = self._make_table()
        table.sort_by_column("name")
        table.move_row("r5", after_id="r2", before_id="r3")
        table.move_row("r4", after_id=None, before_id="r2")
        names = [r.data["name"] for r in table.get_sorted_rows()]
        assert names == ["Diana", "Alice", "Eve", "Bob", "Charlie"]

    def test_rebalance_after_many_moves(self):
        table = SortableTable()
        table.add_row("a", {"val": "A"})
        table.add_row("b", {"val": "B"})
        table.sort_by_column("val")

        prev_id = "a"
        next_id = "b"
        for i in range(60):
            new_id = f"x{i}"
            table.add_row(new_id, {"val": f"X{i}"})
            table.move_row(new_id, after_id=prev_id, before_id=next_id)
            next_id = new_id

        rows = table.get_sorted_rows()
        keys = [r.sort_key for r in rows]
        for i in range(len(keys) - 1):
            assert keys[i] < keys[i + 1], f"Sort keys not strictly increasing at index {i}"


# ---------------------------------------------------------------------------
# COMMON INTERVIEWER FOLLOW-UPS:
#
# 1. "What happens when floating-point precision runs out?"
#    -> After ~52 bisections (IEEE 754 doubles), the gap between adjacent
#       keys becomes zero. We detect this and trigger _rebalance() which
#       reassigns evenly-spaced integer keys. This makes it O(N) worst case
#       but amortized O(1) per move.
#
# 2. "How would you avoid even the O(N) rebalance?"
#    -> Use string-based fractional indices (e.g., base-62 strings). The
#       midpoint is computed by interleaving characters. Strings have
#       unbounded precision so rebalancing is never needed. Libraries:
#       "fractional-indexing" (JS), or implement with base-256 byte arrays.
#
# 3. "How does this work in a database?"
#    -> Store sort_key as a column with a B-tree index. Queries like
#       ORDER BY sort_key are O(N log N) via the index. Updates to a single
#       row's sort_key are O(log N). The database never needs to update
#       other rows.
#
# 4. "What about concurrent moves by multiple users?"
#    -> Conflicts are rare since each move only modifies one row's sort_key.
#       If two users move different rows simultaneously, there is no conflict.
#       If they move the same row, last-write-wins or use CRDTs for
#       conflict resolution.
#
# 5. "Why not use a linked list?"
#    -> Linked lists require O(N) to find the k-th element and don't map well
#       to SQL databases. Fractional indexing works naturally with ORDER BY
#       and is compatible with pagination (OFFSET/LIMIT or cursor-based).
#
# ---------------------------------------------------------------------------
# ALTERNATIVE APPROACHES:
#
# A) Integer positions with gap (e.g., positions: 1000, 2000, 3000)
#    - Insert between 1000 and 2000 -> position 1500
#    - Pro: Integers avoid floating-point issues
#    - Con: Still need rebalancing; gap exhaustion with 32-bit ints
#
# B) Balanced BST (e.g., order-statistic tree)
#    - O(log N) insert, delete, rank queries
#    - Pro: No rebalancing needed
#    - Con: Complex to implement; doesn't map to SQL ORDER BY
#
# C) Array with shift-on-insert (naive)
#    - O(N) per move since all subsequent positions must update
#    - Pro: Simple
#    - Con: Unacceptable for millions of rows -- this is the approach the
#           interviewer wants you to improve upon
#
# ---------------------------------------------------------------------------
# WHAT INTERVIEWERS LOOK FOR:
#
# - Recognition that naive integer positions are O(N) per move
# - The "aha" insight of fractional indexing (midpoint between neighbors)
# - Awareness of precision limits and the need for rebalancing
# - Clean OOP design with clear method responsibilities
# - Discussion of how this maps to real database operations
# - Knowledge of Monday.com's actual drag-and-drop reordering use case
# ---------------------------------------------------------------------------
