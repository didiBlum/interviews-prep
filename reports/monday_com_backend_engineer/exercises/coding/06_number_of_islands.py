"""
Exercise 6: Number of Islands
===============================
Difficulty: Medium | LeetCode #200
Pattern: Graph/Grid BFS/DFS -- Monday.com's most common algorithm category

PROBLEM:
Given an m x n 2D grid of '1's (land) and '0's (water), count the number
of islands.

An island is surrounded by water and is formed by connecting adjacent land
cells horizontally or vertically. You may assume all four edges of the grid
are surrounded by water.

EXAMPLES:
    Input:
        grid = [
            ["1", "1", "1", "1", "0"],
            ["1", "1", "0", "1", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "0", "0", "0"]
        ]
    Output: 1

    Input:
        grid = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "1", "0", "0"],
            ["0", "0", "0", "1", "1"]
        ]
    Output: 3

CONSTRAINTS:
- m == grid.length
- n == grid[i].length
- 1 <= m, n <= 300
- grid[i][j] is '0' or '1'
"""

from collections import deque


def num_islands(grid: list[list[str]]) -> int:
    """
    Count the number of islands in the grid.

    An island is a group of '1's connected horizontally or vertically.

    Args:
        grid: 2D list of '0's and '1's

    Returns:
        Number of islands
    """
    # TODO: Implement using BFS or DFS
    # Strategy:
    #   1. Iterate through every cell in the grid
    #   2. When you find a '1' that hasn't been visited, it's a new island
    #   3. Use BFS/DFS to mark all connected '1's as visited
    #   4. Increment the island count
    pass


def num_islands_dfs(grid: list[list[str]]) -> int:
    """
    Alternative: Solve using DFS (recursive or iterative).

    Args:
        grid: 2D list of '0's and '1's

    Returns:
        Number of islands
    """
    # TODO: Implement using DFS approach
    pass


# ---------------------------------------------------------------------------
# Tests (run with: pytest 06_number_of_islands.py -v)
# ---------------------------------------------------------------------------
import pytest


class TestNumIslands:
    """Tests for the BFS implementation."""

    def test_single_large_island(self):
        """All connected land forms one island."""
        grid = [
            ["1", "1", "1", "1", "0"],
            ["1", "1", "0", "1", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "0", "0", "0"],
        ]
        assert num_islands(grid) == 1

    def test_three_islands(self):
        """Three separate land masses."""
        grid = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "1", "0", "0"],
            ["0", "0", "0", "1", "1"],
        ]
        assert num_islands(grid) == 3

    def test_all_water(self):
        """No land at all."""
        grid = [
            ["0", "0", "0"],
            ["0", "0", "0"],
            ["0", "0", "0"],
        ]
        assert num_islands(grid) == 0

    def test_all_land(self):
        """Entire grid is one island."""
        grid = [
            ["1", "1", "1"],
            ["1", "1", "1"],
            ["1", "1", "1"],
        ]
        assert num_islands(grid) == 1

    def test_single_cell_land(self):
        """Single cell grid with land."""
        grid = [["1"]]
        assert num_islands(grid) == 1

    def test_single_cell_water(self):
        """Single cell grid with water."""
        grid = [["0"]]
        assert num_islands(grid) == 0

    def test_diagonal_not_connected(self):
        """Diagonally adjacent cells are NOT connected."""
        grid = [
            ["1", "0", "1"],
            ["0", "1", "0"],
            ["1", "0", "1"],
        ]
        assert num_islands(grid) == 5

    def test_single_row(self):
        """Grid with a single row."""
        grid = [["1", "0", "1", "1", "0", "1"]]
        assert num_islands(grid) == 3

    def test_single_column(self):
        """Grid with a single column."""
        grid = [["1"], ["0"], ["1"], ["1"], ["0"]]
        assert num_islands(grid) == 2

    def test_checkerboard_pattern(self):
        """Alternating land and water."""
        grid = [
            ["1", "0", "1", "0"],
            ["0", "1", "0", "1"],
            ["1", "0", "1", "0"],
            ["0", "1", "0", "1"],
        ]
        assert num_islands(grid) == 8

    def test_l_shaped_island(self):
        """An L-shaped island should count as one."""
        grid = [
            ["1", "0", "0"],
            ["1", "0", "0"],
            ["1", "1", "1"],
        ]
        assert num_islands(grid) == 1


class TestNumIslandsDFS:
    """Tests for the DFS implementation."""

    def test_single_large_island_dfs(self):
        grid = [
            ["1", "1", "1", "1", "0"],
            ["1", "1", "0", "1", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "0", "0", "0"],
        ]
        assert num_islands_dfs(grid) == 1

    def test_three_islands_dfs(self):
        grid = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "1", "0", "0"],
            ["0", "0", "0", "1", "1"],
        ]
        assert num_islands_dfs(grid) == 3

    def test_all_water_dfs(self):
        grid = [["0", "0"], ["0", "0"]]
        assert num_islands_dfs(grid) == 0

    def test_diagonal_not_connected_dfs(self):
        grid = [
            ["1", "0", "1"],
            ["0", "1", "0"],
            ["1", "0", "1"],
        ]
        assert num_islands_dfs(grid) == 5

    def test_empty_grid_dfs(self):
        """Edge case: empty grid."""
        grid: list[list[str]] = []
        assert num_islands_dfs(grid) == 0


class TestEdgeCases:
    """Additional edge case tests for both implementations."""

    def test_empty_grid(self):
        """Empty grid should return 0."""
        assert num_islands([]) == 0

    def test_grid_does_not_mutate(self):
        """Ensure the grid is not mutated (uses separate visited tracking)."""
        grid = [
            ["1", "1", "0"],
            ["0", "1", "0"],
            ["0", "0", "1"],
        ]
        # Make a deep copy to compare after
        import copy
        original = copy.deepcopy(grid)
        num_islands(grid)
        assert grid == original, "The function should not mutate the input grid"


# ---------------------------------------------------------------------------
# HINTS (reveal progressively if stuck)
# ---------------------------------------------------------------------------

# HINT 1: Think of the grid as a graph. Each '1' cell is a node. Two nodes
#          are connected if they are horizontally or vertically adjacent and
#          both are '1'. "Number of islands" = "number of connected components."

# HINT 2: Use BFS or DFS starting from each unvisited '1'. When you start a
#          new traversal, increment the island count. During traversal, mark
#          cells as visited so you don't count them again. Use a visited set
#          (or mark cells as '0' in-place, though mutating input is debatable).

# HINT 3: For BFS, use a deque. For each cell, enqueue its 4 neighbors
#          (up, down, left, right) if they are in bounds, are '1', and haven't
#          been visited. The 4 directions can be encoded as:
#          directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# ---------------------------------------------------------------------------
# COMPLEXITY TARGETS
# ---------------------------------------------------------------------------
# Time:  O(m * n) where m = rows, n = cols -- visit each cell at most once
# Space: O(m * n) worst case for the visited set / BFS queue
#        (queue can hold all cells if entire grid is land)
