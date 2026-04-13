/**
 * Integer to English Words — Solution
 * ====================================
 *
 * Approach: Process in groups of 3 digits (billions, millions, thousands, ones)
 * Use a helper to convert numbers < 1000 to words.
 *
 * Complexity:
 *   - Time: O(1) — bounded by integer range
 *   - Space: O(1) — output length bounded
 */

public class IntegerToEnglishWordsSolution {

    private static final String[] ONES = {
        "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen"
    };

    private static final String[] TENS = {
        "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
    };

    private static final String[] THOUSANDS = {
        "", "Thousand", "Million", "Billion"
    };

    public String numberToWords(int num) {
        if (num == 0) return "Zero";

        StringBuilder result = new StringBuilder();
        int groupIndex = 0;

        while (num > 0) {
            int group = num % 1000;
            if (group != 0) {
                String groupWords = threeDigitToWords(group);
                if (groupIndex > 0) {
                    groupWords += " " + THOUSANDS[groupIndex];
                }
                if (result.length() > 0) {
                    result.insert(0, groupWords + " ");
                } else {
                    result.insert(0, groupWords);
                }
            }
            num /= 1000;
            groupIndex++;
        }

        return result.toString();
    }

    private String threeDigitToWords(int num) {
        StringBuilder sb = new StringBuilder();

        if (num >= 100) {
            sb.append(ONES[num / 100]).append(" Hundred");
            num %= 100;
            if (num > 0) sb.append(" ");
        }

        if (num >= 20) {
            sb.append(TENS[num / 10]);
            num %= 10;
            if (num > 0) sb.append(" ");
        }

        if (num > 0) {
            sb.append(ONES[num]);
        }

        return sb.toString();
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. CLEAN DECOMPOSITION: Splitting into threeDigitToWords helper shows good design.
     *    The main method handles scale words (Thousand, Million, Billion).
     *
     * 2. TEEN HANDLING: 11-19 must be special-cased. A common bug is outputting
     *    "Ten One" instead of "Eleven".
     *
     * 3. SPACING: No leading/trailing spaces, no double spaces. This is a common bug.
     *    Test with inputs like 1000000 (no "Thousand" part).
     *
     * 4. ZERO GROUP: Groups of 000 (e.g., 1,000,000) should not produce output.
     *    Don't append "Thousand" for an empty group.
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "How would you handle ordinal numbers (1st, 2nd, 3rd)?"
     * A: Add suffix mapping: 1->First, 2->Second, 3->Third, else append "th"
     *    to the word form. Special cases: Twelve->Twelfth, Twenty->Twentieth.
     *
     * Q: "How would you support multiple languages?"
     * A: Strategy pattern — abstract the word arrays and grammar rules into a
     *    locale-specific converter. Some languages have different grouping
     *    (e.g., Chinese/Japanese use 10,000-based groups).
     *
     * Q: "What about decimal numbers?"
     * A: Split on decimal point. Convert integer part normally. For decimal,
     *    either say digits individually ("point one two three") or convert
     *    as fraction ("and 123 thousandths").
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. Recursive:
     *    - Pros: More elegant for some, avoids the loop
     *    - Cons: Stack depth proportional to number of groups (max 4, so fine)
     *
     * 2. String array for all numbers < 1000:
     *    - Pros: O(1) lookup, no branching
     *    - Cons: 1000 entries, wasteful
     */

    public static void main(String[] args) {
        IntegerToEnglishWordsSolution sol = new IntegerToEnglishWordsSolution();
        assert sol.numberToWords(123).equals("One Hundred Twenty Three");
        assert sol.numberToWords(0).equals("Zero");
        assert sol.numberToWords(1000000).equals("One Million");
        assert sol.numberToWords(2147483647).equals(
            "Two Billion One Hundred Forty Seven Million Four Hundred Eighty Three Thousand Six Hundred Forty Seven");
        System.out.println("All solution tests passed!");
    }
}
