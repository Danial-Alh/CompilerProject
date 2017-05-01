import ply.yacc as yacc
from lexer import tokens
from lexer import lexer

code = []

start = 'program'

precedence = (
    ('right', 'THEN', 'ELSE'),
)


def p_program(p):
    """program      : PROGRAM ID declarations_list procedure_list MAIN block
                    | PROGRAM ID procedure_list MAIN block
                    | PROGRAM ID declarations_list MAIN block
                    | PROGRAM ID MAIN block"""
    pass


def p_declarations_list(p):
    """declarations_list    : declarations 
                            | declarations_list declarations"""
    pass


def p_declarations(p):
    """declarations     : type_specifiers declarator_list SEMICOLON"""
    pass

def p_type_specifiers(p):
    """type_specifiers      : INT
                            | REAL
                            | CHAR
                            | BOOLEAN"""
    pass

def p_declarator_list(p):
    """declarator_list      : declarator
                            | declarator_list COMMA declarator"""
    if p.slice[1].type == "declarator":
        print(p[1])


def p_declarator(p):
    """declarator       : dec
                        | dec ASSIGNMENT_SIGN initializer"""
    p[0] = {"varibale_info": p[1]}
    p[0]["initializer"] = None
    if len(p) > 2:
        p[0]["initializer"] = p[3]
    pass



def p_dec(p):
    """dec      : ID
                | ID LBRACK range RBRACK
                | ID LBRACK NUMCONST RBRACK"""
    p[0] = p[1]
    pass


def p_range(p):
    """range        : ID DOUBLE_DOT ID
                    | NUMCONST DOUBLE_DOT NUMCONST
                    | arithmetic_expressions DOUBLE_DOT arithmetic_expressions"""
    pass


def p_initializer(p):
    """initializer      : constant_expressions
                        | LBRACE initializer_list RBRACE"""
    p[0] = {}
    if p[1] == "LBRACE":
        p[0]["initializer_type"] = "array_initializer"
    else:
        p[0]["initializer_type"] = "single_initializer"
        p[0]["constant_value"] = p[1]
    pass


def p_initializer_list(p):
    """initializer_list     : constant_expressions COMMA initializer_list
                            | constant_expressions"""
    pass


def p_procedure_list(p):
    """procedure_list       : procedure_list procedure_nt
                            | procedure_nt"""


def p_procedure(p):
    """procedure_nt         : PROCEDURE ID parameters LBRACE declarations_list block RBRACE SEMICOLON
                            | PROCEDURE ID parameters LBRACE block RBRACE SEMICOLON"""
    pass


def p_parameters(p):
    """parameters       : LPAR declarations_list RPAR
                        | LPAR RPAR"""
    pass


def p_block(p):
    """block        : LBRACE statement_list RBRACE"""
    pass


def p_statement_list(p):
    """statement_list       : statement SEMICOLON
                            | statement_list statement SEMICOLON"""
    pass


def p_statement(p):
    """statement            : ID ASSIGNMENT_SIGN expressions
                            | IF bool_expressions THEN statement
                            | IF bool_expressions THEN statement ELSE statement
                            | DO statement WHILE bool_expressions
                            | FOR ID ASSIGNMENT_SIGN counter DO statement
                            | SWITCH expressions case_element default END
                            | ID LPAR arguments_list RPAR
                            | ID LBRACK expressions RBRACK ASSIGNMENT_SIGN expressions
                            | RETURN expressions
                            | EXIT WHEN bool_expressions
                            | block
                            | """
    pass


def p_arguments_list(p):
    """arguments_list       : multi_arguments
                            | """
    pass


def p_multi_arguments(p):
    """multi_arguments      : multi_arguments COMMA expressions 
                            | expressions"""
    pass


def p_counter(p):
    """counter      : NUMCONST UPTO NUMCONST 
                    | NUMCONST DOWNTO NUMCONST"""
    pass


def p_case_element(p):
    """case_element     : CASE NUMCONST COLON block
                        | case_element CASE NUMCONST COLON block"""
    pass


def p_default(p):
    """default      : DEFAULT COLON block 
                    | """
    pass


def p_expressions(p):
    """expressions      : constant_expressions 
                        | bool_expressions 
                        | arithmetic_expressions
                        | ID 
                        | ID LBRACK expressions RBRACK 
                        | ID LPAR arguments_list RPAR 
                        | LPAR expressions RPAR"""
    pass


def p_constant_expressions(p):
    """constant_expressions     : NUMCONST 
                                | REALCONST 
                                | CHARCONST 
                                | BOOLCONST"""
    p[0] = p[1]
    pass


def p_bool_expressions(p):
    """bool_expressions     : LT pair 
                            | LE pair 
                            | GT pair 
                            | GE pair 
                            | EQ pair 
                            | NEQ pair 
                            | AND pair 
                            | OR pair 
                            | AND THEN pair 
                            | OR ELSE pair 
                            | NOT expressions"""
    pass


def p_arithmetic_expressions(p):
    """arithmetic_expressions       : PLUS pair 
                                    | MINUS pair 
                                    | MULT pair 
                                    | DIV pair 
                                    | MOD pair 
                                    | MINUS expressions"""
    pass


def p_pair(p):
    """pair     : LPAR expressions COMMA expressions RPAR"""
    pass


# def p_empty(p):
#     """empty :"""
#     pass


def p_error(p):
    print("Syntax error in input!")
    print(p.lineno)


# Build the parser
parser = yacc.yacc(tabmodule="parsing_table")

code = None
with open('./input.dm', 'r') as input_file:
    code = input_file.read()
result = parser.parse(code, lexer=lexer, debug=False, tracking=True)
