/**
 * Course Schedule — Solution
 * ==========================
 *
 * Approach: Kahn's Algorithm (BFS Topological Sort)
 * 1. Build adjacency list and compute in-degrees
 * 2. Enqueue all nodes with in-degree 0
 * 3. Process queue: for each node, reduce in-degree of neighbors; enqueue if in-degree becomes 0
 * 4. If all nodes processed, no cycle exists
 *
 * Complexity:
 *   - Time: O(V + E)
 *   - Space: O(V + E)
 */

import java.util.*;

public class CourseScheduleSolution {

    public boolean canFinish(int numCourses, int[][] prerequisites) {
        List<List<Integer>> adj = new ArrayList<>();
        int[] inDegree = new int[numCourses];

        for (int i = 0; i < numCourses; i++) {
            adj.add(new ArrayList<>());
        }

        for (int[] prereq : prerequisites) {
            adj.get(prereq[1]).add(prereq[0]);
            inDegree[prereq[0]]++;
        }

        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }

        int processedCount = 0;
        while (!queue.isEmpty()) {
            int course = queue.poll();
            processedCount++;

            for (int neighbor : adj.get(course)) {
                inDegree[neighbor]--;
                if (inDegree[neighbor] == 0) {
                    queue.offer(neighbor);
                }
            }
        }

        return processedCount == numCourses;
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. GRAPH MODELING: Recognizing this as a directed graph cycle detection problem.
     *
     * 2. BFS vs DFS: Kahn's (BFS) is generally preferred because:
     *    - No recursion stack overhead
     *    - Naturally produces topological order
     *    - Easier to extend to Course Schedule II
     *
     * 3. EDGE DIRECTION: prereq[1] -> prereq[0] means "take prereq[1] before prereq[0]".
     *    Getting this backwards is a common bug.
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "Return one valid course ordering." (Course Schedule II, LC 210)
     * A: Same algorithm, but collect processed nodes in a list. Return the list
     *    if all courses processed, else empty array.
     *
     * Q: "What if you need to find the minimum semesters to finish all courses?"
     * A: This is "Parallel Courses" (LC 1136) — also asked in Microsoft OA.
     *    Use BFS levels: each level = one semester. Answer = number of BFS levels.
     *
     * Q: "What if prerequisites can be added/removed dynamically?"
     * A: Maintain in-degrees and adjacency list incrementally. On add: increment
     *    in-degree and add edge. On remove: decrement and remove. Re-run topo sort
     *    from affected nodes.
     *
     * Q: "What about Alien Dictionary?" (LC 269)
     * A: Build a graph from character ordering in the word list, then topological sort.
     *    Also frequently asked at Microsoft.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. DFS with coloring (white/gray/black):
     *    - Pros: Also O(V+E), can detect back edges (cycles)
     *    - Cons: Recursive, needs careful state management
     *
     * 2. DFS with visited + recursion stack:
     *    - Pros: Slightly simpler than coloring
     *    - Cons: Two boolean arrays, still recursive
     */

    public static void main(String[] args) {
        CourseScheduleSolution sol = new CourseScheduleSolution();
        assert sol.canFinish(2, new int[][]{{1,0}}) == true;
        assert sol.canFinish(2, new int[][]{{1,0},{0,1}}) == false;
        assert sol.canFinish(4, new int[][]{{1,0},{2,0},{3,1},{3,2}}) == true;
        System.out.println("All solution tests passed!");
    }
}
