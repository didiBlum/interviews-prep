/**
 * Merge Intervals (LeetCode 56)
 * =============================
 * Reported in: Microsoft coding rounds and OA (Codility).
 * Sources: CodingInterview.com, Lodely OA guide, DesignGurus
 *
 * Problem:
 * Given an array of intervals where intervals[i] = [start_i, end_i], merge all
 * overlapping intervals, and return an array of the non-overlapping intervals
 * that cover all the intervals in the input.
 *
 * Examples:
 *   Input:  [[1,3],[2,6],[8,10],[15,18]]
 *   Output: [[1,6],[8,10],[15,18]]
 *
 *   Input:  [[1,4],[4,5]]
 *   Output: [[1,5]]
 *
 * Constraints:
 *   - 1 <= intervals.length <= 10^4
 *   - intervals[i].length == 2
 *   - 0 <= start_i <= end_i <= 10^4
 *
 * Complexity targets:
 *   - Time: O(n log n)
 *   - Space: O(n) for the output (O(log n) for sorting if in-place sort)
 *
 * HINT 1: What if you sorted the intervals by their start time first?
 * HINT 2: After sorting, two adjacent intervals overlap if the second's start <= the first's end.
 * HINT 3: When merging, take the max of both end times. Use a result list and compare each
 *         interval with the last merged interval.
 */

import java.util.*;

public class MergeIntervals {

    public int[][] merge(int[][] intervals) {
        // TODO: Implement merge
        return new int[0][0];
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        MergeIntervals sol = new MergeIntervals();

        // Test 1: Standard overlapping
        int[][] result1 = sol.merge(new int[][]{{1,3},{2,6},{8,10},{15,18}});
        assert Arrays.deepEquals(result1, new int[][]{{1,6},{8,10},{15,18}})
            : "Test 1 failed: " + Arrays.deepToString(result1);
        System.out.println("Test 1 passed: standard overlapping");

        // Test 2: Touching intervals
        int[][] result2 = sol.merge(new int[][]{{1,4},{4,5}});
        assert Arrays.deepEquals(result2, new int[][]{{1,5}})
            : "Test 2 failed: " + Arrays.deepToString(result2);
        System.out.println("Test 2 passed: touching intervals");

        // Test 3: No overlaps
        int[][] result3 = sol.merge(new int[][]{{1,2},{5,6},{9,10}});
        assert Arrays.deepEquals(result3, new int[][]{{1,2},{5,6},{9,10}})
            : "Test 3 failed";
        System.out.println("Test 3 passed: no overlaps");

        // Test 4: All merge into one
        int[][] result4 = sol.merge(new int[][]{{1,10},{2,6},{3,5},{7,9}});
        assert Arrays.deepEquals(result4, new int[][]{{1,10}})
            : "Test 4 failed: " + Arrays.deepToString(result4);
        System.out.println("Test 4 passed: all merge into one");

        // Test 5: Single interval
        int[][] result5 = sol.merge(new int[][]{{1,1}});
        assert Arrays.deepEquals(result5, new int[][]{{1,1}})
            : "Test 5 failed";
        System.out.println("Test 5 passed: single interval");

        // Test 6: Unsorted input
        int[][] result6 = sol.merge(new int[][]{{8,10},{1,3},{2,6},{15,18}});
        assert Arrays.deepEquals(result6, new int[][]{{1,6},{8,10},{15,18}})
            : "Test 6 failed: " + Arrays.deepToString(result6);
        System.out.println("Test 6 passed: unsorted input");

        System.out.println("\nAll tests passed!");
    }
}
