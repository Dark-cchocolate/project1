import time

from student_loader import load_students
from btree import BTree


def run_btree_insertion_experiment(records, d):
    tree = BTree(d=d)

    start_time = time.perf_counter()

    for rid, record in enumerate(records):
        key = record["student_id"]
        tree.insert(key, rid)

    end_time = time.perf_counter()
    insertion_time = end_time - start_time

    print(f"d = {d}")
    print(f"Insertion time: {insertion_time:.6f} seconds")
    print(f"Split count: {tree.split_count}")
    
    print(f"Height: {tree.get_height()}")
    print(f"Node count: {tree.count_nodes()}")
    print(f"Node utilization: {tree.get_node_utilization():.6f}")
    print()

    return tree


def main():
    records = load_students("../data/student.csv")

    print("Number of records:", len(records))
    print("=== B-tree Insertion Experiment ===")

    for d in [3, 5, 10]:
        run_btree_insertion_experiment(records, d)


if __name__ == "__main__":
    main()