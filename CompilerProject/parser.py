import ply.yacc as yacc
from lexer import lexer, tokens, symbol_table

code = []


def install_id(identifier):
    symbol_table.append(identifier)
    return len(symbol_table) - 1


start = 'program'

precedence = (
    ('right', 'THEN', 'ELSE'),
)


def p_program(p):
    """program      : PROGRAM ID declarations_list procedure_list MAIN block
                    | PROGRAM ID procedure_list MAIN block
                    | PROGRAM ID declarations_list MAIN block
                    | PROGRAM ID MAIN block"""
    return


def p_declarations_list(p):
    """declarations_list    : declarations 
                            | declarations_list declarations"""
    return


def p_declarations(p):
    """declarations     : type_specifiers declarator_list SEMICOLON"""
    # print("**************************************************************")
    for declarator in p[2]["declarations_info"]:
        declarator["type"] = p[1]["type"]
        place = declarator["variable_info"]["place"]
        if place not in symbol_table:
            index = install_id(declarator)
        else:
            print_error("multiple variable \'" + place + "\' declaration!!", p.slice[1])
        declarator["variable_info"]["index"] = index
        # print(declarator)
    return


def p_type_specifiers(p):
    """type_specifiers      : INT
                            | REAL
                            | CHAR
                            | BOOLEAN"""
    p[0] = {"type": p[1]}
    return


def p_declarator_list(p):
    """declarator_list      : declarator
                            | declarator_list COMMA declarator"""
    if p.slice[1].type == "declarator":
        p[0] = {"declarations_info": [p[1]]}
    else:
        p[0] = {"declarations_info": p[1]["declarations_info"] + [p[3]]}
    return


def p_declarator(p):
    """declarator       : dec
                        | dec ASSIGNMENT_SIGN initializer"""
    p[0] = {"variable_info": p[1]}
    p[0]["initializer"] = None
    if len(p) > 2:
        p[0]["initializer"] = p[3]
    return


def p_dec(p):
    """dec      : ID
                | ID LBRACK range RBRACK
                | ID LBRACK NUMCONST RBRACK"""
    p[0] = p[1]
    if len(p) == 2:
        p[0]["is_array"] = False
    else:
        p[0]["is_array"] = True
    return


def p_range(p):
    """range        : ID DOUBLE_DOT ID
                    | NUMCONST DOUBLE_DOT NUMCONST
                    | arithmetic_expressions DOUBLE_DOT arithmetic_expressions"""
    return


def p_initializer(p):
    """initializer      : constant_expressions
                        | LBRACE initializer_list RBRACE"""
    p[0] = {}
    if p.slice[1].type == "LBRACE":
        p[0]["initializer_type"] = "array_initializer"
        p[0]["initial_value"] = p[2]["initial_values"]
    else:
        p[0]["initializer_type"] = "single_initializer"
        p[0]["initial_value"] = [p[1]]
    return


def p_initializer_list(p):
    """initializer_list     : constant_expressions COMMA initializer_list
                            | constant_expressions"""
    if len(p) == 2:
        p[0] = {"initial_values": [p[1]]}
    else:
        p[0] = {"initial_values": [p[1]] + p[3]["initial_values"]}
    return


def p_procedure_list(p):
    """procedure_list       : procedure_list procedure_nt
                            | procedure_nt"""


def p_procedure(p):
    """procedure_nt         : PROCEDURE ID parameters LBRACE declarations_list block RBRACE SEMICOLON
                            | PROCEDURE ID parameters LBRACE block RBRACE SEMICOLON"""
    return


def p_parameters(p):
    """parameters       : LPAR declarations_list RPAR
                        | LPAR RPAR"""
    return


def p_block(p):
    """block        : LBRACE statement_list RBRACE"""
    return


def p_statement_list(p):
    """statement_list       : statement SEMICOLON
                            | statement_list statement SEMICOLON"""
    return


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
    return


def p_arguments_list(p):
    """arguments_list       : multi_arguments
                            | """
    return


def p_multi_arguments(p):
    """multi_arguments      : multi_arguments COMMA expressions 
                            | expressions"""
    return


def p_counter(p):
    """counter      : NUMCONST UPTO NUMCONST 
                    | NUMCONST DOWNTO NUMCONST"""
    return


def p_case_element(p):
    """case_element     : CASE NUMCONST COLON block
                        | case_element CASE NUMCONST COLON block"""
    return


def p_default(p):
    """default      : DEFAULT COLON block 
                    | """
    return


def p_expressions(p):
    """expressions      : constant_expressions 
                        | bool_expressions 
                        | arithmetic_expressions
                        | ID 
                        | ID LBRACK expressions RBRACK 
                        | ID LPAR arguments_list RPAR 
                        | LPAR expressions RPAR"""
    p[0] = {}
    if p.slice[1].type == "ID":
        if not p[1]["declared"]:
            msg = "variable \'" + p[1]["place"] + "\' not declared!!"
            print_error(msg, p.slice[1])
    else:
        return
    return


def p_constant_expressions(p):
    """constant_expressions     : NUMCONST 
                                | REALCONST 
                                | CHARCONST 
                                | BOOLCONST"""
    p[0] = p[1]
    return


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
    return


def p_arithmetic_expressions(p):
    """arithmetic_expressions       : PLUS pair 
                                    | MINUS pair 
                                    | MULT pair 
                                    | DIV pair 
                                    | MOD pair 
                                    | MINUS expressions"""
    return


def p_pair(p):
    """pair     : LPAR expressions COMMA expressions RPAR"""
    return


# def p_empty(p):
#     """empty :"""
#     return


def p_error(p):
    print("Syntax error in input!")
    print(str(p) + str(p.lineno))
    parser.restart()


def print_error(msg, p):
    print(msg + "\tline: " + str(p.lineno))
    raise SyntaxError
    return


# Build the parser
parser = yacc.yacc(tabmodule="parsing_table")
code = None
with open('./input.dm', 'r') as input_file:
    code = input_file.read()
result = parser.parse(code, lexer=lexer, debug=False, tracking=True)
