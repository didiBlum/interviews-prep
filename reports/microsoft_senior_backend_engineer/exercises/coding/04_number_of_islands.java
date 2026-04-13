/**
 * Number of Islands (LeetCode 200)
 * =================================
 * Reported in: Microsoft coding rounds — frequently asked across levels.
 * Sources: InterviewSolver, CodingInterview.com, Lodely, Onsites.fyi, HackMNC
 *
 * Problem:
 * Given an m x n 2D binary grid which represents a map of '1's (land) and '0's (water),
 * return the number of islands. An island is surrounded by water and is formed by connecting
 * adjacent lands horizontally or vertically. You may assume all four edges of the grid are
 * surrounded by water.
 *
 * Examples:
 *   Input: grid = [
 *     ["1","1","1","1","0"],
 *     ["1","1","0","1","0"],
 *     ["1","1","0","0","0"],
 *     ["0","0","0","0","0"]
 *   ]
 *   Output: 1
 *
 *   Input: grid = [
 *     ["1","1","0","0","0"],
 *     ["1","1","0","0","0"],
 *     ["0","0","1","0","0"],
 *     ["0","0","0","1","1"]
 *   ]
 *   Output: 3
 *
 * Constraints:
 *   - m == grid.length, n == grid[i].length
 *   - 1 <= m, n <= 300
 *   - grid[i][j] is '0' or '1'
 *
 * Complexity targets:
 *   - Time: O(m * n)
 *   - Space: O(m * n) worst case for DFS stack / BFS queue (can be O(1) extra if modifying grid)
 *
 * HINT 1: Each unvisited '1' starts a new island. Mark all connected '1's as visited.
 * HINT 2: Use DFS or BFS from each unvisited '1' to "sink" the entire island (mark as '0').
 * HINT 3: The number of times you initiate a DFS/BFS equals the number of islands.
 */

public class NumberOfIslands {

    public int numIslands(char[][] grid) {
        // TODO: Implement
        return 0;
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        NumberOfIslands sol = new NumberOfIslands();

        // Test 1: Single island
        char[][] grid1 = {
            {'1','1','1','1','0'},
            {'1','1','0','1','0'},
            {'1','1','0','0','0'},
            {'0','0','0','0','0'}
        };
        assert sol.numIslands(grid1) == 1 : "Test 1 failed";
        System.out.println("Test 1 passed: single island");

        // Test 2: Three islands
        char[][] grid2 = {
            {'1','1','0','0','0'},
            {'1','1','0','0','0'},
            {'0','0','1','0','0'},
            {'0','0','0','1','1'}
        };
        assert sol.numIslands(grid2) == 3 : "Test 2 failed";
        System.out.println("Test 2 passed: three islands");

        // Test 3: All water
        char[][] grid3 = {
            {'0','0','0'},
            {'0','0','0'}
        };
        assert sol.numIslands(grid3) == 0 : "Test 3 failed";
        System.out.println("Test 3 passed: all water");

        // Test 4: All land
        char[][] grid4 = {
            {'1','1'},
            {'1','1'}
        };
        assert sol.numIslands(grid4) == 1 : "Test 4 failed";
        System.out.println("Test 4 passed: all land");

        // Test 5: Single cell island
        char[][] grid5 = {
            {'0','0','0'},
            {'0','1','0'},
            {'0','0','0'}
        };
        assert sol.numIslands(grid5) == 1 : "Test 5 failed";
        System.out.println("Test 5 passed: single cell island");

        // Test 6: Diagonal doesn't count
        char[][] grid6 = {
            {'1','0','1'},
            {'0','1','0'},
            {'1','0','1'}
        };
        assert sol.numIslands(grid6) == 5 : "Test 6 failed";
        System.out.println("Test 6 passed: diagonal doesn't connect");

        System.out.println("\nAll tests passed!");
    }
}
