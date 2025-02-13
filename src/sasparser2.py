import ply.lex as lex
import ply.yacc as yacc

# ---------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------
reserved = {
    "data": "DATA",
    "proc": "PROC",
    "sql": "SQL",
    "quit": "QUIT",
    "create": "CREATE",
    "table": "TABLE",
    "select": "SELECT",
    "from": "FROM",
    "where": "WHERE",
    "as": "AS",
    "set": "SET",
    "run": "RUN",
}

tokens = [
    "ID",
    "SEMICOLON",
    "COMMA",
    "DOT",
    "GREATER",
    "NUMBER",
    "STRING",
    "EQUALS",
    "LPAREN",
    "RPAREN",
] + list(reserved.values())

t_SEMICOLON = r";"
t_COMMA = r","
t_DOT = r"\."
t_GREATER = r">"


def t_NUMBER(t):
    r"\d+(\.\d+)?"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


def t_STRING(t):
    r"\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\'"
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value.lower(), "ID")
    return t


t_ignore = " \t"


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


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


class ProcSQL(ASTNode):
    def __init__(self, query):
        super().__init__("ProcSQL")
        self.query = query

    def __str__(self):
        return f"ProcSQL(query={self.query})"


class StringLiteral(ASTNode):
    def __init__(self, value):
        super().__init__("StringLiteral")
        self.value = value

    def __str__(self):
        return f"StringLiteral({self.value})"


class SQLQuery(ASTNode):
    def __init__(self, create_table, select_clause, from_clause, where_clause=None):
        super().__init__("SQLQuery")
        self.create_table = create_table
        self.select_clause = select_clause
        self.from_clause = from_clause
        self.where_clause = where_clause

    def __str__(self):
        return f"SQLQuery(create_table={self.create_table}, select={self.select_clause}, from={self.from_clause}, where={self.where_clause})"


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------
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


def p_stmt(p):
    """stmt : data_step
    | proc_sql"""
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


def p_proc_sql(p):
    """proc_sql : PROC SQL SEMICOLON sql_query QUIT SEMICOLON"""
    p[0] = ProcSQL(query=p[4])


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


def p_sql_query(p):
    """sql_query : CREATE TABLE ID AS select_stmt"""
    p[0] = SQLQuery(
        create_table=p[3],
        select_clause=p[5].get("select"),
        from_clause=p[5].get("from"),
        where_clause=p[5].get("where"),
    )


def p_select_stmt(p):
    """select_stmt : SELECT select_list FROM ID where_clause_opt"""
    p[0] = {"select": p[2], "from": p[4], "where": p[5]}


def p_select_list(p):
    """select_list : select_list COMMA ID
    | ID"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_where_clause_opt(p):
    """where_clause_opt : WHERE condition
    |"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None


def p_condition(p):
    """condition : ID GREATER NUMBER"""
    p[0] = (p[1], ">", p[3])


def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}, value {p.value} at line {p.lineno}")
        parser.errok()
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()

# ---------------------------------------------------------------------
# Testing with PROC SQL Example
# ---------------------------------------------------------------------
if __name__ == "__main__":
    test_code_proc_sql = """
proc sql;
   create table work.class_summary as
   select name, age, height
   from sashelp.class
   where age > 12;
quit;
"""

    ast_result_proc_sql = parser.parse(test_code_proc_sql)

    def print_ast(node, indent=0):
        pad = "  " * indent
        if isinstance(node, list):
            for subnode in node:
                print_ast(subnode, indent)
        elif isinstance(node, ASTNode):
            print(f"{pad}{node.node_type}:", end=" ")
            if isinstance(node, ProcSQL):
                print(f"(query: {node.query})")
                print_ast(node.query, indent + 2)
            elif isinstance(node, SQLQuery):
                print(f"(create_table: {node.create_table})")
                print(f"{pad}  Select: {node.select_clause}")
                print(f"{pad}  From: {node.from_clause}")
                if node.where_clause:
                    print(f"{pad}  Where: {node.where_clause}")
            else:
                print()
        else:
            print(f"{pad}{node}")

    print("Abstract Syntax Tree for PROC SQL:")
    print_ast(ast_result_proc_sql)
