/**
 * Merge Intervals — Solution
 * ==========================
 *
 * Approach: Sort + Linear Scan
 * 1. Sort intervals by start time
 * 2. Iterate, merging overlapping intervals
 *
 * Complexity:
 *   - Time: O(n log n) for sorting
 *   - Space: O(n) for output
 */

import java.util.*;

public class MergeIntervalsSolution {

    public int[][] merge(int[][] intervals) {
        if (intervals.length <= 1) return intervals;

        // Sort by start time
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));

        List<int[]> merged = new ArrayList<>();
        int[] current = intervals[0];
        merged.add(current);

        for (int i = 1; i < intervals.length; i++) {
            if (intervals[i][0] <= current[1]) {
                // Overlapping — extend the end
                current[1] = Math.max(current[1], intervals[i][1]);
            } else {
                // No overlap — start new interval
                current = intervals[i];
                merged.add(current);
            }
        }

        return merged.toArray(new int[merged.size()][]);
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. SORT FIRST: Recognizing that sorting simplifies the problem from O(n^2) to O(n log n).
     *
     * 2. IN-PLACE MERGE: Notice we modify `current[1]` directly — the reference in the list
     *    updates automatically. This avoids unnecessary object creation.
     *
     * 3. EDGE CASES: Touching intervals [1,4],[4,5] should merge. <= not <.
     *
     * 4. CLEAN CODE: Using Integer.compare avoids integer overflow from subtraction.
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "What if intervals are streaming in real-time?"
     * A: Use a TreeMap<Integer, Integer> (start -> end). On each new interval, find overlapping
     *    entries with floorKey/ceilingKey and merge them. O(log n) per insertion.
     *
     * Q: "What if you need to insert one interval into a sorted non-overlapping list?"
     * A: Binary search for insertion point, then merge with neighbors. O(n) worst case
     *    due to shifting, but O(log n) for finding position.
     *
     * Q: "How would you parallelize this?"
     * A: Partition the sorted array, merge each partition in parallel, then merge
     *    the boundary intervals between partitions.
     *
     * Q: "What about the 'Meeting Rooms II' variant — minimum rooms needed?"
     * A: Separate starts and ends, sort each, sweep with a counter. Or use a min-heap
     *    of end times. This is LC 253 and also frequently asked at Microsoft.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. TreeMap-based:
     *    - Pros: Supports dynamic insertion/deletion
     *    - Cons: O(n log n) total, more complex code
     *
     * 2. Connected Components (graph-based):
     *    - Build graph where overlapping intervals are connected, find components
     *    - Pros: Conceptually clean
     *    - Cons: O(n^2) time — much worse
     */

    public static void main(String[] args) {
        MergeIntervalsSolution sol = new MergeIntervalsSolution();
        int[][] result = sol.merge(new int[][]{{1,3},{2,6},{8,10},{15,18}});
        assert Arrays.deepEquals(result, new int[][]{{1,6},{8,10},{15,18}});
        System.out.println("All solution tests passed!");
    }
}
