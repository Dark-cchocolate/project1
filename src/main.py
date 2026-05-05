from student_loader import load_students


def main():
    records = load_students("../data/student.csv")

    print("Number of records:", len(records))
    print("First record:", records[0])


if __name__ == "__main__":
    main()