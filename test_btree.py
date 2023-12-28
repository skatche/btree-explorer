import unittest

from main.btree import *

class TestBTree(unittest.TestCase):
    def test_insert(self):
        tree = BTree()
        
        tree.insert(5)      # -> 5
        tree.insert(10)     # -> 5 (R-> 10)
        tree.insert(7)      # -> 5 (R-> 10 (L-> 7))
        tree.insert(4)      # -> 5 (L-> 4, R-> 10 (L-> 7))
        # check whole structure
        self.assertEqual(tree.root.val, 5)
        self.assertEqual(tree.root.left.val, 4)
        self.assertIsNone(tree.root.left.left)
        self.assertIsNone(tree.root.left.right)
        self.assertEqual(tree.root.right.val, 10)
        self.assertEqual(tree.root.right.left.val, 7)
        self.assertIsNone(tree.root.right.right)
        self.assertIsNone(tree.root.right.left.left)
        self.assertIsNone(tree.root.right.left.right)
    
    def test_find(self):
        #                                5
        #         4                                             11
        #    2                                          7
        #      3                                      6   9
        #                                                  10
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])
        self.assertTrue(tree.find(7))
        self.assertFalse(tree.find(8))
        self.assertTrue(3 in tree)
        self.assertFalse(12 in tree)
    
    def test_successor(self):
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])

        node5 = tree.find(5)
        node6 = tree.find(6)
        node7 = tree.find(7)
        node10 = tree.find(10)
        node11 = tree.find(11)

        self.assertEqual(tree.successor(node5), node6)
        self.assertEqual(tree.successor(node6), node7)
        self.assertEqual(tree.successor(node10), node11)
        self.assertIsNone(tree.successor(node11))

    def test_predecessor(self):
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])

        node2 = tree.find(2)
        node3 = tree.find(3)
        node4 = tree.find(4)
        node5 = tree.find(5)
        node6 = tree.find(6)

        self.assertIsNone(tree.predecessor(node2))
        self.assertEqual(tree.predecessor(node3), node2)
        self.assertEqual(tree.predecessor(node4), node3)
        self.assertEqual(tree.predecessor(node5), node4)
        self.assertEqual(tree.predecessor(node6), node5)
    
    def test_delete(self):
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])

        node4 = tree.find(4)
        node5 = tree.find(5)
        node6 = tree.find(6)
        node7 = tree.find(7)
        node9 = tree.find(9)
        node10 = tree.find(10)
        node11 = tree.find(11)
        
        tree.delete_node(node10)
        self.assertIsNone(node10.parent)
        self.assertIsNone(node9.right)

        tree.delete(11)
        self.assertIsNone(node11.left)
        self.assertEqual(node5.right, node7)
        self.assertEqual(node7.parent, node5)

        tree.delete_node(node5)
        self.assertEqual(tree.root, node6)
        self.assertEqual(node6.right, node7)
        self.assertEqual(node7.parent, node6)
        self.assertEqual(node6.left, node4)
        self.assertEqual(node4.parent, node6)
        self.assertIsNone(node6.parent)

        self.assertFalse(tree.find(10))
        self.assertFalse(tree.find(11))
        self.assertFalse(tree.find(5))
    
    def test_rotation(self):
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])

        node4 = tree.find(4)
        node5 = tree.find(5)
        node6 = tree.find(6)
        node7 = tree.find(7)
        node9 = tree.find(9)
        node10 = tree.find(10)
        node11 = tree.find(11)

        tree.rotate_left(node9)
        self.assertEqual(node7.right, node10)
        self.assertEqual(node10.parent, node7)
        self.assertEqual(node10.left, node9)
        self.assertEqual(node9.parent, node10)
        self.assertIsNone(node9.left)
        self.assertIsNone(node9.right)

        tree.rotate_pivot(node10) # should rotate left at node7
        self.assertEqual(node11.left, node10)
        self.assertEqual(node10.parent, node11)
        self.assertEqual(node10.left, node7)
        self.assertEqual(node7.parent, node10)
        self.assertEqual(node7.left, node6)
        self.assertEqual(node7.right, node9)
        self.assertEqual(node9.parent, node7)

        tree.rotate_right(node5)
        self.assertEqual(tree.root, node4)
    
    def test_internals(self):
        #                                5
        #         4                                             11
        #    2                                          7
        #      3                                      6   9
        #                                                  10
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])
        
        node4 = tree.find(4)
        node5 = tree.find(5)
        node9 = tree.find(9)
        node10 = tree.find(10)

        tree._transplant(node9, node5, True)
        self.assertEqual(node9.parent, node5)
        self.assertTrue(node9.is_left_child())
        self.assertIsNone(node9.left)
        self.assertEqual(node9.right, node10)
        tree._transplant(node9, None, True)
        self.assertEqual(tree.root, node9)
        self.assertIsNone(node9.parent)

        # refresh tree
        tree = BTree([5, 11, 7, 4, 6, 9, 2, 3, 10])
        node5 = tree.find(5)
        node6 = tree.find(6)
        node7 = tree.find(7)
        node9 = tree.find(9)
        node10 = tree.find(10)
        node11 = tree.find(11)

        tree._swap_nodes(node7, node9)
        self.assertEqual(node7.parent, node9)
        self.assertEqual(node9.parent, node11)
        self.assertEqual(node9.right, node7)
        self.assertIsNone(node7.left, None)
        self.assertEqual(node7.right, node10)
        self.assertEqual(node9.left, node6)
        
        tree._swap_nodes(node11, node5)
        self.assertEqual(tree.root, node11)
        self.assertIsNone(node11.parent)
        self.assertEqual(node5.parent, node11)
        self.assertEqual(node11.right, node5)
        self.assertEqual(node5.left, node9) # because we swapped earlier
    
    def test_btnode(self):
        tree = BTree([5, 10, 7, 4]) # as in test_insert
        node10 = tree.root.right
        node7 = tree.root.right.left
        node4 = tree.root.left

        self.assertFalse(tree.root.is_left_child())
        self.assertFalse(tree.root.is_right_child())
        self.assertTrue(node7.is_left_child())
        self.assertFalse(node7.is_right_child())
        self.assertEqual(node10.sibling(), node4)
        self.assertEqual(node4.sibling(), node10)
        self.assertEqual(node7.uncle(), node4)


if __name__ == "__main__":
    unittest.main()