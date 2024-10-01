import sys
from project.runner import CodeInterpreter

def main(file_path):
    CodeInterpreter(file_path).interpet()
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python truth_table.py <input_file>")
    else:
        main(sys.argv[1])