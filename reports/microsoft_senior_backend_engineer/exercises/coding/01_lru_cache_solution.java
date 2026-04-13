/**
 * LRU Cache — Solution
 * ====================
 *
 * Approach: HashMap + Doubly Linked List
 * - HashMap maps key -> Node for O(1) lookup
 * - Doubly Linked List maintains access order: head = most recent, tail = least recent
 * - Sentinel head/tail nodes simplify boundary operations
 *
 * Complexity:
 *   - Time: O(1) for get and put
 *   - Space: O(capacity)
 */

import java.util.HashMap;
import java.util.Map;

public class LRUCacheSolution {

    private class Node {
        int key, value;
        Node prev, next;

        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<Integer, Node> map;
    private final Node head; // sentinel: most recent side
    private final Node tail; // sentinel: least recent side

    public LRUCacheSolution(int capacity) {
        this.capacity = capacity;
        this.map = new HashMap<>();
        this.head = new Node(0, 0);
        this.tail = new Node(0, 0);
        head.next = tail;
        tail.prev = head;
    }

    public int get(int key) {
        if (!map.containsKey(key)) {
            return -1;
        }
        Node node = map.get(key);
        // Move to front (most recently used)
        remove(node);
        insertAfterHead(node);
        return node.value;
    }

    public void put(int key, int value) {
        if (map.containsKey(key)) {
            // Update existing: remove, update value, re-insert at front
            Node node = map.get(key);
            remove(node);
            node.value = value;
            insertAfterHead(node);
        } else {
            // Insert new
            if (map.size() == capacity) {
                // Evict LRU (node before tail sentinel)
                Node lru = tail.prev;
                remove(lru);
                map.remove(lru.key);
            }
            Node newNode = new Node(key, value);
            insertAfterHead(newNode);
            map.put(key, newNode);
        }
    }

    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void insertAfterHead(Node node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. CLEAN SEPARATION: Sentinel nodes eliminate null checks for head/tail boundary cases.
     *    This is the #1 thing experienced interviewers notice — it shows maturity.
     *
     * 2. NAMING: "remove" and "insertAfterHead" are self-documenting.
     *    Avoid names like "helper1" or "moveNode".
     *
     * 3. KEY IN NODE: Storing the key in the Node is critical — when evicting the LRU node
     *    from the tail, you need the key to remove it from the HashMap.
     *    Forgetting this is the most common bug.
     *
     * 4. THREAD SAFETY: If asked "what if this is concurrent?", discuss:
     *    - ReadWriteLock (multiple readers, single writer)
     *    - ConcurrentHashMap + synchronized list operations
     *    - Striped locking for higher throughput
     *    - Java's LinkedHashMap as a simpler alternative (but less educational)
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "What if the input is very large (millions of keys)?"
     * A: The design scales linearly with capacity. For distributed systems,
     *    consider consistent hashing to shard across nodes (this connects
     *    directly to Microsoft's Distributed Cache system design question).
     *
     * Q: "How would you make this thread-safe?"
     * A: Use ReentrantReadWriteLock — get() takes read lock, put() takes write lock.
     *    For higher concurrency, use striped locks or ConcurrentHashMap with
     *    synchronized linked list segments.
     *
     * Q: "What about LFU (Least Frequently Used) instead?"
     * A: LFU requires a frequency counter per node + a min-frequency tracker.
     *    Use a HashMap<frequency, DoublyLinkedList> to group nodes by frequency.
     *    O(1) operations still possible. (LeetCode 460)
     *
     * Q: "Could you implement this with Java's built-in classes?"
     * A: Yes — LinkedHashMap with accessOrder=true and override removeEldestEntry().
     *    But interviewers want to see you build the data structure from scratch.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. LinkedHashMap (Java built-in):
     *    - Pros: 3 lines of code, battle-tested
     *    - Cons: Doesn't demonstrate understanding; interviewers explicitly don't want this
     *
     * 2. TreeMap with timestamp:
     *    - Pros: Simpler mental model
     *    - Cons: O(log n) operations — fails the O(1) requirement
     *
     * 3. Array-based circular buffer:
     *    - Pros: Cache-friendly memory access
     *    - Cons: O(n) for arbitrary removal — fails O(1) requirement
     */

    public static void main(String[] args) {
        LRUCacheSolution cache = new LRUCacheSolution(2);
        cache.put(1, 1);
        cache.put(2, 2);
        assert cache.get(1) == 1;
        cache.put(3, 3);
        assert cache.get(2) == -1;
        cache.put(4, 4);
        assert cache.get(1) == -1;
        assert cache.get(3) == 3;
        assert cache.get(4) == 4;
        System.out.println("All solution tests passed!");
    }
}
