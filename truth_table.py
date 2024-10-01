import sys
import argparse
from project.ROBDD import ROBDD
from project.parser import parse
import traceback
from time import time
from itertools import product

def print_truth_table(declared_vars, assignments, show_instructions):
    robdd = ROBDD()

    # Build ROBDDs for all required variables at once
    results = {var: robdd.build(expr, declared_vars) for var, expr in assignments.items() 
               if var in show_instructions["show"] or var in show_instructions["show_ones"]}

    for instruction_type, output_vars_list in show_instructions.items():
        for output_vars in output_vars_list:
            # Print table header
            header = " ".join(declared_vars) + " | " + " ".join(output_vars)
            print("# " + header)
            print("# " + "-" * len(header))

            # Generate all possible combinations of truth values
            truth_value_combinations = list(product([False, True], repeat=len(declared_vars)))

            for truth_values in truth_value_combinations:
                truth_dict = dict(zip(declared_vars, truth_values))

                # Evaluate ROBDD for each output variable
                output_results = [str(int(results[var](truth_dict))) for var in output_vars]

                if instruction_type == "show" or (instruction_type == "show_ones" and any(int(x) for x in output_results)):
                    input_vals = " ".join(str(int(tv)) for tv in truth_values)
                    output_vals = " ".join(output_results)
                    print(f"{input_vals}   {output_vals}")

            print()  # Add a blank line between different show instructions

def main(file_path=None):
    if file_path is None:
        parser = argparse.ArgumentParser(description="Generate truth table from ROBDD input file")
        parser.add_argument("file_path", help="Path to the input file")
        args = parser.parse_args()
        file_path = args.file_path

    try:
        with open(file_path, 'r') as file:
            content = file.read()

        variables, assignments, show_instructions = parse(content)
        print_truth_table(variables, assignments, show_instructions)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()