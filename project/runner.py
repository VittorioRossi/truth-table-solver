from project.parser import parse
from project.ROBDD import ROBDD
from itertools import product


class CodeInterpreter:
    """
    Main entrypoint of the code, this class is responsible for reading the file, parsing the content
    and building the ROBDDs for all required assignments at once.

    The class also provides methods to show the truthtable for all assignments, show the truthtable for

    The output of the show methdos is:

    # A B C | X Y
    # ----------- 
      0 0 0   1 0
      0 0 1   0 1
      0 1 0   1 0
      0 1 1   0 1
      1 0 0   1 0
    """


    def __init__(self, file) -> None:
        self.file_content = self._read_file(file)
        self.variables, self.assignments, self.show_instructions = self._parse_content()

        self.trees = {}

    
    def interpet(self, reduce = True):
        """
        Interprets and executes the instructions for building and showing ROBDDs.

        This method iterates over the instructions specified in `self.show_instructions` 
        and executes the appropriate method based on the instruction type.

        Raises:
            ValueError: If an invalid instruction type is encountered.
        """

        # populate the trees dictionary with the ROBDDs for all required assignments
        self._build_robdds(reduce=reduce)

        for instruction_type, output_vars_list in self.show_instructions:
            # we iterate over the declared variables and build the tree
            # for every set of shows in the instructions

            # if the instruction is show or show_ones
            if instruction_type == "show":
                # we build the trees for the assignments in this show and then evaluate them
                self._show_lazy(output_vars_list)
            elif instruction_type == "show_ones":

                self._show_ones(output_vars_list)
            else:
                raise ValueError("Invalid instruction type")

    # Build ROBDDs for all required assignment at once
    def _build_robdds(self, reduce = True):
        robdd = ROBDD()
        # _ takes in the show or show_ones and the name of the variable is in name
        # we take the assignment corresponding to the name and build the robdd
        # so we can evaluate it later
        for show_type, names in self.show_instructions:
            for name in names:
                expr = self.assignments[name]
                self.trees[name] = robdd.build(expr, self.variables, reduce=False)
                # we reduce the tree with the show_ones flag if showing ones otherwise we normally reduce
                self.trees[name].reduce(show_type == 'show_ones') 
        
    def _show(self):
        return
    

    def _show_ones(self, output_vars_list):
        all_vars = self.variables  # Use the original order of variables
        
        print(self._create_header(all_vars, output_vars_list))

        # Get assignments leading to one for all output variables
        all_assignments = set()
        for output_var in output_vars_list:
            one_assignments = self.trees[output_var].get_complete_assignments_to_one()
            all_assignments.update(tuple((var, assignment[var]) for var in all_vars) for assignment in one_assignments)

        # Convert back to dictionaries and sort based on the original variable order
        all_assignments = [dict(assignment) for assignment in all_assignments]
        all_assignments.sort(key=lambda x: tuple(x[var] for var in all_vars))

        # Print the assignments
        for assignment in all_assignments:
            output_results = [self.trees[var].evaluate(assignment) for var in output_vars_list]
            print(self._create_line(assignment, output_results))



    # blindly evaluates all assignments regardless of the expression 
    # form and then passes those to the evaluate to perform computations
    def _show_lazy(self, output_vars_list):
        combinations = self._generate_assignments(self.variables)
        
        # print header
        print(self._create_header(self.variables, output_vars_list))

        for comb in combinations:
            assingment_results = []

            # for every var in the assignment
            for output_vars_list in self.trees.keys():
                res = self.trees[output_vars_list].evaluate(comb)
                assingment_results.append(res)
            
            #print line
            print(self._create_line(comb, assingment_results))
    
    def _show_ones_lazy(self, output_vars_list):
        combinations = self._generate_assignments(self.variables)

        # print header
        print(self._create_header(self.variables, output_vars_list))

        for comb in combinations:
            # for every var in the assignment 
            # we evaluate the tree and if the result is 1 we print the line
            assingment_results = [self.trees[output_vars_list].evaluate(comb) for output_vars_list in self.trees.keys()]

            if any(assingment_results):
                print(self._create_line(comb, assingment_results))

    def _create_header(self, variables, output_vars):
        return "# " + " ".join(variables) + " | " + " ".join(output_vars)

    def _create_line(self, truth_values, output_results):
        return f"  " + " ".join(str(int(tv)) for tv in truth_values.values()) + "   " + " ".join(str(int(x)) for x in output_results)

    def _generate_assignments(self, variables):
        return [dict(zip(variables, values)) for values in product([0, 1], repeat=len(variables))]
    
    def _read_file(self, file):
        with open(file, 'r') as file:
            return file.read()
        
    def _parse_content(self):
        return parse(self.file_content)