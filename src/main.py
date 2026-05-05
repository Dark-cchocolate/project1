import time
import random

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

def run_btree_search_experiment(tree, records, num_queries=10000):
    query_records = random.sample(records, num_queries)

    start_time = time.perf_counter()

    found_count = 0

    for record in query_records:
        key = record["student_id"]
        rid = tree.search(key)

        if rid is not None:
            found_count += 1

    end_time = time.perf_counter()

    total_time = end_time - start_time
    mean_time = total_time / num_queries

    print(f"Point search queries: {num_queries}")
    print(f"Found count: {found_count}")
    print(f"Total search time: {total_time:.6f} seconds")
    print(f"Mean search time: {mean_time:.10f} seconds")
    print()

def run_btree_range_query_experiment(tree, records):
    start_key = 202000000
    end_key = 202100000

    start_time = time.perf_counter()

    results = tree.range_query(start_key, end_key)

    male_count = 0
    gpa_sum = 0
    height_sum = 0

    for key, rid in results:
        record = records[rid]

        if record["gender"] == "Male":
            male_count += 1
            gpa_sum += record["gpa"]
            height_sum += record["height"]

    end_time = time.perf_counter()

    total_time = end_time - start_time

    if male_count > 0:
        avg_gpa = gpa_sum / male_count
        avg_height = height_sum / male_count
    else:
        avg_gpa = 0
        avg_height = 0

    print("Range query:")
    print(f"Student ID between {start_key} and {end_key}, Gender = Male")
    print(f"Matched male students: {male_count}")
    print(f"Average GPA: {avg_gpa:.4f}")
    print(f"Average height: {avg_height:.4f}")
    print(f"Range query time: {total_time:.6f} seconds")
    print()


def main():
    records = load_students("../data/student.csv")

    print("Number of records:", len(records))
    print("=== B-tree Insertion Experiment ===")

    for d in [3, 5, 10]:
        tree = run_btree_insertion_experiment(records, d)

        print("=== B-tree Point Search Experiment ===")
        run_btree_search_experiment(tree, records, num_queries=10000)

        print("=== B-tree Range Query Experiment ===")
        run_btree_range_query_experiment(tree, records)


if __name__ == "__main__":
    main()