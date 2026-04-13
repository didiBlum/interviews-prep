/**
 * Serialize and Deserialize Binary Tree (LeetCode 297)
 * =====================================================
 * Reported in: Microsoft Senior (L63) interview — 1+ hour deep discussion on space optimization.
 * Sources: Medium (Rohit Verma 2025-2026), HelloInterview L63-64 guide
 *
 * Problem:
 * Design an algorithm to serialize and deserialize a binary tree. Serialization is the process
 * of converting a tree to a string, and deserialization is converting the string back to the
 * original tree structure.
 *
 * You may serialize to any string format as long as your deserialize method can reconstruct
 * the original tree from the string.
 *
 * Example:
 *       1
 *      / \
 *     2   3
 *        / \
 *       4   5
 *
 *   serialize:   "1,2,null,null,3,4,null,null,5,null,null"
 *   deserialize: reconstructs the same tree
 *
 * Constraints:
 *   - Number of nodes: [0, 10^4]
 *   - Node values: [-1000, 1000]
 *
 * Complexity targets:
 *   - Time: O(n) for both serialize and deserialize
 *   - Space: O(n) for the serialized string
 *
 * HINT 1: Preorder traversal (root, left, right) with null markers preserves tree structure.
 * HINT 2: Use a delimiter (e.g., comma) between values and a special marker (e.g., "null") for null nodes.
 * HINT 3: Deserialization uses recursion with a queue/iterator: consume the next token, if null return null,
 *         otherwise create node and recursively build left and right subtrees.
 */

import java.util.*;

public class SerializeDeserializeBinaryTree {

    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int x) { val = x; }
    }

    // Encodes a tree to a single string
    public String serialize(TreeNode root) {
        // TODO: Implement serialize
        return "";
    }

    // Decodes your encoded data to tree
    public TreeNode deserialize(String data) {
        // TODO: Implement deserialize
        return null;
    }

    // ==================== TESTS ====================
    public static void main(String[] args) {
        SerializeDeserializeBinaryTree codec = new SerializeDeserializeBinaryTree();

        // Test 1: Standard tree
        //       1
        //      / \
        //     2   3
        //        / \
        //       4   5
        TreeNode root1 = new TreeNode(1);
        root1.left = new TreeNode(2);
        root1.right = new TreeNode(3);
        root1.right.left = new TreeNode(4);
        root1.right.right = new TreeNode(5);
        String s1 = codec.serialize(root1);
        TreeNode d1 = codec.deserialize(s1);
        assert d1.val == 1 : "Test 1a failed";
        assert d1.left.val == 2 : "Test 1b failed";
        assert d1.right.val == 3 : "Test 1c failed";
        assert d1.right.left.val == 4 : "Test 1d failed";
        assert d1.right.right.val == 5 : "Test 1e failed";
        assert d1.left.left == null : "Test 1f failed";
        System.out.println("Test 1 passed: standard tree");

        // Test 2: Empty tree
        String s2 = codec.serialize(null);
        TreeNode d2 = codec.deserialize(s2);
        assert d2 == null : "Test 2 failed: expected null";
        System.out.println("Test 2 passed: empty tree");

        // Test 3: Single node
        TreeNode root3 = new TreeNode(42);
        String s3 = codec.serialize(root3);
        TreeNode d3 = codec.deserialize(s3);
        assert d3.val == 42 : "Test 3a failed";
        assert d3.left == null : "Test 3b failed";
        assert d3.right == null : "Test 3c failed";
        System.out.println("Test 3 passed: single node");

        // Test 4: Left-skewed tree
        TreeNode root4 = new TreeNode(1);
        root4.left = new TreeNode(2);
        root4.left.left = new TreeNode(3);
        String s4 = codec.serialize(root4);
        TreeNode d4 = codec.deserialize(s4);
        assert d4.val == 1 && d4.left.val == 2 && d4.left.left.val == 3 : "Test 4 failed";
        System.out.println("Test 4 passed: left-skewed tree");

        // Test 5: Negative values
        TreeNode root5 = new TreeNode(-1);
        root5.left = new TreeNode(-2);
        root5.right = new TreeNode(3);
        String s5 = codec.serialize(root5);
        TreeNode d5 = codec.deserialize(s5);
        assert d5.val == -1 && d5.left.val == -2 && d5.right.val == 3 : "Test 5 failed";
        System.out.println("Test 5 passed: negative values");

        System.out.println("\nAll tests passed!");
    }
}
