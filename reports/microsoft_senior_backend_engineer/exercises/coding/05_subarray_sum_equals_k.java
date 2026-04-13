/**
 * Subarray Sum Equals K (LeetCode 560)
 * =====================================
 * Reported in: Microsoft coding rounds — frequently asked.
 * Sources: InterviewSolver (66%+ frequency), Interviewing.io, CodingInterview.com
 *
 * Problem:
 * Given an array of integers nums and an integer k, return the total number of
 * subarrays whose sum equals to k.
 *
 * A subarray is a contiguous non-empty sequence of elements within an array.
 *
 * Examples:
 *   Input: nums = [1,1,1], k = 2
 *   Output: 2  (subarrays [1,1] at index 0-1 and 1-2)
 *
 *   Input: nums = [1,2,3], k = 3
 *   Output: 2  (subarrays [1,2] and [3])
 *
 * Constraints:
 *   - 1 <= nums.length <= 2 * 10^4
 *   - -1000 <= nums[i] <= 1000
 *   - -10^7 <= k <= 10^7
 *
 * Complexity targets:
 *   - Time: O(n)
 *   - Space: O(n)
 *
 * HINT 1: The sum of subarray [i, j] = prefixSum[j] - prefixSum[i-1]. So you need
 *         prefixSum[j] - prefixSum[i-1] == k, i.e., prefixSum[i-1] == prefixSum[j] - k.
 * HINT 2: Use a HashMap to count how many times each prefix sum has occurred so far.
 * HINT 3: As you compute running prefix sum, check if (prefixSum - k) exists in the map.
 *         Initialize the map with {0: 1} to handle subarrays starting from index 0.
 */

import java.util.*;

public class SubarraySumEqualsK {

    public int subarraySum(int[] nums, int k) {
        // TODO: Implement
        return 0;
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        SubarraySumEqualsK sol = new SubarraySumEqualsK();

        assert sol.subarraySum(new int[]{1,1,1}, 2) == 2 : "Test 1 failed";
        System.out.println("Test 1 passed: [1,1,1], k=2 -> 2");

        assert sol.subarraySum(new int[]{1,2,3}, 3) == 2 : "Test 2 failed";
        System.out.println("Test 2 passed: [1,2,3], k=3 -> 2");

        assert sol.subarraySum(new int[]{1}, 0) == 0 : "Test 3 failed";
        System.out.println("Test 3 passed: [1], k=0 -> 0");

        // Negative numbers
        assert sol.subarraySum(new int[]{-1,-1,1}, 0) == 1 : "Test 4 failed";
        System.out.println("Test 4 passed: [-1,-1,1], k=0 -> 1");

        // Entire array sums to k
        assert sol.subarraySum(new int[]{1,2,3}, 6) == 1 : "Test 5 failed";
        System.out.println("Test 5 passed: [1,2,3], k=6 -> 1");

        // Multiple overlapping subarrays
        assert sol.subarraySum(new int[]{0,0,0}, 0) == 6 : "Test 6 failed";
        System.out.println("Test 6 passed: [0,0,0], k=0 -> 6");

        // Negative k
        assert sol.subarraySum(new int[]{-1,2,-1}, -1) == 2 : "Test 7 failed";
        System.out.println("Test 7 passed: [-1,2,-1], k=-1 -> 2");

        System.out.println("\nAll tests passed!");
    }
}
