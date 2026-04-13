/**
 * LRU Cache (LeetCode 146)
 * =======================
 * Reported in: Microsoft Senior (L63-L64) interviews — one of the most frequently asked questions.
 * Sources: HelloInterview, InterviewSolver (88% frequency), Interviewing.io, Lodely
 *
 * Problem:
 * Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.
 *
 * Implement the LRUCache class:
 *   - LRUCache(int capacity) — Initialize the LRU cache with positive size capacity.
 *   - int get(int key) — Return the value of the key if it exists, otherwise return -1.
 *   - void put(int key, int value) — Update the value of the key if it exists. Otherwise,
 *     add the key-value pair to the cache. If the number of keys exceeds the capacity,
 *     evict the least recently used key.
 *
 * Both get and put must run in O(1) average time complexity.
 *
 * Constraints:
 *   - 1 <= capacity <= 3000
 *   - 0 <= key <= 10^4
 *   - 0 <= value <= 10^5
 *   - At most 2 * 10^5 calls to get and put
 *
 * Complexity targets:
 *   - Time: O(1) for both get and put
 *   - Space: O(capacity)
 *
 * HINT 1: You need two data structures working together — one for O(1) lookup, one for O(1) ordering.
 * HINT 2: A HashMap gives O(1) lookup. A Doubly Linked List allows O(1) removal and insertion at ends.
 * HINT 3: The HashMap maps keys to linked list nodes. On access, move the node to the head (most recent).
 *         On eviction, remove from the tail (least recent).
 */

import java.util.HashMap;
import java.util.Map;

public class LRUCache {

    // TODO: Define a doubly linked list node class

    // TODO: Initialize your data structures

    public LRUCache(int capacity) {
        // TODO: Implement constructor
    }

    public int get(int key) {
        // TODO: Implement get
        return -1;
    }

    public void put(int key, int value) {
        // TODO: Implement put
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        // Test 1: Basic operations
        LRUCache cache = new LRUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        assert cache.get(1) == 1 : "Test 1a failed: expected 1";
        cache.put(3, 3);    // evicts key 2
        assert cache.get(2) == -1 : "Test 1b failed: expected -1 (evicted)";
        cache.put(4, 4);    // evicts key 1
        assert cache.get(1) == -1 : "Test 1c failed: expected -1 (evicted)";
        assert cache.get(3) == 3 : "Test 1d failed: expected 3";
        assert cache.get(4) == 4 : "Test 1e failed: expected 4";
        System.out.println("Test 1 passed: basic operations");

        // Test 2: Update existing key
        LRUCache cache2 = new LRUCache(2);
        cache2.put(1, 1);
        cache2.put(2, 2);
        cache2.put(1, 10);  // update value
        assert cache2.get(1) == 10 : "Test 2a failed: expected 10";
        cache2.put(3, 3);   // should evict key 2 (not 1, since 1 was recently updated)
        assert cache2.get(2) == -1 : "Test 2b failed: expected -1 (evicted)";
        assert cache2.get(1) == 10 : "Test 2c failed: expected 10";
        System.out.println("Test 2 passed: update existing key");

        // Test 3: Capacity 1
        LRUCache cache3 = new LRUCache(1);
        cache3.put(1, 1);
        assert cache3.get(1) == 1 : "Test 3a failed";
        cache3.put(2, 2);
        assert cache3.get(1) == -1 : "Test 3b failed: expected -1 (evicted)";
        assert cache3.get(2) == 2 : "Test 3c failed: expected 2";
        System.out.println("Test 3 passed: capacity 1");

        // Test 4: Get non-existent key
        LRUCache cache4 = new LRUCache(2);
        assert cache4.get(1) == -1 : "Test 4 failed: expected -1";
        System.out.println("Test 4 passed: get non-existent key");

        // Test 5: Access order matters
        LRUCache cache5 = new LRUCache(3);
        cache5.put(1, 1);
        cache5.put(2, 2);
        cache5.put(3, 3);
        cache5.get(1);       // makes 1 most recent; order is now 2, 3, 1
        cache5.put(4, 4);   // should evict 2
        assert cache5.get(2) == -1 : "Test 5a failed: expected -1 (evicted)";
        assert cache5.get(1) == 1 : "Test 5b failed: expected 1";
        assert cache5.get(3) == 3 : "Test 5c failed: expected 3";
        assert cache5.get(4) == 4 : "Test 5d failed: expected 4";
        System.out.println("Test 5 passed: access order matters");

        System.out.println("\nAll tests passed!");
    }
}
