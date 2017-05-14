import re
import ply.yacc as yacc
from lexer import tokens, lexer
from assets import symbol_table, code_array, CodeGenerator

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
        declarator["type"] = p[1]["type"]
        place = declarator["place"]
        if place not in symbol_table:
            index = symbol_table.install_id(declarator)
            declarator["declared"] = True
            declarator["index"] = index
            code_array.initialize_variable(declarator)
        else:
            print_error("multiple variable \'" + place + "\' declaration!!", p.slice[1])
    return


def p_type_specifiers(p):
    """type_specifiers      : INT
                            | REAL
                            | CHAR
                            | BOOLEAN"""
    if p[1] == "boolean":
        p[1] = "bool"
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
        p[0]["is_array"] = False
    else:
        p[0]["is_array"] = True
        if p.slice[3].type == "range":
            p[0]["range"] = p[3]
        if p.slice[3].type == "NUMCONST":
            from_variable = {"value": 1, "type": "int"}
            to_variable = p[3]
            p[0]["range"] = {"from": from_variable, "to": to_variable}
        array_size_variable = symbol_table.get_new_temp_variable("int")
        code_array.emit("-", array_size_variable, p[0]["range"]["to"], p[0]["range"]["from"])
        p[0]["array_size"] = array_size_variable
    return


def p_range(p):
    """range        : ID DOUBLE_DOT ID
                    | NUMCONST DOUBLE_DOT NUMCONST
                    | arithmetic_expressions DOUBLE_DOT arithmetic_expressions"""
    p[0] = {"from": p[1], "to": p[3]}
    return


