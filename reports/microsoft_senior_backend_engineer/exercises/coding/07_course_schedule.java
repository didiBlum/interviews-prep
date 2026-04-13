/**
 * Course Schedule (LeetCode 207)
 * ===============================
 * Reported in: Microsoft coding rounds — topological sort is a key pattern.
 * Sources: HackMNC, Lodely, DesignGurus
 *
 * Problem:
 * There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1.
 * You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you
 * must take course bi first if you want to take course ai.
 *
 * Return true if you can finish all courses. Otherwise, return false.
 *
 * Examples:
 *   Input: numCourses = 2, prerequisites = [[1,0]]
 *   Output: true  (Take 0 then 1)
 *
 *   Input: numCourses = 2, prerequisites = [[1,0],[0,1]]
 *   Output: false (Cycle: 0 requires 1, 1 requires 0)
 *
 * Constraints:
 *   - 1 <= numCourses <= 2000
 *   - 0 <= prerequisites.length <= 5000
 *   - prerequisites[i].length == 2
 *   - 0 <= ai, bi < numCourses
 *   - All prerequisite pairs are unique
 *
 * Complexity targets:
 *   - Time: O(V + E) where V = numCourses, E = prerequisites.length
 *   - Space: O(V + E)
 *
 * HINT 1: This is a cycle detection problem in a directed graph.
 * HINT 2: Use Kahn's algorithm (BFS topological sort): start with nodes having in-degree 0.
 * HINT 3: If you can process all nodes via BFS (removing edges as you go), there's no cycle.
 *         If some nodes remain unprocessed, a cycle exists.
 */

import java.util.*;

public class CourseSchedule {

    public boolean canFinish(int numCourses, int[][] prerequisites) {
        // TODO: Implement
        return false;
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        CourseSchedule sol = new CourseSchedule();

        assert sol.canFinish(2, new int[][]{{1,0}}) == true : "Test 1 failed";
        System.out.println("Test 1 passed: simple prerequisite");

        assert sol.canFinish(2, new int[][]{{1,0},{0,1}}) == false : "Test 2 failed";
        System.out.println("Test 2 passed: cycle detected");

        assert sol.canFinish(1, new int[][]{}) == true : "Test 3 failed";
        System.out.println("Test 3 passed: single course, no prereqs");

        assert sol.canFinish(4, new int[][]{{1,0},{2,0},{3,1},{3,2}}) == true : "Test 4 failed";
        System.out.println("Test 4 passed: diamond dependency");

        assert sol.canFinish(3, new int[][]{{0,1},{1,2},{2,0}}) == false : "Test 5 failed";
        System.out.println("Test 5 passed: 3-node cycle");

        // Disconnected graph with no cycles
        assert sol.canFinish(5, new int[][]{{1,0},{3,2}}) == true : "Test 6 failed";
        System.out.println("Test 6 passed: disconnected graph");

        System.out.println("\nAll tests passed!");
    }
}
