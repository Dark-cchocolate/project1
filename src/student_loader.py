import csv


def load_students(csv_path):
    records = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            record = {
                "student_id": int(row["Student ID"]),
                "name": row["Name"],
                "gender": row["Gender"],
                "gpa": float(row["GPA"]),
                "height": float(row["Height"]),
                "weight": float(row["Weight"]),
            }
            records.append(record)

    return records