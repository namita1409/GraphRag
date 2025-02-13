import re


# Base AST node class
class ASTNode:
    def __init__(self, node_type):
        self.node_type = node_type
        self.children = []

    def print_tree(self, indent=0):
        print(" " * indent + f"{self.node_type}")
        # Print additional properties if available
        if hasattr(self, "name"):
            print(" " * (indent + 2) + f"Name: {self.name}")
        if hasattr(self, "dataset_name"):
            print(" " * (indent + 2) + f"Dataset: {self.dataset_name}")
        if hasattr(self, "block"):
            print(" " * (indent + 2) + "Block:")
            for line in self.block:
                print(" " * (indent + 4) + line)
        for child in self.children:
            child.print_tree(indent + 2)


# Program node representing the top-level SAS code file
class ProgramNode(ASTNode):
    def __init__(self):
        super().__init__("Program")


# Macro node representing a SAS macro definition
class MacroNode(ASTNode):
    def __init__(self, name, children, block):
        super().__init__("Macro")
        self.name = name  # the macro name
        self.children = children  # child nodes parsed from within the macro block
        self.block = block  # the full text block of the macro (for reference)


# Data step node representing a SAS DATA step
class DataStepNode(ASTNode):
    def __init__(self, dataset_name, block):
        super().__init__("DataStep")
        self.dataset_name = dataset_name  # name of the dataset (if found)
        self.block = block  # all lines that belong to the DATA step


# ProcSQL node representing a PROC SQL block in SAS
class ProcSQLNode(ASTNode):
    def __init__(self, block):
        super().__init__("ProcSQL")
        self.block = block  # all lines that belong to the PROC SQL block


# The SASParser class reads SAS code and builds the AST
class SASParser:
    def __init__(self, code):
        self.lines = code.splitlines()
        self.index = 0
        self.total_lines = len(self.lines)

    # Main parse method that returns a ProgramNode
    def parse(self):
        program = ProgramNode()
        while self.index < self.total_lines:
            line = self.current_line().strip()
            lower_line = line.lower()
            # Identify a macro block
            if lower_line.startswith("%macro"):
                macro_node = self.parse_macro()
                program.children.append(macro_node)
            # Identify a DATA step block
            elif lower_line.startswith("data "):
                data_node = self.parse_data_step()
                program.children.append(data_node)
            # Identify a PROC SQL block
            elif lower_line.startswith("proc sql"):
                procsql_node = self.parse_proc_sql()
                program.children.append(procsql_node)
            else:
                self.index += 1  # skip lines that don't start a recognized block
        return program

    # Utility to get the current line based on the pointer
    def current_line(self):
        if self.index < self.total_lines:
            return self.lines[self.index]
        return ""

    # Parse a SAS macro from %macro to %mend
    def parse_macro(self):
        start_index = self.index
        line = self.current_line().strip()
        # Extract macro name using regex
        macro_match = re.match(r"%macro\s+(\w+)", line, re.IGNORECASE)
        macro_name = macro_match.group(1) if macro_match else "UnknownMacro"
        self.index += 1
        macro_block = []
        # Collect lines until the macro end marker is found
        while self.index < self.total_lines:
            line = self.current_line()
            if line.strip().lower().startswith("%mend"):
                macro_block.append(line.strip())
                self.index += 1
                break
            else:
                macro_block.append(line)
                self.index += 1
        # Recursively parse the macro's inner contents
        inner_code = "\n".join(macro_block)
        inner_parser = SASParser(inner_code)
        inner_ast = inner_parser.parse()
        macro_node = MacroNode(macro_name, inner_ast.children, macro_block)
        return macro_node

    # Parse a DATA step block from a line starting with "data" until "run;" is found
    def parse_data_step(self):
        block_lines = []
        line = self.current_line().strip()
        block_lines.append(line)
        # Extract the dataset name from the first line (if available)
        dataset_name = "UnknownDataset"
        ds_match = re.match(r"data\s+([\w\.]+)", line, re.IGNORECASE)
        if ds_match:
            dataset_name = ds_match.group(1)
        self.index += 1
        # Continue adding lines until the "run;" statement is encountered
        while self.index < self.total_lines:
            line = self.current_line()
            block_lines.append(line)
            if "run;" in line.lower():
                self.index += 1
                break
            self.index += 1
        return DataStepNode(dataset_name, block_lines)

    # Parse a PROC SQL block from a line starting with "proc sql" until "quit;" is found
    def parse_proc_sql(self):
        block_lines = []
        line = self.current_line().strip()
        block_lines.append(line)
        self.index += 1
        # Continue until the "quit;" statement is encountered
        while self.index < self.total_lines:
            line = self.current_line()
            block_lines.append(line)
            if "quit;" in line.lower():
                self.index += 1
                break
            self.index += 1
        return ProcSQLNode(block_lines)


# Test cases that run the parser and print the resulting AST for verification
if __name__ == "__main__":
    # Test Case 1: SAS code with only a DATA step
    sas_code_data_step = """
data test;
    set source;
    x = 1;
run;
"""
    print("Test Case 1: Data Step Only")
    parser1 = SASParser(sas_code_data_step)
    ast1 = parser1.parse()
    ast1.print_tree()

    print("\n" + "=" * 40 + "\n")

    # Test Case 2: SAS code with a macro that includes a DATA step and a PROC SQL block
    sas_code_macro = """
%macro sample;
    data work.mydata;
        set sashelp.class;
        new_var = age * 2;
    run;

    proc sql;
        create table work.newdata as 
        select name, age, new_var
        from work.mydata
        where age > 15;
    quit;
%mend sample;
"""
    print("Test Case 2: Macro with Data Step and Proc SQL")
    parser2 = SASParser(sas_code_macro)
    ast2 = parser2.parse()
    ast2.print_tree()
