/**
 * Integer to English Words (LeetCode 273)
 * ========================================
 * Reported in: Microsoft Senior (L63-L64) interviews — one of the most commonly asked hard problems.
 * Sources: HelloInterview L63-64 guide
 *
 * Problem:
 * Convert a non-negative integer num to its English words representation.
 *
 * Examples:
 *   Input: 123
 *   Output: "One Hundred Twenty Three"
 *
 *   Input: 12345
 *   Output: "Twelve Thousand Three Hundred Forty Five"
 *
 *   Input: 1234567
 *   Output: "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven"
 *
 *   Input: 0
 *   Output: "Zero"
 *
 * Constraints:
 *   - 0 <= num <= 2^31 - 1 (max 2,147,483,647 — "Two Billion ...")
 *
 * Complexity targets:
 *   - Time: O(1) — bounded by max integer size
 *   - Space: O(1)
 *
 * HINT 1: Process 3 digits at a time (ones, thousands, millions, billions).
 * HINT 2: Build a helper that converts a number < 1000 to words.
 * HINT 3: Handle teens (11-19) separately from tens (20, 30, ..., 90) — this is the tricky part.
 */

public class IntegerToEnglishWords {

    public String numberToWords(int num) {
        // TODO: Implement
        return "";
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        IntegerToEnglishWords sol = new IntegerToEnglishWords();

        assert sol.numberToWords(123).equals("One Hundred Twenty Three") : "Test 1 failed";
        System.out.println("Test 1 passed: 123");

        assert sol.numberToWords(12345).equals("Twelve Thousand Three Hundred Forty Five") : "Test 2 failed";
        System.out.println("Test 2 passed: 12345");

        assert sol.numberToWords(1234567).equals("One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven")
            : "Test 3 failed";
        System.out.println("Test 3 passed: 1234567");

        assert sol.numberToWords(0).equals("Zero") : "Test 4 failed";
        System.out.println("Test 4 passed: 0");

        assert sol.numberToWords(1000000).equals("One Million") : "Test 5 failed";
        System.out.println("Test 5 passed: 1000000");

        assert sol.numberToWords(20).equals("Twenty") : "Test 6 failed";
        System.out.println("Test 6 passed: 20");

        assert sol.numberToWords(15).equals("Fifteen") : "Test 7 failed";
        System.out.println("Test 7 passed: 15 (teen)");

        assert sol.numberToWords(2147483647).equals(
            "Two Billion One Hundred Forty Seven Million Four Hundred Eighty Three Thousand Six Hundred Forty Seven")
            : "Test 8 failed";
        System.out.println("Test 8 passed: Integer.MAX_VALUE");

        assert sol.numberToWords(100).equals("One Hundred") : "Test 9 failed";
        System.out.println("Test 9 passed: 100 (no trailing words)");

        System.out.println("\nAll tests passed!");
    }
}
