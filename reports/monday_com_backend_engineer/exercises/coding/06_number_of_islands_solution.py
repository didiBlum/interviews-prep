"""
Exercise 6: Number of Islands - SOLUTION
==========================================
Difficulty: Medium | LeetCode #200
Pattern: Graph/Grid BFS/DFS -- Monday.com's most common algorithm category

Time Complexity:  O(m * n)
Space Complexity: O(m * n)
"""

from collections import deque


def num_islands(grid: list[list[str]]) -> int:
    """
    Count islands using BFS.

    Strategy: Treat the grid as a graph. Each '1' cell is a node connected
    to its horizontal/vertical neighbors. Count connected components by
    running BFS from each unvisited '1'.

    We use a separate visited set to avoid mutating the input grid.
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    count = 0

    # 4-directional movement: right, left, down, up
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def bfs(start_r: int, start_c: int) -> None:
        """Flood-fill from (start_r, start_c), marking all connected land as visited."""
        queue = deque([(start_r, start_c)])
        visited.add((start_r, start_c))

        while queue:
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                # Check bounds, land, and not visited
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and grid[nr][nc] == "1"
                    and (nr, nc) not in visited
                ):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    # Main loop: scan every cell
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                # Found a new island -- BFS to mark all its cells
                bfs(r, c)
                count += 1

    return count


def num_islands_dfs(grid: list[list[str]]) -> int:
    """
    Count islands using iterative DFS (stack-based).

    Iterative DFS avoids Python's recursion limit (default 1000), which
    matters for large grids (up to 300x300 = 90,000 cells).
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    count = 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def dfs(start_r: int, start_c: int) -> None:
        """Iterative DFS flood-fill."""
        stack = [(start_r, start_c)]
        visited.add((start_r, start_c))

        while stack:
            r, c = stack.pop()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and grid[nr][nc] == "1"
                    and (nr, nc) not in visited
                ):
                    visited.add((nr, nc))
                    stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                dfs(r, c)
                count += 1

    return count


# ---------------------------------------------------------------------------
# Alternative: Union-Find (Disjoint Set Union) approach
# ---------------------------------------------------------------------------
class UnionFind:
    """
    Union-Find with path compression and union by rank.

    This is an alternative approach that some interviewers prefer because
    it demonstrates knowledge of a more advanced data structure.
    """

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = 0  # Number of distinct components

    def find(self, x: int) -> int:
        """Find with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        """Union by rank."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        # Attach smaller tree under larger tree
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1  # Two components merged into one


