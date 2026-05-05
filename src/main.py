from student_loader import load_students
from btree import BTree


def main():
    records = load_students("../data/student.csv")

    tree = BTree(d=3)

    for rid, record in enumerate(records):
        key = record["student_id"]
        tree.insert(key, rid)

    print("B-tree insertion finished")
    print("Number of records:", len(records))
    print("Split count:", tree.split_count)

    print("Height:", tree.get_height())
    print("Node count:", tree.count_nodes())
    print("Node utilization:", tree.get_node_utilization())

    test_keys = [
        records[0]["student_id"],
        records[100]["student_id"],
        records[-1]["student_id"],
    ]

    for key in test_keys:
        rid = tree.search(key)
        print("key:", key, "rid:", rid)

        if rid is not None:
            print("found record:", records[rid])


if __name__ == "__main__":
    main()