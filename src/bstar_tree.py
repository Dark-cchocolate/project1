from btree import BTree, BTreeNode


class BStarTree(BTree):
    def __init__(self, d):
        super().__init__(d)
        self.redistribution_count = 0
        self.two_to_three_split_count = 0

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
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1

            if len(node.children[i].keys) == self.max_keys:
                handled = self._handle_full_child(node, i)

                if not handled:
                    self._split_child(node, i)

                # Important:
                # redistribution or 2-to-3 split changes parent.keys,
                # so the child index must be recomputed.
                i = 0
                while i < len(node.keys) and key > node.keys[i]:
                    i += 1

                # Safety fallback: if the target child is still full,
                # split it using the normal B-tree split.
                if len(node.children[i].keys) == self.max_keys:
                    self._split_child(node, i)

                    i = 0
                    while i < len(node.keys) and key > node.keys[i]:
                        i += 1

            self._insert_non_full(node.children[i], key, rid)

    def _handle_full_child(self, parent, index):
        # Try redistribution with left sibling.
        if index > 0 and len(parent.children[index - 1].keys) < self.max_keys:
            self._redistribute_with_left(parent, index)
            self.redistribution_count += 1
            return True

        # Try redistribution with right sibling.
        if index < len(parent.children) - 1 and len(parent.children[index + 1].keys) < self.max_keys:
            self._redistribute_with_right(parent, index)
            self.redistribution_count += 1
            return True

        # If both siblings are full, try 2-to-3 split with right sibling.
        if index < len(parent.children) - 1:
            self._split_two_to_three(parent, index)
            self.two_to_three_split_count += 1
            return True

        # Otherwise try 2-to-3 split with left sibling.
        if index > 0:
            self._split_two_to_three(parent, index - 1)
            self.two_to_three_split_count += 1
            return True

        return False

    def _redistribute_with_left(self, parent, index):
        child = parent.children[index]
        left = parent.children[index - 1]

        all_keys = left.keys + [parent.keys[index - 1]] + child.keys
        all_rids = left.rids + [parent.rids[index - 1]] + child.rids

        mid = len(all_keys) // 2

        left.keys = all_keys[:mid]
        left.rids = all_rids[:mid]

        parent.keys[index - 1] = all_keys[mid]
        parent.rids[index - 1] = all_rids[mid]

        child.keys = all_keys[mid + 1:]
        child.rids = all_rids[mid + 1:]

        if not child.is_leaf:
            all_children = left.children + child.children
            left.children = all_children[:len(left.keys) + 1]
            child.children = all_children[len(left.keys) + 1:]

    def _redistribute_with_right(self, parent, index):
        child = parent.children[index]
        right = parent.children[index + 1]

        all_keys = child.keys + [parent.keys[index]] + right.keys
        all_rids = child.rids + [parent.rids[index]] + right.rids

        mid = len(all_keys) // 2

        child.keys = all_keys[:mid]
        child.rids = all_rids[:mid]

        parent.keys[index] = all_keys[mid]
        parent.rids[index] = all_rids[mid]

        right.keys = all_keys[mid + 1:]
        right.rids = all_rids[mid + 1:]

        if not child.is_leaf:
            all_children = child.children + right.children
            child.children = all_children[:len(child.keys) + 1]
            right.children = all_children[len(child.keys) + 1:]

    def _split_two_to_three(self, parent, index):
        left = parent.children[index]
        right = parent.children[index + 1]

        all_keys = left.keys + [parent.keys[index]] + right.keys
        all_rids = left.rids + [parent.rids[index]] + right.rids

        if not left.is_leaf:
            all_children = left.children + right.children
        else:
            all_children = []

        new_node = BTreeNode(is_leaf=left.is_leaf)

        total = len(all_keys)
        one_third = total // 3
        two_third = (2 * total) // 3

        left.keys = all_keys[:one_third]
        left.rids = all_rids[:one_third]

        promote_key_1 = all_keys[one_third]
        promote_rid_1 = all_rids[one_third]

        new_node.keys = all_keys[one_third + 1:two_third]
        new_node.rids = all_rids[one_third + 1:two_third]

        promote_key_2 = all_keys[two_third]
        promote_rid_2 = all_rids[two_third]

        right.keys = all_keys[two_third + 1:]
        right.rids = all_rids[two_third + 1:]

        if not left.is_leaf:
            left.children = all_children[:len(left.keys) + 1]

            start = len(left.keys) + 1
            end = start + len(new_node.keys) + 1
            new_node.children = all_children[start:end]

            right.children = all_children[end:]

        parent.keys[index] = promote_key_1
        parent.rids[index] = promote_rid_1

        parent.keys.insert(index + 1, promote_key_2)
        parent.rids.insert(index + 1, promote_rid_2)
        parent.children.insert(index + 1, new_node)

        self.split_count += 1