/**
 * Number of Islands — Solution
 * ============================
 *
 * Approach: DFS flood fill
 * - Scan grid for unvisited '1'
 * - DFS to mark entire island as '0' (visited)
 * - Count number of DFS initiations
 *
 * Complexity:
 *   - Time: O(m * n) — each cell visited at most once
 *   - Space: O(m * n) worst case for DFS stack (long snake-like island)
 */

public class NumberOfIslandsSolution {

    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) return 0;

        int rows = grid.length;
        int cols = grid[0].length;
        int count = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] == '1') {
                    count++;
                    dfs(grid, r, c, rows, cols);
                }
            }
        }

        return count;
    }

    private void dfs(char[][] grid, int r, int c, int rows, int cols) {
        if (r < 0 || r >= rows || c < 0 || c >= cols || grid[r][c] != '1') {
            return;
        }

        grid[r][c] = '0'; // mark visited

        dfs(grid, r + 1, c, rows, cols);
        dfs(grid, r - 1, c, rows, cols);
        dfs(grid, r, c + 1, rows, cols);
        dfs(grid, r, c - 1, rows, cols);
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. CLEAN BOUNDARY CHECK: Checking bounds at the start of DFS (guard clause)
     *    is cleaner than checking before each recursive call.
     *
     * 2. MUTATION vs VISITED SET: Modifying the grid in-place avoids extra space.
     *    If the interviewer says "don't modify input", use a boolean[][] visited.
     *
     * 3. DFS vs BFS CHOICE: DFS is simpler to code. If asked about stack overflow
     *    risk for very large grids, mention BFS as alternative.
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "What if the grid is very large and DFS might overflow the stack?"
     * A: Use iterative BFS with a Queue<int[]>. Same time complexity, bounded
     *    by O(min(m,n)) queue size for BFS frontier.
     *
     * Q: "What if islands are added dynamically (online)?"
     * A: Use Union-Find (Disjoint Set Union). Each new '1' cell unions with
     *    adjacent '1' cells. Number of islands = number of distinct components.
     *    O(alpha(n)) per operation with path compression + union by rank.
     *
     * Q: "What about Max Area of Island?" (LC 695)
     * A: Same DFS, but return the count of cells visited per DFS and track max.
     *
     * Q: "What if the grid wraps around (edges connect)?"
     * A: Use modular arithmetic: (r + dr + rows) % rows, (c + dc + cols) % cols.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. BFS:
     *    - Pros: No stack overflow, bounded memory for queue
     *    - Cons: Slightly more code (explicit queue)
     *
     * 2. Union-Find:
     *    - Pros: Supports dynamic updates, parallelizable
     *    - Cons: More complex implementation for a static grid
     *    - Time: O(m*n * alpha(m*n)) which is effectively O(m*n)
     */

    public static void main(String[] args) {
        NumberOfIslandsSolution sol = new NumberOfIslandsSolution();
        char[][] grid = {
            {'1','1','0','0','0'},
            {'1','1','0','0','0'},
            {'0','0','1','0','0'},
            {'0','0','0','1','1'}
        };
        assert sol.numIslands(grid) == 3;
        System.out.println("All solution tests passed!");
    }
}
