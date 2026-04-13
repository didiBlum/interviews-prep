/**
 * Serialize and Deserialize Binary Tree — Solution
 * =================================================
 *
 * Approach: Preorder DFS with null markers
 * - Serialize: preorder traversal, comma-delimited, "null" for null nodes
 * - Deserialize: consume tokens in preorder, recursively build tree
 *
 * Complexity:
 *   - Time: O(n) for both operations
 *   - Space: O(n) for the string / O(h) for recursion stack where h is tree height
 */

import java.util.*;

public class SerializeDeserializeBinaryTreeSolution {

    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int x) { val = x; }
    }

    private static final String NULL_MARKER = "null";
    private static final String DELIMITER = ",";

    public String serialize(TreeNode root) {
        StringBuilder sb = new StringBuilder();
        serializeDfs(root, sb);
        return sb.toString();
    }

    private void serializeDfs(TreeNode node, StringBuilder sb) {
        if (node == null) {
            sb.append(NULL_MARKER).append(DELIMITER);
            return;
        }
        sb.append(node.val).append(DELIMITER);
        serializeDfs(node.left, sb);
        serializeDfs(node.right, sb);
    }

    public TreeNode deserialize(String data) {
        Queue<String> tokens = new LinkedList<>(Arrays.asList(data.split(DELIMITER)));
        return deserializeDfs(tokens);
    }

    private TreeNode deserializeDfs(Queue<String> tokens) {
        if (tokens.isEmpty()) return null;

        String token = tokens.poll();
        if (token.equals(NULL_MARKER)) {
            return null;
        }

        TreeNode node = new TreeNode(Integer.parseInt(token));
        node.left = deserializeDfs(tokens);
        node.right = deserializeDfs(tokens);
        return node;
    }

    /*
     * ==================== WHAT INTERVIEWERS LOOK FOR ====================
     *
     * 1. TRAVERSAL CHOICE: Preorder is natural because the root comes first,
     *    making deserialization straightforward. BFS (level-order) also works
     *    but the code is slightly more complex.
     *
     * 2. NULL MARKERS: Essential for reconstructing structure. Without them,
     *    you'd need both inorder + preorder traversals.
     *
     * 3. DELIMITER HANDLING: Using split with a queue is clean. Some candidates
     *    use an index pointer (int[]{0}) passed by reference — also valid.
     *
     * 4. STRING BUILDER: Using StringBuilder instead of string concatenation
     *    shows awareness of O(n^2) vs O(n) string building in Java.
     *
     * ==================== COMMON FOLLOW-UPS ====================
     *
     * Q: "How would you optimize space?"
     * A: Several approaches discussed in the 1-hour Microsoft interview:
     *    - Use single bits for null markers instead of "null" string
     *    - Use binary encoding (4 bytes per int) instead of ASCII digits
     *    - For BSTs specifically, preorder alone suffices (no null markers needed)
     *    - Huffman coding on the value distribution
     *    - Delta encoding if values are close together
     *
     * Q: "What if the tree is very deep (stack overflow)?"
     * A: Use iterative BFS serialization with a queue. Level-order avoids
     *    deep recursion. Track null children explicitly.
     *
     * Q: "What about a BST instead of general binary tree?"
     * A: For BSTs, preorder traversal alone is sufficient — no null markers needed.
     *    Deserialization uses value bounds to determine left/right subtree boundaries.
     *    Space: O(n) values instead of O(2n) with markers.
     *
     * Q: "How would you handle this for a distributed system?"
     * A: Use Protocol Buffers or similar binary format. Consider compression
     *    (gzip). For very large trees, serialize subtrees independently
     *    and store in a distributed store with parent references.
     *
     * ==================== ALTERNATIVE APPROACHES ====================
     *
     * 1. BFS (Level-order):
     *    - Pros: Iterative, no stack overflow risk
     *    - Cons: More null markers for sparse trees, more complex code
     *
     * 2. Preorder + Inorder (no null markers):
     *    - Pros: Slightly smaller output for dense trees
     *    - Cons: O(n^2) deserialization without optimization; doesn't work with duplicates
     *
     * 3. Binary encoding:
     *    - Pros: Much more compact (4 bytes per node vs variable-length ASCII)
     *    - Cons: Not human-readable, more complex to implement
     */

    public static void main(String[] args) {
        SerializeDeserializeBinaryTreeSolution codec = new SerializeDeserializeBinaryTreeSolution();
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);
        root.right.left = new TreeNode(4);
        root.right.right = new TreeNode(5);

        String serialized = codec.serialize(root);
        TreeNode deserialized = codec.deserialize(serialized);
        assert deserialized.val == 1;
        assert deserialized.right.left.val == 4;
        assert codec.deserialize(codec.serialize(null)) == null;
        System.out.println("All solution tests passed!");
    }
}
