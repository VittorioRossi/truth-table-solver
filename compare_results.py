import sys

def read_truth_table(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    table = []
    for line in lines:
        row = [int(bit) for bit in line.strip().split()]
        table.append(row)
    
    return table

def compare_truth_tables(table1, table2):
    if len(table1) != len(table2):
        return False
    
    for row1, row2 in zip(table1, table2):
        if row1 != row2:
            return False
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <file1> <file2>")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    table1 = read_truth_table(file1)
    table2 = read_truth_table(file2)

    if compare_truth_tables(table1, table2):
        print("The truth tables are the same.")
    else:
        print("The truth tables are different.")

if __name__ == "__main__":
    main()