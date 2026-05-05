class BTreeNode:
    def __init__(self, is_leaf):
        self.is_leaf = is_leaf
        self.keys = []
        self.rids = []
        self.children = []


class BTree:
    def __init__(self, d):
        self.d = d
        self.max_keys = 2 * d - 1
        self.min_keys = d - 1
        self.root = BTreeNode(is_leaf=True)
        self.split_count = 0

    def search(self, key):
        return self._search_node(self.root, key)

    def _search_node(self, node, key):
        i = 0

        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return node.rids[i]

        if node.is_leaf:
            return None

        return self._search_node(node.children[i], key)

    def insert(self, key, rid):
        root = self.root

        if len(root.keys) == self.max_keys:
            new_root = BTreeNode(is_leaf=False)
            new_root.children.append(root)
            self.root = new_root

            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, rid)
        else:
            self._insert_non_full(root, key, rid)

    def _insert_non_full(self, node, key, rid):
        i = len(node.keys) - 1

        if node.is_leaf:
            node.keys.append(None)
            node.rids.append(None)

            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.rids[i + 1] = node.rids[i]
                i -= 1

            node.keys[i + 1] = key
            node.rids[i + 1] = rid

        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1

            i += 1

            if len(node.children[i].keys) == self.max_keys:
                self._split_child(node, i)

                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, rid)

    def _split_child(self, parent, index):
        d = self.d
        child = parent.children[index]
        new_child = BTreeNode(is_leaf=child.is_leaf)

        middle_key = child.keys[d - 1]
        middle_rid = child.rids[d - 1]

        new_child.keys = child.keys[d:]
        new_child.rids = child.rids[d:]

        child.keys = child.keys[:d - 1]
        child.rids = child.rids[:d - 1]

        if not child.is_leaf:
            new_child.children = child.children[d:]
            child.children = child.children[:d]

        parent.keys.insert(index, middle_key)
        parent.rids.insert(index, middle_rid)
        parent.children.insert(index + 1, new_child)

        self.split_count += 1

    #Function for verification

    def get_height(self):
        height = 0
        node = self.root

        while not node.is_leaf:
            height += 1
            node = node.children[0]

        return height

    def get_node_utilization(self):
        total_keys = 0
        total_capacity = 0

        def traverse(node):
            nonlocal total_keys, total_capacity

            total_keys += len(node.keys)
            total_capacity += self.max_keys

            if not node.is_leaf:
                for child in node.children:
                    traverse(child)

        traverse(self.root)

        if total_capacity == 0:
            return 0

        return total_keys / total_capacity

    def count_nodes(self):
        count = 0

        def traverse(node):
            nonlocal count
            count += 1

            if not node.is_leaf:
                for child in node.children:
                    traverse(child)

        traverse(self.root)
        return count
    
    def range_query(self, start_key, end_key):
        result = []

        def traverse(node):
            i = 0

            while i < len(node.keys):
                if not node.is_leaf:
                    traverse(node.children[i])

                key = node.keys[i]

                if start_key <= key <= end_key:
                    result.append((key, node.rids[i]))

                i += 1

            if not node.is_leaf:
                traverse(node.children[i])

        traverse(self.root)
        return result
    
    #Delete
    def delete(self, key):
        deleted = self._delete(self.root, key)

        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]

        return deleted

    def _delete(self, node, key):
        i = 0

        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and node.keys[i] == key:
            if node.is_leaf:
                node.keys.pop(i)
                node.rids.pop(i)
                return True
            else:
                return self._delete_internal_key(node, i)

        else:
            if node.is_leaf:
                return False

            child_index = i
            child = node.children[child_index]

            if len(child.keys) < self.d:
                self._fill_child(node, child_index)

                if child_index > len(node.keys):
                    child_index -= 1

            return self._delete(node.children[child_index], key)

    def _delete_internal_key(self, node, index):
        key = node.keys[index]

        left_child = node.children[index]
        right_child = node.children[index + 1]

        if len(left_child.keys) >= self.d:
            pred_key, pred_rid = self._get_predecessor(left_child)

            node.keys[index] = pred_key
            node.rids[index] = pred_rid

            return self._delete(left_child, pred_key)

        elif len(right_child.keys) >= self.d:
            succ_key, succ_rid = self._get_successor(right_child)

            node.keys[index] = succ_key
            node.rids[index] = succ_rid

            return self._delete(right_child, succ_key)

        else:
            self._merge_children(node, index)
            return self._delete(left_child, key)

    def _get_predecessor(self, node):
        current = node

        while not current.is_leaf:
            current = current.children[-1]

        return current.keys[-1], current.rids[-1]

    def _get_successor(self, node):
        current = node

        while not current.is_leaf:
            current = current.children[0]

        return current.keys[0], current.rids[0]

    def _fill_child(self, parent, index):
        if index > 0 and len(parent.children[index - 1].keys) >= self.d:
            self._borrow_from_prev(parent, index)

        elif index < len(parent.children) - 1 and len(parent.children[index + 1].keys) >= self.d:
            self._borrow_from_next(parent, index)

        else:
            if index < len(parent.children) - 1:
                self._merge_children(parent, index)
            else:
                self._merge_children(parent, index - 1)

    def _borrow_from_prev(self, parent, index):
        child = parent.children[index]
        sibling = parent.children[index - 1]

        child.keys.insert(0, parent.keys[index - 1])
        child.rids.insert(0, parent.rids[index - 1])

        if not child.is_leaf:
            child.children.insert(0, sibling.children.pop())

        parent.keys[index - 1] = sibling.keys.pop()
        parent.rids[index - 1] = sibling.rids.pop()

    def _borrow_from_next(self, parent, index):
        child = parent.children[index]
        sibling = parent.children[index + 1]

        child.keys.append(parent.keys[index])
        child.rids.append(parent.rids[index])

        if not child.is_leaf:
            child.children.append(sibling.children.pop(0))

        parent.keys[index] = sibling.keys.pop(0)
        parent.rids[index] = sibling.rids.pop(0)

    def _merge_children(self, parent, index):
        child = parent.children[index]
        sibling = parent.children[index + 1]

        child.keys.append(parent.keys.pop(index))
        child.rids.append(parent.rids.pop(index))

        child.keys.extend(sibling.keys)
        child.rids.extend(sibling.rids)

        if not child.is_leaf:
            child.children.extend(sibling.children)

        parent.children.pop(index + 1)