# CSE321 Project 1: Implementation and Analysis of B-tree Index Structures

## Overview

This project implements and evaluates three tree-based index structures for CSE321 Project #1:

- B-tree
- B+tree
- B*tree

The project uses the provided student record dataset. Each student ID is used as the search key, and the array index of each loaded record is used as the Record Identifier (RID).

The implementation supports insertion, point search, range query, deletion, and experimental evaluation for all three tree structures.

## Environment

- Language: Python
- Python version: Python 3.14.4
- External dependencies: None

Only Python standard libraries are used.

## Project Structure

```text
project1/
├── data/
│   └── student.csv
├── src/
│   ├── main.py
│   ├── student_loader.py
│   ├── btree.py
│   ├── bplus_tree.py
│   └── bstar_tree.py
├── results/
│   ├── final_results.txt
│   └── results.csv
├── .gitignore
└── README.md
```

## Dataset

Place the provided CSV file in the following location:

```text
data/student.csv
```

The program expects the dataset to contain 100,000 student records.

Each record is loaded into an in-memory array. The student ID is used as the key, and the index of the record in the array is used as the RID.

## Compilation

No separate compilation step is required because the project is written in Python.

## How to Run

From the project root directory, move into the `src` directory:

```bash
cd src
```

Then run:

```bash
python main.py
```

If your system uses `python3` instead of `python`, run:

```bash
python3 main.py
```

## Output

When the program runs, it prints the experimental results to the console.

It also automatically saves the summarized results to:

```text
results/results.csv
```

The `results` directory is created automatically if it does not already exist.

The file `results/final_results.txt` contains the reference experimental output used in the submitted report. In contrast, `results/results.csv` is generated or overwritten whenever `main.py` is executed.

Because the search and deletion workloads use randomly sampled records, and because execution time depends on the runtime environment, some values in `results.csv` may change between runs.

## Implemented Index Structures

### B-tree

The B-tree supports:

- Search
- Insert
- Delete
- Range query
- Height measurement
- Node count measurement
- Node utilization measurement

In this implementation, `d` is used as the minimum degree of the tree.

For B-tree nodes:

- Minimum number of keys in a non-root node: `d - 1`
- Maximum number of keys in a node: `2d - 1`

Internal nodes may store key-RID pairs, and search may terminate at an internal node.

### B+tree

The B+tree supports:

- Search
- Insert
- Delete
- Range query
- Height measurement
- Node count measurement
- Node utilization measurement

In the B+tree implementation:

- Internal nodes store only keys and child pointers.
- RIDs are stored only in leaf nodes.
- Search always descends to a leaf node.
- Leaf nodes are connected using linked pointers.
- Range queries are performed by locating the starting leaf node and then following the linked leaf pointers.

### B*tree

The B*tree is implemented by extending the B-tree implementation.

The B*tree supports:

- Search
- Insert
- Delete
- Range query
- Height measurement
- Node count measurement
- Node utilization measurement

During insertion, the B*tree attempts the following before performing a regular split:

1. Redistribute keys with the left sibling if possible.
2. Redistribute keys with the right sibling if possible.
3. If redistribution is not possible, perform a 2-to-3 split.

The program also reports:

- Redistribution count
- 2-to-3 split count
- Maximum-key violation count for validation

## Experiments

The program automatically runs all experiments for the following order parameters:

```text
d = 3, 5, 10
```

The same workloads are executed on B-tree, B+tree, and B*tree.

### 1. Insertion Experiment

All 100,000 records are inserted into an initially empty tree.

Measured metrics:

- Insertion time
- Split count
- Tree height
- Node count
- Node utilization

Additional B*tree metrics:

- Redistribution count
- 2-to-3 split count
- Maximum-key violation count

### 2. Point Search Experiment

The program randomly selects 10,000 student IDs from the dataset and searches for them.

Measured metrics:

- Number of search queries
- Found count
- Total search time
- Mean search time

### 3. Range Query Experiment

The program executes the following analytical range query:

```text
Calculate the average GPA and average height of male students
whose student IDs are between 202000000 and 202100000.
```

Measured metrics:

- Number of matched male students
- Average GPA
- Average height
- Range query execution time

### 4. Deletion Experiment

The program randomly selects 2,000 records and deletes them from the tree.

Measured metrics:

- Deletion time
- Deleted count
- Number of deleted keys not found after deletion
- Tree height after deletion
- Node count after deletion
- Node utilization after deletion

The deletion experiment also checks whether deleted keys are no longer searchable after deletion.

## Result File Format

```markdown
After execution, `results/results.csv` contains one row for each tree type and order parameter.

The values in `results.csv` represent the output of the most recent execution. The report tables are based on the saved reference output in `results/final_results.txt`.

The CSV columns are:

```text
tree,
d,
insertion_time,
split_count,
redistribution_count,
two_to_three_split_count,
height,
node_count,
node_utilization,
search_found_count,
search_total_time,
search_mean_time,
range_matched_male_count,
range_avg_gpa,
range_avg_height,
range_query_time,
deleted_count,
deleted_not_found_count,
deletion_time,
height_after_deletion,
node_count_after_deletion,
node_utilization_after_deletion
```

## Correctness Checks

The program performs basic correctness checks during the experiments:

- Point search should find all 10,000 randomly selected existing keys.
- Range query results should be consistent across B-tree, B+tree, and B*tree.
- After deletion, all deleted keys should no longer be searchable.
- For B*tree, maximum-key violations are checked after insertion.

## Notes

The values in `results/final_results.txt` are the reference results used in the submitted report.

The file `results/results.csv` is automatically generated from the most recent run of `main.py`. Since random samples are used for search and deletion workloads, and execution time depends on the runtime environment, some values may differ slightly between runs.

Execution times should be interpreted together with structural metrics such as height, node count, split count, and node utilization.
