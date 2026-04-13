/**
 * Subarray Sum Equals K — Solution
 * =================================
 *
 * Approach: Prefix Sum + HashMap
 * - Compute running prefix sum
 * - For each prefix sum, check how many previous prefix sums equal (currentSum - k)
 * - Those represent subarrays that sum to k
 *
 * Complexity:
 *   - Time: O(n)
 *   - Space: O(n) for the HashMap
 */

import java.util.*;

public class SubarraySumEqualsKSolution {

    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> prefixCount = new HashMap<>();
        prefixCount.put(0, 1); // empty prefix has sum 0

        int sum = 0;
        int count = 0;

        for (int num : nums) {
            sum += num;
            // How many previous prefix sums equal (sum - k)?
            // Each one marks a start point for a subarray summing to k
            count += prefixCount.getOrDefault(sum - k, 0);
            prefixCount.merge(sum, 1, Integer::sum);
        }

        return count;
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. PREFIX SUM INSIGHT: Recognizing that subarray sum = difference of prefix sums
     *    is the key insight. This is a fundamental pattern used in many problems.
     *
     * 2. INITIALIZATION: Map must be initialized with {0: 1}. Forgetting this is the
     *    #1 bug — it misses subarrays starting from index 0.
     *
     * 3. ORDER OF OPERATIONS: Count BEFORE adding current prefix sum to map.
     *    Otherwise you'd count the empty subarray from index i to i.
     *
     * 4. WHY NOT SLIDING WINDOW?: Because values can be negative. Sliding window
     *    only works when all values are positive (expanding always increases sum).
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "What if all values are positive? Can we do O(1) space?"
     * A: Yes — use sliding window (two pointers). Expand right to increase sum,
     *    shrink left to decrease. O(n) time, O(1) space.
     *
     * Q: "What if we want the longest subarray with sum k?"
     * A: Same prefix sum approach, but store the first occurrence of each prefix
     *    sum. Track max length = i - firstOccurrence[sum - k].
     *
     * Q: "What about 2D submatrix sum equals k?"
     * A: Fix top and bottom rows, compute column prefix sums, reduce to 1D
     *    subarray sum problem. O(m^2 * n) time.
     *
     * Q: "What if k changes dynamically?"
     * A: Precompute all prefix sums. For each query k, iterate prefix sums
     *    with a fresh HashMap. Or use offline processing if queries are batched.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. Brute force: O(n^2) — check all subarrays
     *    - Pros: Simple, no extra space
     *    - Cons: Too slow for n = 20,000
     *
     * 2. Brute force with prefix sum array: O(n^2)
     *    - Slightly faster constant factor but same complexity
     *
     * 3. Sliding window (positive values only): O(n) time, O(1) space
     *    - Not applicable here because of negative values
     */

    public static void main(String[] args) {
        SubarraySumEqualsKSolution sol = new SubarraySumEqualsKSolution();
        assert sol.subarraySum(new int[]{1,1,1}, 2) == 2;
        assert sol.subarraySum(new int[]{0,0,0}, 0) == 6;
        System.out.println("All solution tests passed!");
    }
}
