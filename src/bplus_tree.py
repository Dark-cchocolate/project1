class BPlusTreeNode:
    def __init__(self, is_leaf):
        self.is_leaf = is_leaf
        self.keys = []

        # leaf node only
        self.rids = []
        self.next = None

        # internal node only
        self.children = []


class BPlusTree:
    def __init__(self, d):
        self.d = d
        self.max_keys = 2 * d - 1
        self.min_keys = d - 1
        self.root = BPlusTreeNode(is_leaf=True)
        self.split_count = 0

    def search(self, key):
        leaf = self._find_leaf(key)

        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.rids[i]

        return None

    def _find_leaf(self, key):
        node = self.root

        while not node.is_leaf:
            i = 0

            while i < len(node.keys) and key >= node.keys[i]:
                i += 1

            node = node.children[i]

        return node

    def insert(self, key, rid):
        root = self.root

        if len(root.keys) == self.max_keys:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.children.append(root)
            self.root = new_root

            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, rid)
        else:
            self._insert_non_full(root, key, rid)

    def _insert_non_full(self, node, key, rid):
        if node.is_leaf:
            i = len(node.keys) - 1

            node.keys.append(None)
            node.rids.append(None)

            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.rids[i + 1] = node.rids[i]
                i -= 1

            node.keys[i + 1] = key
            node.rids[i + 1] = rid

        else:
            i = 0

            while i < len(node.keys) and key >= node.keys[i]:
                i += 1

            if len(node.children[i].keys) == self.max_keys:
                self._split_child(node, i)

                if key >= node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, rid)

    def _split_child(self, parent, index):
        child = parent.children[index]
        new_child = BPlusTreeNode(is_leaf=child.is_leaf)

        mid = self.d

        if child.is_leaf:
            new_child.keys = child.keys[mid:]
            new_child.rids = child.rids[mid:]

            child.keys = child.keys[:mid]
            child.rids = child.rids[:mid]

            new_child.next = child.next
            child.next = new_child

            promoted_key = new_child.keys[0]

            parent.keys.insert(index, promoted_key)
            parent.children.insert(index + 1, new_child)

        else:
            promoted_key = child.keys[mid - 1]

            new_child.keys = child.keys[mid:]
            new_child.children = child.children[mid:]

            child.keys = child.keys[:mid - 1]
            child.children = child.children[:mid]

            parent.keys.insert(index, promoted_key)
            parent.children.insert(index + 1, new_child)

        self.split_count += 1

    def range_query(self, start_key, end_key):
        result = []

        leaf = self._find_leaf(start_key)

        while leaf is not None:
            for i, key in enumerate(leaf.keys):
                if key > end_key:
                    return result

                if start_key <= key <= end_key:
                    result.append((key, leaf.rids[i]))

            leaf = leaf.next

        return result
    

    def delete(self, key):
        deleted = self._delete_recursive(self.root, key)

        if not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]

        return deleted

    def _delete_recursive(self, node, key):
        if node.is_leaf:
            for i, k in enumerate(node.keys):
                if k == key:
                    node.keys.pop(i)
                    node.rids.pop(i)
                    return True

            return False

        child_index = 0

        while child_index < len(node.keys) and key >= node.keys[child_index]:
            child_index += 1

        child = node.children[child_index]

        deleted = self._delete_recursive(child, key)

        if not deleted:
            return False

        self._refresh_internal_keys(node)

        if len(child.keys) < self.min_keys:
            self._rebalance_child(node, child_index)

        self._refresh_internal_keys(node)

        return True

    def _rebalance_child(self, parent, index):
        child = parent.children[index]

        left_sibling = parent.children[index - 1] if index > 0 else None
        right_sibling = parent.children[index + 1] if index < len(parent.children) - 1 else None

        if left_sibling is not None and len(left_sibling.keys) > self.min_keys:
            self._borrow_from_left(parent, index)
            return

        if right_sibling is not None and len(right_sibling.keys) > self.min_keys:
            self._borrow_from_right(parent, index)
            return

        if left_sibling is not None:
            self._merge_with_left(parent, index)
        elif right_sibling is not None:
            self._merge_with_right(parent, index)

    def _borrow_from_left(self, parent, index):
        child = parent.children[index]
        left_sibling = parent.children[index - 1]

        if child.is_leaf:
            borrowed_key = left_sibling.keys.pop()
            borrowed_rid = left_sibling.rids.pop()

            child.keys.insert(0, borrowed_key)
            child.rids.insert(0, borrowed_rid)

        else:
            borrowed_child = left_sibling.children.pop()
            borrowed_key = left_sibling.keys.pop()

            child.children.insert(0, borrowed_child)
            child.keys.insert(0, parent.keys[index - 1])

        self._refresh_internal_keys(parent)

    def _borrow_from_right(self, parent, index):
        child = parent.children[index]
        right_sibling = parent.children[index + 1]

        if child.is_leaf:
            borrowed_key = right_sibling.keys.pop(0)
            borrowed_rid = right_sibling.rids.pop(0)

            child.keys.append(borrowed_key)
            child.rids.append(borrowed_rid)

        else:
            borrowed_child = right_sibling.children.pop(0)
            borrowed_key = right_sibling.keys.pop(0)

            child.children.append(borrowed_child)
            child.keys.append(parent.keys[index])

        self._refresh_internal_keys(parent)

    def _merge_with_left(self, parent, index):
        child = parent.children[index]
        left_sibling = parent.children[index - 1]

        if child.is_leaf:
            left_sibling.keys.extend(child.keys)
            left_sibling.rids.extend(child.rids)
            left_sibling.next = child.next

        else:
            separator_key = parent.keys[index - 1]
            left_sibling.keys.append(separator_key)
            left_sibling.keys.extend(child.keys)
            left_sibling.children.extend(child.children)

        parent.children.pop(index)
        parent.keys.pop(index - 1)

    def _merge_with_right(self, parent, index):
        child = parent.children[index]
        right_sibling = parent.children[index + 1]

        if child.is_leaf:
            child.keys.extend(right_sibling.keys)
            child.rids.extend(right_sibling.rids)
            child.next = right_sibling.next

        else:
            separator_key = parent.keys[index]
            child.keys.append(separator_key)
            child.keys.extend(right_sibling.keys)
            child.children.extend(right_sibling.children)

        parent.children.pop(index + 1)
        parent.keys.pop(index)

    def _refresh_internal_keys(self, node):
        if node.is_leaf:
            return

        new_keys = []

        for i in range(1, len(node.children)):
            first_key = self._get_first_key(node.children[i])
            new_keys.append(first_key)

        node.keys = new_keys

    def _get_first_key(self, node):
        current = node

        while not current.is_leaf:
            current = current.children[0]

        return current.keys[0]


    def get_height(self):
        height = 0
        node = self.root

        while not node.is_leaf:
            height += 1
            node = node.children[0]

        return height

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