def p_initializer(p):
    """initializer      : constant_expressions
                        | LBRACE initializer_list RBRACE"""
    p[0] = {}
    if p.slice[1].type == "LBRACE":
        p[0]["initializer_type"] = "array_iniitalizer"
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
        if not p[1]["declared"]:
            msg = "variable \'" + p[1]["place"] + "\' not declared!!"
            print_error(msg, p.slice[1])
        p[0] = p[1]
        if len(p) == 5 and p.slice[3].type == "expressions":
            p[0]["array_index"] = p[3]
    elif p.slice[1].type == "constant_expressions":
        p[0] = p[1]
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
            "f_list": [code_array.get_next_quad_index() + 2],
            "starting_quad_index": code_array.get_next_quad_index(),
            "type": "bool"}
    opt = p.slice[1].type
    if opt == "EQ":
        opt = "=="
    elif opt == "NEQ":
        opt = "!="
    else:
        opt = p[1]
    code_array.emit(opt, None, p[2]["first_arg"], p[2]["second_arg"])
    code_array.emit("goto", None, None, None)
    code_array.emit("goto", None, None, None)
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
    temp_var = symbol_table.get_new_temp_variable("bool")
    code_array.emit('=', temp_var, {"value": 1, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["t_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, second_arg["starting_quad_index"], None)
    code_array.emit('=', temp_var, {"value": 0, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["f_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, second_arg["starting_quad_index"], None)
    code_array.create_simple_if_check(temp_var)
    code_array.backpatch_e_list(second_arg["t_list"], code_array.get_current_quad_index() - 2)
    p[0] = {"t_list": temp_var["t_list"],
            "f_list": code_array.merge_e_lists(temp_var["f_list"], second_arg["f_list"]),
            "starting_quad_index": first_arg["starting_quad_index"],
            "type": "bool"}
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
    temp_var = symbol_table.get_new_temp_variable("bool")
    code_array.emit('=', temp_var, {"value": 1, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["t_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, second_arg["starting_quad_index"], None)
    code_array.emit('=', temp_var, {"value": 0, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["f_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, second_arg["starting_quad_index"], None)
    code_array.create_simple_if_check(temp_var)
    code_array.backpatch_e_list(second_arg["f_list"], code_array.get_current_quad_index() - 2)
    p[0] = {"t_list": code_array.merge_e_lists(temp_var["t_list"], second_arg["t_list"]),
            "f_list": temp_var["f_list"],
            "starting_quad_index": first_arg["starting_quad_index"],
            "type": "bool"}
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
            "starting_quad_index": first_arg["starting_quad_index"],
            "type": "bool"}
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
            "starting_quad_index": first_arg["starting_quad_index"],
            "type": "bool"}
    return


def p_bool_expressions_not(p):
    """bool_expressions     : NOT expressions"""
    arg = p[2]
    if "t_list" not in arg:
        code_array.create_simple_if_check(arg)
    p[0] = {"t_list": arg["f_list"],
            "f_list": arg["t_list"],
            "starting_quad_index": arg["starting_quad_index"],
            "type": "bool"}
    return


def p_arithmetic_expressions1(p):
    """arithmetic_expressions       : PLUS pair 
                                    | MINUS pair 
                                    | MULT pair 
                                    | DIV pair 
                                    | MOD pair
                                    | MINUS expressions"""
    if p.slice[2].type == "expressions":
        exp_type = p[1]["type"]
        if exp_type == "bool" and "place" not in p[2]:
            p[1] = code_array.store_boolean_expression_in_variable(p[1])
        first_arg = p[1]
        second_arg = None
    else:
        if p[2]["first_arg"]["type"] == "bool" and "place" not in p[2]["first_arg"]:
            p[2]["first_arg"] = code_array.store_boolean_expression_in_variable(p[2]["first_arg"])
        if p[2]["second_arg"]["type"] == "bool" and "place" not in p[2]["second_arg"]:
            p[2]["second_arg"] = code_array.store_boolean_expression_in_variable(p[2]["second_arg"])
        first_arg = p[2]["first_arg"]
        second_arg = p[2]["second_arg"]
        pattern = r'(\*|\+|\-|\/)'
        if re.match(pattern, p[1]):
            exp_type = get_pair_type_for_arithmetic_expression(p[2])
        else:
            if p[2]["type"] != "real":
                exp_type = "int"
            else:
                exp_type = "real"
    p[0] = symbol_table.get_new_temp_variable(exp_type)
    new_code_entry = code_array.get_new_entry(p[1], p[0], first_arg, second_arg, None)
    code_array.append(new_code_entry)
    return


def p_pair(p):
    """pair     : LPAR expressions COMMA expressions RPAR"""
    p[0] = {"first_arg": p[2], "second_arg": p[4]}
    return


def get_pair_type_for_arithmetic_expression(pair):
    first_arg_type = pair["first_arg"]["type"]
    second_arg_type = pair["second_arg"]["type"]
    if first_arg_type == "int":
        if second_arg_type == "int":
            pair_type = "int"
        elif second_arg_type == "char":
            pair_type = "int"
        elif second_arg_type == "real":
            pair_type = "real"
        elif second_arg_type == "bool":
            pair_type = "int"
    if first_arg_type == "char":
        if second_arg_type == "int":
            pair_type = "int"
        elif second_arg_type == "char":
            pair_type = "char"
        elif second_arg_type == "real":
            pair_type = "real"
        elif second_arg_type == "bool":
            pair_type = "int"
    if first_arg_type == "real":
        pair_type = "real"
    if first_arg_type == "bool":
        if second_arg_type == "int":
            pair_type = "int"
        elif second_arg_type == "char":
            pair_type = "int"
        elif second_arg_type == "real":
            pair_type = "real"
        elif second_arg_type == "bool":
            pair_type = "int"
    return pair_type


def p_error(p):
    print("Syntax error in input!")
    print(str(p) + str(p.lineno))
    parser.restart()


def print_error(msg, p):
    print(msg + "\tline: " + str(p.lineno))
    # raise SyntaxError
    return


def run_compiler(input_file_path, output_file_path):
    code = None
    with open(input_file_path, 'r') as input_file:
        code = input_file.read()
    parser.parse(code, lexer=lexer, debug=False, tracking=True)
    code_generator = CodeGenerator()
    generated_code = code_generator.generate_code()
    with open(output_file_path, 'w') as output_file:
        output_file.write(generated_code)
    return


def run_lexer(input_file_path):
    # read input file
    code = None
    with open(input_file_path, 'r') as input_file:
        code = input_file.read()
    # Give the lexer some input
    lexer.input(code)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)
    return


def main():
    # run_lexer("./input_boolean.dm")
    run_compiler("./input_boolean.dm", "./output_code.c")
    return


# Build the parser
parser = yacc.yacc(tabmodule="parsing_table")
main()
