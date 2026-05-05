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