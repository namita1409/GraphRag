import ply.lex as lex
import ply.yacc as yacc

# ---------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------
# Reserved words in SAS (case-insensitive)
reserved = {
    "data": "DATA",
    "proc": "PROC",
    "set": "SET",
    "run": "RUN",
}

# List of token names
tokens = [
    "ID",
    "SEMICOLON",
    "EQUALS",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "STRING",
    "DOT",
] + list(reserved.values())

# Regular expression rules for simple tokens
t_SEMICOLON = r";"
t_EQUALS = r"="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","
t_DOT = r"\."


# String token (supports simple double- and single-quoted strings)
def t_STRING(t):
    r"(\"([^\\\n]|(\\.))*?\")|(\'([^\\\n]|(\\.))*?\')"
    # Remove quotes for the AST node
    t.value = t.value[1:-1]
    return t


# Identifier (check against reserved words, and allow letter/digit/underscore sequences)
def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    # Use lower case for lookup to allow case-insensitive matching
    t.type = reserved.get(t.value.lower(), "ID")
    return t


# Ignore whitespace and tabs
t_ignore = " \t"


# Newline rule to track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Error handling for illegal characters
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


# ---------------------------------------------------------------------
# AST Node Classes
# ---------------------------------------------------------------------
class ASTNode:
    def __init__(self, node_type):
        self.node_type = node_type

    def __str__(self):
        return f"{self.node_type}"

    __repr__ = __str__


class DataStep(ASTNode):
    def __init__(self, dataset, body):
        super().__init__("DataStep")
        self.dataset = dataset
        self.body = body  # list of statements inside the DATA step

    def __str__(self):
        return f"DataStep(dataset={self.dataset}, body={self.body})"


class SetStatement(ASTNode):
    def __init__(self, dataset):
        super().__init__("SetStatement")
        self.dataset = dataset

    def __str__(self):
        return f"SetStatement(dataset={self.dataset})"


class Assignment(ASTNode):
    def __init__(self, target, value):
        super().__init__("Assignment")
        self.target = target
        self.value = value

    def __str__(self):
        return f"Assignment(target={self.target}, value={self.value})"


class FunctionCall(ASTNode):
    def __init__(self, func, args):
        super().__init__("FunctionCall")
        self.func = func
        self.args = args  # list of expressions

    def __str__(self):
        return f"FunctionCall(func={self.func}, args={self.args})"


class Identifier(ASTNode):
    def __init__(self, name):
        super().__init__("Identifier")
        self.name = name

    def __str__(self):
        return f"Identifier({self.name})"


class StringLiteral(ASTNode):
    def __init__(self, value):
        super().__init__("StringLiteral")
        self.value = value

    def __str__(self):
        return f"StringLiteral({self.value})"


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------
# Program consists of a list of statements
def p_program(p):
    """program : stmt_list"""
    p[0] = p[1]


def p_stmt_list(p):
    """stmt_list : stmt_list stmt
    | stmt"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


# A statement in this simplified grammar is currently just a DATA step.
def p_stmt(p):
    """stmt : data_step"""
    p[0] = p[1]


# DATA step: DATA <dataset_name> ; <data_body> RUN ;
def p_data_step(p):
    "data_step : DATA ID SEMICOLON data_body RUN SEMICOLON"
    p[0] = DataStep(dataset=Identifier(p[2]), body=p[4])


# Data body: a list of statements within the DATA step (e.g., SET and assignments)
def p_data_body(p):
    """data_body : stmt_list_data"""
    p[0] = p[1]


def p_stmt_list_data(p):
    """stmt_list_data : stmt_list_data stmt_data
    | stmt_data"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


# A data step statement can be a SET statement or an assignment statement
def p_stmt_data(p):
    """stmt_data : set_stmt
    | assignment_stmt"""
    p[0] = p[1]


# SET statement. It handles both dotted (qualified) and simple identifiers.
def p_set_stmt_qualified(p):
    "set_stmt : SET qualified_id SEMICOLON"
    p[0] = SetStatement(dataset=p[2])


def p_set_stmt_simple(p):
    "set_stmt : SET ID SEMICOLON"
    p[0] = SetStatement(dataset=Identifier(p[2]))


# Qualified identifier: e.g., library.dataset
def p_qualified_id(p):
    "qualified_id : ID DOT ID"
    p[0] = Identifier(f"{p[1]}.{p[3]}")


# Assignment statement: <identifier> = <expression> ;
def p_assignment_stmt(p):
    "assignment_stmt : ID EQUALS expr SEMICOLON"
    p[0] = Assignment(target=Identifier(p[1]), value=p[3])


# Expression rules
def p_expr_function_call(p):
    "expr : function_call"
    p[0] = p[1]


def p_expr_identifier(p):
    "expr : ID"
    p[0] = Identifier(p[1])


def p_expr_string(p):
    "expr : STRING"
    p[0] = StringLiteral(p[1])


# Function call: identifier ( argument list )
def p_function_call(p):
    "function_call : ID LPAREN expr_arg_list_opt RPAREN"
    p[0] = FunctionCall(func=Identifier(p[1]), args=p[3])


# Optional argument list: could be empty or a nonempty list of expressions.
def p_expr_arg_list_opt(p):
    """expr_arg_list_opt : expr_list
    |"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = []


def p_expr_list_single(p):
    "expr_list : expr"
    p[0] = [p[1]]


def p_expr_list_multiple(p):
    "expr_list : expr_list COMMA expr"
    p[0] = p[1] + [p[3]]


# Error rule for syntax errors
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}, value {p.value} at line {p.lineno}")
    else:
        print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()


# ---------------------------------------------------------------------
# Helper function to pretty-print the AST
# ---------------------------------------------------------------------
def print_ast(node, indent=0):
    pad = "  " * indent
    if isinstance(node, list):
        for subnode in node:
            print_ast(subnode, indent)
    elif isinstance(node, ASTNode):
        print(f"{pad}{node.node_type}:", end=" ")
        if isinstance(node, Identifier):
            print(node.name)
        elif isinstance(node, StringLiteral):
            print(f"'{node.value}'")
        elif isinstance(node, DataStep):
            print(f"(dataset = {node.dataset.name})")
            print_ast(node.body, indent + 1)
        elif isinstance(node, SetStatement):
            print(f"(dataset = {node.dataset.name})")
        elif isinstance(node, Assignment):
            print()
            print(f"{pad}  Target:")
            print_ast(node.target, indent + 2)
            print(f"{pad}  Value:")
            print_ast(node.value, indent + 2)
        elif isinstance(node, FunctionCall):
            print(f"(func: {node.func.name})")
            print(f"{pad}  Args:")
            print_ast(node.args, indent + 2)
        else:
            print()
    else:
        print(f"{pad}{node}")


# ---------------------------------------------------------------------
# Testing with example SAS code
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Example SAS code snippet that includes a DATA step.
    test_code = """
    data class;
      set sashelp.class;
      name = catx('-', name, eof);
    run;
    """
    ast_result = parser.parse(test_code)
    print("Abstract Syntax Tree:")
    print_ast(ast_result)