def num_islands_union_find(grid: list[list[str]]) -> int:
    """
    Count islands using Union-Find.

    Time:  O(m * n * alpha(m * n)) which is effectively O(m * n)
    Space: O(m * n)
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    uf = UnionFind(rows * cols)

    # Initialize: count all land cells as separate islands
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                uf.count += 1

    # Merge adjacent land cells
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                idx = r * cols + c
                # Only check right and down to avoid double-processing
                if c + 1 < cols and grid[r][c + 1] == "1":
                    uf.union(idx, idx + 1)
                if r + 1 < rows and grid[r + 1][c] == "1":
                    uf.union(idx, idx + cols)

    return uf.count


# ---------------------------------------------------------------------------
# COMPLEXITY ANALYSIS
# ---------------------------------------------------------------------------
#
# BFS / DFS approach:
#   Time:  O(m * n) -- each cell is visited at most once
#   Space: O(m * n) -- visited set stores all land cells; BFS queue can hold
#          up to m * n cells in worst case (entire grid is land)
#
# Union-Find approach:
#   Time:  O(m * n * alpha(m * n)) ~ O(m * n) -- inverse Ackermann is
#          practically constant
#   Space: O(m * n) for parent and rank arrays
#
# In-place mutation approach (not shown):
#   Time:  O(m * n)
#   Space: O(min(m, n)) for the BFS queue -- this is the optimal space approach
#          but mutates the input, which is a tradeoff to discuss
#
# ---------------------------------------------------------------------------
# WHAT INTERVIEWERS LOOK FOR
# ---------------------------------------------------------------------------
#
# 1. GRAPH MODELING: Recognizing that "connected components on a grid" is a
#    graph problem. The grid is the adjacency structure itself.
#
# 2. BFS vs DFS CHOICE: Both work. BFS with a deque is slightly preferred
#    because it avoids recursion depth issues. But explain your choice --
#    interviewers want to hear you reason about tradeoffs.
#
# 3. VISITED TRACKING: Using a set vs mutating the grid. Discuss tradeoffs:
#    - Set: clean, doesn't mutate input, extra O(m*n) space
#    - Mutation: no extra space, but destroys the input (bad in production)
#    - Interview tip: ask the interviewer "Can I modify the grid?"
#
# 4. BOUNDARY CHECKS: Clean handling of grid edges. The directions array
#    pattern (dr, dc) is cleaner than 4 separate if-statements.
#
# 5. EMPTY INPUT: Handling empty grid, single cell, single row/column.
#    Check for these edge cases early.
#
# ---------------------------------------------------------------------------
# COMMON INTERVIEWER FOLLOW-UPS
# ---------------------------------------------------------------------------
#
# Q: "What if we need to count the size of each island?"
# A: During BFS/DFS, count how many cells are visited. Return a list of sizes
#    or map island_id -> size. Trivial modification.
#
# Q: "What if islands can connect diagonally?"
# A: Change directions from 4 to 8:
#    directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
#    Everything else stays the same.
#
# Q: "What if the grid is too large to fit in memory?"
# A: Process the grid row by row (streaming). Use Union-Find on the current
#    row and the previous row. This reduces memory to O(n) for a single row.
#    This is relevant at Monday.com's scale for large data processing.
#
# Q: "What if the grid changes dynamically (land appears/disappears)?"
# A: Union-Find is better for this. Adding land: create new component, union
#    with neighbors. Removing land: harder -- Union-Find doesn't support
#    efficient splits. May need to rebuild or use a link-cut tree.
#
# Q: "How would you parallelize this?"
# A: Divide the grid into blocks. Process each block independently to find
#    local islands. Then merge islands that span block boundaries using
#    Union-Find. This is a real distributed computing pattern.
#
# Q: "What if the grid wraps around (torus topology)?"
# A: Adjust neighbor calculation to use modular arithmetic:
#    nr = (r + dr) % rows, nc = (c + dc) % cols
#    The algorithm structure stays the same.
#
# ---------------------------------------------------------------------------
# ALTERNATIVE APPROACHES WITH TRADEOFFS
# ---------------------------------------------------------------------------
#
# 1. BFS (shown above):
#    + No recursion depth issues
#    + Familiar to most developers
#    - Queue can grow large (O(min(m,n)) in practice for grid BFS)
#
# 2. Iterative DFS (shown above):
#    + No recursion depth issues
#    + Stack typically smaller than BFS queue for grid problems
#    - Traversal order less intuitive than BFS
#
# 3. Recursive DFS (not shown, but common in interviews):
#    + Most concise code (5-6 lines for the DFS function)
#    - Python recursion limit: max 1000 by default, grid can be 300*300=90000
#    - Stack overflow risk in production
#    - Interviewers may dock points if you don't mention the recursion limit
#
# 4. Union-Find (shown above):
#    + Better for dynamic grids (adding/removing land)
#    + Generalizes well to higher dimensions
#    + Shows advanced data structure knowledge
#    - More code than BFS/DFS
#    - Slightly harder to explain
#    - No practical speed advantage for static grids
#
# 5. In-place mutation (not shown):
#    + O(1) extra space (just the queue/stack)
#    + Fastest in practice (no hash set overhead)
#    - Destroys the input -- unacceptable in most production code
#    - Ask the interviewer before using this approach
