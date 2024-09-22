import sys
import argparse
from project.ROBDD import ROBDD
from project.parser import parse
import traceback
from time import time

def print_truth_table(declared_vars, assignments, show_instructions):
    robdd = ROBDD()

    declared_vars = [var for var in declared_vars if var not in assignments.keys()]

    results = {var: robdd.build(expr, declared_vars) for var, expr in assignments.items() if var in show_instructions["show"] or var in show_instructions["show_ones"]}

    for instruction_type, output_vars_list in show_instructions.items():
        for output_vars in output_vars_list:
            # Print table header
            header = " ".join(declared_vars) + " | " + " ".join(output_vars)
            print("# " + header)
            print("# " + "-" * len(header))

            # Generate all possible combinations of truth values
            n = len(declared_vars)
            total_time = 0

            for i in range(2**n):
                truth_values = {declared_vars[j]: bool(i & (1 << j)) for j in range(n)}

                start_time = time()
                # Evaluate ROBDD for each output variable
                output_results = [str(int(results[var](truth_values))) for var in output_vars]
                end_time = time()

                total_time += (end_time - start_time)

                if instruction_type == "show" or (instruction_type == "show_ones" and any(int(x) for x in output_results)):
                    input_vals = " ".join(str(int(truth_values[var])) for var in declared_vars)
                    output_vals = " ".join(output_results)
                    print(f"{input_vals} | {output_vals}")

            print(f"Average time to generate output results: {total_time:.6f} seconds")

            print()  # Add a blank line between different show instructions

def main():
    parser = argparse.ArgumentParser(description="Generate truth table from ROBDD input file")
    parser.add_argument("file_path", help="Path to the input file")
    args = parser.parse_args()

    try:
        with open(args.file_path, 'r') as file:
            content = file.read()

        variables, assignments, show_instructions = parse(content)
        print_truth_table(variables, assignments, show_instructions)
    except FileNotFoundError:
        print(f"Error: File '{args.file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()