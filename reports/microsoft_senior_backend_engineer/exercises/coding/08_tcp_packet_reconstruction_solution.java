/**
 * TCP Packet Reconstruction — Solution
 * ======================================
 *
 * Approach: Sort by offset + sweep (interval coverage check)
 * 1. Validate that exactly one packet has isEnd = true
 * 2. Sort packets by offset
 * 3. Sweep: track the furthest byte covered. Each packet must start at or before
 *    the current coverage boundary.
 * 4. The final coverage must reach the end of the last (isEnd) packet.
 *
 * Complexity:
 *   - Time: O(n log n) for sorting
 *   - Space: O(1) extra (sorting in-place) or O(n) for copy
 */

import java.util.*;

public class TcpPacketReconstructionSolution {

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
        if (packets == null || packets.isEmpty()) return false;

        // Find the end packet and calculate total data length
        int totalEnd = -1;
        boolean hasEnd = false;
        for (Packet p : packets) {
            if (p.isEnd) {
                if (hasEnd) return false; // multiple end markers is invalid
                hasEnd = true;
                totalEnd = p.offset + p.length;
            }
        }

        if (!hasEnd) return false; // no end marker means data is incomplete

        // Sort by offset, then by length descending (longer packets first for same offset)
        List<Packet> sorted = new ArrayList<>(packets);
        sorted.sort((a, b) -> a.offset != b.offset
            ? Integer.compare(a.offset, b.offset)
            : Integer.compare(b.length, a.length));

        // Sweep: track coverage boundary
        int covered = 0; // bytes [0, covered) are covered

        for (Packet p : sorted) {
            // If this packet starts beyond our coverage, there's a gap
            if (p.offset > covered) {
                return false;
            }

            // Extend coverage
            int packetEnd = p.offset + p.length;
            if (packetEnd > covered) {
                covered = packetEnd;
            }
        }

        return covered >= totalEnd;
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. PROBLEM REDUCTION: Recognizing this as an interval coverage problem
     *    (similar to Merge Intervals) is the key insight.
     *
     * 2. EDGE CASES:
     *    - No end marker -> false
     *    - Packets starting after 0 -> gap from start
     *    - Fully overlapping packets -> should still work
     *    - Large offsets/lengths -> use long if needed for offset + length overflow
     *
     * 3. SORTING STRATEGY: Sort by offset is essential. Breaking ties by length
     *    descending ensures maximum coverage is considered first.
     *
     * 4. REAL-WORLD CONNECTION: This directly relates to TCP reassembly in
     *    networking — a great topic to discuss with Microsoft interviewers
     *    given their Azure networking infrastructure.
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "What if packets can be duplicated?"
     * A: The algorithm already handles duplicates — overlapping intervals are
     *    naturally merged in the sweep.
     *
     * Q: "What if you need to return the actual reconstructed data?"
     * A: Sort by offset, use a byte array or StringBuilder. Copy each packet's
     *    data, skipping already-written regions. O(total_data_length) time.
     *
     * Q: "What if packets arrive as a stream?"
     * A: Use a TreeMap<Integer, Integer> (offset -> end) to maintain merged
     *    intervals. On each new packet, merge with overlapping entries.
     *    Check completeness when end marker arrives.
     *
     * Q: "How does real TCP handle this?"
     * A: TCP uses sequence numbers (like our offsets), ACKs for received ranges,
     *    retransmission for lost packets, and a receive buffer for reordering.
     *    Discuss sliding window protocol if the interviewer goes deeper.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. Union-Find on byte ranges:
     *    - Pros: Handles streaming packets well
     *    - Cons: More complex, harder to implement correctly
     *
     * 2. Boolean array marking each byte:
     *    - Pros: Simple
     *    - Cons: O(total_data_length) space — impractical for large offsets
     */

    public static void main(String[] args) {
        TcpPacketReconstructionSolution sol = new TcpPacketReconstructionSolution();

        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 5, false), new Packet(5, 3, true)
        )) == true;

        assert sol.canReconstruct(Arrays.asList(
            new Packet(0, 3, false), new Packet(5, 3, true)
        )) == false;

        assert sol.canReconstruct(Arrays.asList(
            new Packet(7, 3, true), new Packet(0, 4, false), new Packet(3, 5, false)
        )) == true;

        System.out.println("All solution tests passed!");
    }
}
