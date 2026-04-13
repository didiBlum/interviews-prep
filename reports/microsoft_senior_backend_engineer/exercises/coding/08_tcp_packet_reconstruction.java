/**
 * TCP Packet Reconstruction (Custom Microsoft Problem)
 * =====================================================
 * Reported in: Microsoft Senior L63 onsite interview — Hyderabad.
 * Source: Roundz Substack (https://roundz.substack.com/p/microsoft-senior-software-engineer-63)
 *
 * Problem:
 * You are given a list of TCP packets. Each packet has:
 *   - offset: the starting byte position in the original data
 *   - length: the number of bytes in this packet
 *   - isEnd: whether this packet contains the final byte of the data
 *
 * Packets may arrive out of order and may overlap. Determine if the complete
 * original data can be reconstructed from the given packets (i.e., every byte
 * from position 0 to the end is covered).
 *
 * Return true if the full data can be reconstructed, false otherwise.
 *
 * Examples:
 *   Input: packets = [{offset:0, length:5, isEnd:false},
 *                     {offset:5, length:3, isEnd:true}]
 *   Output: true (bytes 0-7 covered, last packet marked end)
 *
 *   Input: packets = [{offset:0, length:3, isEnd:false},
 *                     {offset:5, length:3, isEnd:true}]
 *   Output: false (bytes 3-4 missing)
 *
 *   Input: packets = [{offset:0, length:5, isEnd:false},
 *                     {offset:3, length:5, isEnd:true}]
 *   Output: true (overlapping, bytes 0-7 covered)
 *
 * Constraints:
 *   - 1 <= packets.length <= 10^5
 *   - 0 <= offset <= 10^9
 *   - 1 <= length <= 10^9
 *   - Exactly 0 or 1 packet has isEnd = true
 *   - If no packet has isEnd = true, the data cannot be complete
 *
 * Complexity targets:
 *   - Time: O(n log n)
 *   - Space: O(n)
 *
 * HINT 1: This is essentially an interval coverage problem. Each packet covers [offset, offset+length).
 * HINT 2: Sort packets by offset. Then check if intervals form a contiguous range from 0 to the end.
 * HINT 3: Similar to Merge Intervals — after sorting, check that each interval's start <= current coverage end.
 *         The end marker tells you the total length.
 */

import java.util.*;

public class TcpPacketReconstruction {

    public static class Packet {
        int offset;
        int length;
        boolean isEnd;

        Packet(int offset, int length, boolean isEnd) {
            this.offset = offset;
            this.length = length;
            this.isEnd = isEnd;
        }
    }

    public boolean canReconstruct(List<Packet> packets) {
        // TODO: Implement
        return false;
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        TcpPacketReconstruction sol = new TcpPacketReconstruction();

        // Test 1: Contiguous packets
        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 5, false),
            new Packet(5, 3, true)
        )) == true : "Test 1 failed";
        System.out.println("Test 1 passed: contiguous packets");

        // Test 2: Gap in coverage
        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 3, false),
            new Packet(5, 3, true)
        )) == false : "Test 2 failed";
        System.out.println("Test 2 passed: gap detected");

        // Test 3: Overlapping packets
        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 5, false),
            new Packet(3, 5, true)
        )) == true : "Test 3 failed";
        System.out.println("Test 3 passed: overlapping packets");

        // Test 4: No end marker
        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 5, false),
            new Packet(5, 3, false)
        )) == false : "Test 4 failed";
        System.out.println("Test 4 passed: no end marker");

        // Test 5: Doesn't start at 0
        assert sol.canReconstruct(Arrays.asList(
            new Packet(1, 5, false),
            new Packet(6, 3, true)
        )) == false : "Test 5 failed";
        System.out.println("Test 5 passed: doesn't start at 0");

        // Test 6: Out of order, overlapping, complete
        assert sol.canReconstruct(Arrays.asList(
            new Packet(7, 3, true),
            new Packet(0, 4, false),
            new Packet(3, 5, false)
        )) == true : "Test 6 failed";
        System.out.println("Test 6 passed: out of order + overlapping");

        // Test 7: Single packet covering everything
        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 10, true)
        )) == true : "Test 7 failed";
        System.out.println("Test 7 passed: single complete packet");

        System.out.println("\nAll tests passed!");
    }
}
