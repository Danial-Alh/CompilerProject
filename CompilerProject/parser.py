import ply.yacc as yacc
from lexer import lexer, tokens
from assets import symbol_table, code_array

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
    for declarator in p[2]["declarations_info"]:
        declarator["variable_info"]["type"] = p[1]["type"]
        place = declarator["variable_info"]["place"]
        if place not in symbol_table:
            index = symbol_table.install_id(declarator)
            declarator["variable_info"]["declared"] = True
            declarator["variable_info"]["index"] = index
        else:
            print_error("multiple variable \'" + place + "\' declaration!!", p.slice[1])
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
    p[0] = p[1]
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
        p[0]["variable_info"]["is_array"] = False
    else:
        p[0]["variable_info"]["is_array"] = True
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
    if p.slice[1].type == "ID":
        if not p[1]["variable_info"]["declared"]:
            msg = "variable \'" + p[1]["variable_info"]["place"] + "\' not declared!!"
            print_error(msg, p.slice[1])
        p[1]["variable_info"]["array_index_variable"] = p[3]["variable_info"]
        p[0] = p[1]
    elif p.slice[1].type == "constant_expressions":
        p[0] = symbol_table.get_new_temp_variable()
        new_code_entry = code_array.get_new_entry("=", p[0], p[1], None, None)
        code_array.append(new_code_entry)
    elif p.slice[1].type == "LPAR":
        p[0] = p[2]
    else:
        p[0] = p[1]
    return


def p_constant_expressions(p):
    """constant_expressions     : NUMCONST 
                                | REALCONST 
                                | CHARCONST 
                                | BOOLCONST"""
    p[0] = p[1]
    return


def p_bool_expressions_comparator(p):
    """bool_expressions     : LT pair 
                            | LE pair 
                            | GT pair 
                            | GE pair 
                            | EQ pair 
                            | NEQ pair"""
    p[0] = {"t_list": [code_array.get_next_quad_index() + 1],
            "f_list": [code_array.get_next_quad_index() + 2]}
    opt = p.slice[1].type
    if opt == "EQ":
        opt = "=="
    elif opt == "NEQ":
        opt = "!="
    else:
        opt = p[1]
    code_array.append(code_array.get_new_entry(opt, None, p[2]["first_arg"], p[2]["second_arg"], None))
    code_array.append(code_array.get_new_entry("goto", None, None, None, None))
    code_array.append(code_array.get_new_entry("goto", None, None, None, None))
    return


def p_bool_expressions_and(p):
    """bool_expressions     : AND pair"""
    first_arg = p[2]["first_arg"]
    second_arg = p[2]["second_arg"]
    if "t_list" not in first_arg and "t_list" not in second_arg:
        code_array.create_simple_if_check(first_arg)
        code_array.create_simple_if_check(second_arg)
    elif "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    elif "t_list" not in second_arg:
        code_array.create_simple_if_check(second_arg)
    temp_var = symbol_table.get_new_temp_variable()
    code_array.backpatch_e_list(first_arg["t_list"], code_array.get_next_quad_index())
    code_array.append(code_array.get_new_entry('=', temp_var, {"value": "true", "type": "boolean"}, None, None))
    code_array.append(code_array.get_new_entry('goto', None, second_arg["starting_quad_index"], None, None))
    code_array.backpatch_e_list(first_arg["f_list"], code_array.get_next_quad_index())
    code_array.append(code_array.get_new_entry('=', temp_var, {"value": "false", "type": "boolean"}, None, None))
    code_array.append(code_array.get_new_entry('goto', None, second_arg["starting_quad_index"], None, None))
    code_array.backpatch_e_list(second_arg["t_list"], code_array.get_next_quad_index())
    code_array.create_simple_if_check(temp_var)
    p[0] = {"t_list": temp_var["t_list"],
            "f_list": code_array.merge_e_lists(temp_var["f_list"], second_arg["f_list"]),
            "starting_quad_index": first_arg["starting_quad_index"]}
    return


