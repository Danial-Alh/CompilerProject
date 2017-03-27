import lexer
import ply.yacc as yacc
from lexer import tokens

start = 'program'


def p_program(p):
    """program    : PROGRAM ID declarations_list procedure_list MAIN block"""
    pass


def p_declarations_list(p):
    """declarations_list    : declarations 
                            | declarations_list declarations"""
    pass


def p_declarations(p):
    """declarations     : type_specifiers declarator_list SEMICOLON
                        | empty"""
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
    pass


def p_declarator(p):
    """declarator       : dec
                        | dec ASSIGNMENT_SIGN initializer"""
    pass


def p_dec(p):
    """dec      : ID
                | ID LBRACK range RBRACK
                | ID LBRACK NUMCONST RBRACK"""
    pass


def p_range(p):
    """range        : ID DOUBLE_DOT ID
                    | NUMCONST DOUBLE_DOT NUMCONST
                    | arithmetic_expressions DOUBLE_DOT arithmetic_expressions"""
    pass


def p_initializer(p):
    """initializer      : constant_expressions
                        | LBRACE initializer_list RBRACE"""
    pass


def p_initializer_list(p):
    """initializer_list     : constant_expressions COMMA initializer_list
                            | constant_expressions"""
    pass


def p_procedure_list(p):
    """procedure_list       : procedure_list procedure
                            | empty"""


def p_procedure(p):
    """procedure        : PROCEDURE ID parameters LBRACE declarations_list block RBRACE SEMICOLON"""
    pass


def p_parameters(p):
    """parameters       : LPAR declarations_list RPAR"""
    pass


def p_block(p):
    """block        : LBRACE statement_list RBRACE"""
    pass


def p_statement_list(p):
    """statement_list       : statement SEMICOLON
                            | statement_list statement SEMICOLON"""
    pass


# def p_(p):
#     """"""
#     pass


def p_empty(p):
    """empty :"""
    pass


def p_error(p):
    print("Syntax error in input!")


# Build the parser
parser = yacc.yacc()

while True:
    try:
        s = raw_input('input.dm > ')
    except EOFError:
        break
    if not s: continue
    result = parser.parse(s, lexer=(lexer.lexer), debug=True)
    print(result)
