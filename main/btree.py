class BTree:
    def __init__(self, vals=None):
        self.root = None
    
        if vals is not None:
            for v in vals:
                self.insert(v)
    
    def insert(self, val):
        if self.root is None:
            self.root = BTNode(val)
            return
        return self._insert_r(val, self.root)

    def _insert_r(self, val, current):
        if val == current.val:
            return
        elif val < current.val:
            if current.left is None:
                current.left = BTNode(val, parent=current)
                return
            else:
                return self._insert_r(val, current.left)
        elif val > current.val:
            if current.right is None:
                current.right = BTNode(val, parent=current)
                return
            else:
                return self._insert_r(val, current.right)
    
    def delete(self, val):
        return self.delete_node(self.find(val))
    
    def delete_node(self, node):
        if node is None:
            return

        if node.left is None and node.right is None:
            # case 1: no children, so just delete the reference
            if node.is_left_child():
                self._set_left_child(node.parent, None)
            else:
                self._set_right_child(node.parent, None)
                
            if self.root == node:
                self.root = None

        elif node.left is None:
            # node has only a right child
            if node.is_left_child():
                self._set_left_child(node.parent, node.right)
            else:
                self._set_right_child(node.parent, node.right)

            self._set_parent(node.right, node.parent)
        
        elif node.right is None:
            #node has only a left child
            if node.is_left_child():
                self._set_left_child(node.parent, node.left)
            else:
                self._set_right_child(node.parent, node.left)

            self._set_parent(node.left, node.parent)
        
        else:
            # node has two children. We swap it with its successor, which will have at most one child, then delete it.
            self._swap_nodes(node, self.successor(node))
            return self.delete_node(node)
        
        # delete internal references from deleted node. Most likely unnecessary.
        node.left = node.right = node.parent = None
            
    def find(self, val):
        return self._find_r(val, self.root)
    
    def _find_r(self, val, current):
        if current is None:
            return None
        
        if val == current.val:
            return current
        elif val < current.val:
            return self._find_r(val, current.left)
        else:
            return self._find_r(val, current.right)
        
    def __contains__(self, val):
        return self.find(val)
    
    def depth_of_node(self, node):
        depth = 1
        while node.parent is not None:
            depth += 1
            node = node.parent
        return depth
    
    def depth_of(self, val):
        return self.depth_of_node(self.find(val))
    
    def depth(self):
        depths = map(self.depth_of_node, self.sorted_nodes())
        return max(depths, default=0)
    
    def sorted_list(self):
        return map(lambda x: x.val, self.sorted_nodes())
    
    def sorted_nodes(self):
        if self.root is None:
            return []
        return self._sorted_nodes_r(self.root)
    
    def _sorted_nodes_r(self, node):
        left = (
            [] if node.left is None
            else self._sorted_nodes_r(node.left)
        )
        right = (
            [] if node.right is None
            else self._sorted_nodes_r(node.right)
        )
        return left + [node] + right
    
    def successor(self, node):
        # if node has a right child, go right once, then left all the way down to a leaf node
        if node.right is not None:
            current = node.right
            while current.left is not None:
                current = current.left
            return current
        
        # if node has no right child and no parent, then it has no successor
        if node.parent is None:
            return None
        
        # if there is a parent, we need to climb up to the first non-right ancestor (possibly node itself), and take its parent as the successor (might be None)
        ancestor = node
        while ancestor.is_right_child():
            ancestor = ancestor.parent
        return ancestor.parent
    
    def predecessor(self, node):
        # as in successor(node), but with directions reversed
        if node.left is not None:
            current = node.left
            while current.right is not None:
                current = current.right
            return current
        
        if node.parent is None:
            return None
        
        ancestor = node
        while ancestor.is_left_child():
            ancestor = ancestor.parent
        return ancestor.parent
    
    def rotate_left(self, node):
        if node.right is None:
            return # should this throw an exception instead?
        pivot = node.right

        node_parent = node.parent
        node_was_left = node.is_left_child()
        self._transplant(pivot.left, node, False)
        self._transplant(node, pivot, True)
        self._transplant(pivot, node_parent, node_was_left)
    
    def rotate_right(self, node):
        if node.left is None:
            return
        pivot = node.left

        node_parent = node.parent
        node_was_left = node.is_left_child()
        self._transplant(pivot.right, node, True)
        self._transplant(node, pivot, False)
        self._transplant(pivot, node_parent, node_was_left)

    def rotate_pivot(self, pivot):
        if self.root == pivot:
            return # this definitely feels more exception-y
        if pivot.is_left_child():
            return self.rotate_right(pivot.parent)
        else:
            return self.rotate_left(pivot.parent)
    
    # --- The following methods can destroy the ordering property or worse, so they are for internal use only.
    
    def _set_parent(self, node, parent):
        if node is not None:
            node.parent = parent
    
    def _set_left_child(self, node, child):
        if node is not None:
            node.left = child
    
    def _set_right_child(self, node, child):
        if node is not None:
            node.right = child

    def _transplant(self, node, target_parent, left_side):
        if target_parent is None:
            self.root = node
            node.parent = None
            return
        
        target = target_parent.left if left_side else target_parent.right

        if left_side:
            target_parent.left = node
        else:
            target_parent.right = node
        
        self._set_parent(node, target_parent)
    
    def _swap_nodes(self, node1, node2):
        # I want to swap nodes rather than just their values because it makes the test cases easier
        # to write. Yet it makes the algorithm itself more cumbersome. Is this stupid?
        if node1 == node2: return
        if node1.parent == node2:
            node1, node2 = node2, node1 # reduce to case where node1 is the parent of node2, which follows:
        if node2.parent == node1:
            node1_wes_left = node1.is_left_child()

            if node2.is_left_child():
                node1.right, node2.right = node2.right, node2.right
                node1.left, node2.left = node2.left, node1
            else:
                node1.left, node2.left = node2.left, node1.left
                node1.right, node2.right = node2.right, node1

            node1.parent, node2.parent = node2, node1.parent
            if node1_wes_left:
                self._set_left_child(node2.parent, node2)
            else:
                self._set_right_child(node2.parent, node2)
            
        else: # generic case
            node1.left, node2.left = node2.left, node1.left
            node1.right, node2.right = node2.right, node1.right
            parent1, parent2 = node1.parent, node2.parent
            self._set_parent(node1, parent2)
            self._set_parent(node2, parent1)
        
        # this, at least, works for all cases
        self._set_parent(node1.left, node1)
        self._set_parent(node1.right, node1)
        self._set_parent(node2.left, node2)
        self._set_parent(node2.right, node2)

        if self.root == node1:
            self.root = node2
        elif self.root == node2:
            self.root = node1

class BTNode:
    def __init__(self, val, parent=None):
        self.val = val
        self.parent = parent
        self.left = None
        self.right = None
    
    def is_left_child(self):
        return self.parent is not None and self.parent.left == self
    
    def is_right_child(self):
        return self.parent is not None and self.parent.right == self
    
    def sibling(self):
        if self.parent is None:
            return None
        if self.is_left_child():
            return self.parent.right
        else:
            return self.parent.left
    
    def uncle(self):
        if self.parent is None or self.parent.parent is None:
            return None
        return self.parent.sibling()
    
    def __repr__(self):
        return f"BTNode({self.val})"