def p_bool_expressions_or(p):
    """bool_expressions     : OR pair"""
    first_arg = p[2]["first_arg"]
    second_arg = p[2]["second_arg"]
    if "t_list" not in first_arg and "t_list" not in second_arg:
        code_array.create_simple_if_check(first_arg)
        code_array.create_simple_if_check(second_arg)
    elif "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    elif "t_list" not in second_arg:
        code_array.create_simple_if_check(second_arg)
    temp_var = symbol_table.get_new_temp_variable()
    code_array.backpatch_e_list(first_arg["t_list"], code_array.get_next_quad_index())
    code_array.append(code_array.get_new_entry('=', temp_var, {"value": "true", "type": "boolean"}, None, None))
    code_array.append(code_array.get_new_entry('goto', None, second_arg["starting_quad_index"], None, None))
    code_array.backpatch_e_list(first_arg["f_list"], code_array.get_next_quad_index())
    code_array.append(code_array.get_new_entry('=', temp_var, {"value": "false", "type": "boolean"}, None, None))
    code_array.append(code_array.get_new_entry('goto', None, second_arg["starting_quad_index"], None, None))
    code_array.backpatch_e_list(second_arg["f_list"], code_array.get_next_quad_index())
    code_array.create_simple_if_check(temp_var)
    p[0] = {"t_list": code_array.merge_e_lists(temp_var["t_list"], second_arg["t_list"]),
            "f_list": temp_var["f_list"],
            "starting_quad_index": first_arg["starting_quad_index"]}
    return


def p_bool_expressions_and_then(p):
    """bool_expressions     : AND THEN pair"""
    first_arg = p[3]["first_arg"]
    second_arg = p[3]["second_arg"]
    if "t_list" not in first_arg and "t_list" not in second_arg:
        code_array.create_simple_if_check(first_arg)
        code_array.create_simple_if_check(second_arg)
    elif "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    elif "t_list" not in second_arg:
        code_array.create_simple_if_check(second_arg)
    code_array.backpatch_e_list(first_arg["t_list"], second_arg["starting_quad_index"])
    p[0] = {"t_list": second_arg["t_list"],
            "f_list": code_array.merge_e_lists(first_arg["f_list"], second_arg["f_list"]),
            "starting_quad_index": first_arg["starting_quad_index"]}
    return


def p_bool_expressions_or_else(p):
    """bool_expressions     : OR ELSE pair"""
    first_arg = p[3]["first_arg"]
    second_arg = p[3]["second_arg"]
    if "t_list" not in first_arg and "t_list" not in second_arg:
        code_array.create_simple_if_check(first_arg)
        code_array.create_simple_if_check(second_arg)
    elif "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    elif "t_list" not in second_arg:
        code_array.create_simple_if_check(second_arg)
    code_array.backpatch_e_list(first_arg["f_list"], second_arg["starting_quad_index"])
    p[0] = {"f_list": second_arg["f_list"],
            "t_list": code_array.merge_e_lists(first_arg["t_list"], second_arg["t_list"]),
            "starting_quad_index": first_arg["starting_quad_index"]}
    return


def p_bool_expressions_not(p):
    """bool_expressions     : NOT expressions"""
    arg = p[2]
    if "t_list" not in arg:
        code_array.create_simple_if_check(arg)
    p[0] = {"t_list": arg["f_list"],
            "f_list": arg["t_list"],
            "starting_quad_index": arg["starting_quad_index"]}
    return


def p_arithmetic_expressions1(p):
    """arithmetic_expressions       : PLUS pair 
                                    | MINUS pair 
                                    | MULT pair 
                                    | DIV pair 
                                    | MOD pair
                                    | MINUS expressions"""
    p[0] = symbol_table.get_new_temp_variable()
    if p.slice[2].type == "expressions":
        first_arg = p[2]
        second_arg = None
    else:
        first_arg = p[2]["first_arg"]
        second_arg = p[2]["second_arg"]
    new_code_entry = code_array.get_new_entry(p[1], p[0], first_arg, second_arg, None)
    code_array.append(new_code_entry)
    return


def p_pair(p):
    """pair     : LPAR expressions COMMA expressions RPAR"""
    p[0] = {"first_arg": p[2], "second_arg": p[4]}
    return


def p_error(p):
    print("Syntax error in input!")
    print(str(p) + str(p.lineno))
    parser.restart()


def print_error(msg, p):
    print(msg + "\tline: " + str(p.lineno))
    # raise SyntaxError
    return


# Build the parser
parser = yacc.yacc(tabmodule="parsing_table")
code = None
with open('./input_boolean.dm', 'r') as input_file:
    code = input_file.read()
result = parser.parse(code, lexer=lexer, debug=False, tracking=True)
code_array.generate_code()
