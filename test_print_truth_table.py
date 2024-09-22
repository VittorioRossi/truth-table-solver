from project.ROBDD import ROBDD
from project.parser import parse
from time import time
import os

def print_truth_table(declared_vars, assignments, show_instructions, output_file):
    robdd = ROBDD()

    declared_vars = [var for var in declared_vars if var not in assignments.keys()]

    # create the ROBDDs for the vars we have to show
    results = {var: robdd.build(expr, declared_vars) for var, expr in assignments.items() if var in show_instructions["show"] or var in show_instructions["show_ones"]}

    with open(output_file, 'w') as f:
        for instruction_type, output_vars_list in show_instructions.items():
            for output_vars in output_vars_list:
                # Print table header
                header = " ".join(declared_vars) + " | " + " ".join(output_vars)
                f.write("# " + header + "\n")
                f.write("# " + "-" * len(header) + "\n")

            

                # Generate all possible combinations of truth values
                n = len(declared_vars)
                for i in range(2**n):
                    truth_values = {declared_vars[j]: bool(i & (1 << j)) for j in range(n)}

                    # Evaluate ROBDD for each output variable
                    output_results = [str(int(results[var](truth_values))) for var in output_vars]
                    if instruction_type == "show" or (instruction_type == "show_ones" and any(int(x) for x in output_results)):
                        input_vals = " ".join(str(int(truth_values[var])) for var in declared_vars)
                        output_vals = " ".join(output_results)
                        f.write(f"{input_vals}   {output_vals}\n")
                
                f.write("\n")  # Add a blank line between different show instructions


vezzos = [f for f in os.listdir("./hw01_vezzo/") if f.endswith(".txt")]

for file_path in vezzos:
    input_name = file_path.replace("_output.txt", ".txt")

    file_path = f"./hw01_instances/{input_name}"
    with open(file_path, 'r') as file:
        content = file.read()
        variables, assignments, show_instructions = parse(content)
    
        output_file = f"./hw01_outputs/{input_name.replace('.txt', '_output.txt')}"
        print_truth_table(variables, assignments, show_instructions, output_file)