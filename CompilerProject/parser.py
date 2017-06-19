import re, copy
import ply.yacc as yacc
from lexer import tokens, lexer
from assets import symbol_table, code_array, CodeGenerator, CompilationException

start = 'program'

precedence = (
    ('right', 'THEN', 'ELSE'),
)


def p_program(p):
    """program      : PROGRAM psc ID declarations_list qis_1 procedure_list MAIN block
                    | PROGRAM psc ID qis_1 procedure_list MAIN block
                    | PROGRAM psc ID declarations_list MAIN block
                    | PROGRAM psc ID MAIN block"""
    if p[len(p) - 1] and "exit_when_quad_index" in p[len(p) - 1]:
        raise CompilationException("exit when just allowed in loops!!! function: main", p.slice[1])
    symbol_table.set_root()
    if len(p) > 7:
        if len(p) == 9:
            main_goto_quad_index = p[5]
            main_quad_index = p[8]
        else:
            main_goto_quad_index = p[4]
            main_quad_index = p[7]
        code_array.backpatch_e_list(main_goto_quad_index["goto_quad_index"], main_quad_index["starting_quad_index"])
    return


def p_declarations_list(p):
    """declarations_list    : declarations 
                            | declarations_list declarations"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
    return


def p_declarations(p):
    """declarations     : type_specifiers declarator_list SEMICOLON"""
    declarations = []
    for declarator in p[2]["declarations_info"]:
        declarator["type"] = p[1]["type"]
        place = declarator["place"]
        if not symbol_table.current_scope_has_variable(place):
            if place in symbol_table:
                should_be_declared = False
            else:
                should_be_declared = True
            index = symbol_table.install_variable(declarator)
            code_array.initialize_variable(declarator)
            symbol_table[index]["should_be_declared"] = should_be_declared
        else:
            raise CompilationException("multiple variable \'" + place + "\' declaration!!", p.slice[1])
        declarations.append(declarator)
    p[0] = declarations
    return


def p_type_specifiers(p):
    """type_specifiers      : INT
                            | REAL
                            | CHAR
                            | BOOLEAN"""
    if p[1] == "boolean":
        p[1] = "bool"
    elif p[1] == "real":
        p[1] = "float"
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
            from_variable = {"value": 0, "type": "int"}
            to_variable = symbol_table.get_new_temp_variable("int")
            code_array.emit("-", to_variable, p[3], {"value": 1, "type": "int"})
            p[0]["range"] = {"from": from_variable, "to": to_variable}
        array_size_variable = symbol_table.get_new_temp_variable("int")
        code_array.emit("-", array_size_variable, p[0]["range"]["to"], p[0]["range"]["from"])
        code_array.emit("+", array_size_variable, array_size_variable, {"value": 1, "type": "int"})
        p[0]["array_size"] = array_size_variable
    return


def p_range(p):
    """range        : ID DOUBLE_DOT ID
                    | NUMCONST DOUBLE_DOT NUMCONST
                    | arithmetic_expressions DOUBLE_DOT arithmetic_expressions"""
    if p.slice[1].type == "ID":
        symbol_table.check_variable_declaration(p[1], p.slice[1])
        code_array.check_variable_is_not_array(p[1], p.slice[1])
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
    """procedure_list       : procedure_list procedure
                            | procedure"""


def p_procedure(p):
    """procedure        : PROCEDURE function_sign LBRACE qis_1 declarations_list block RBRACE SEMICOLON
                        | PROCEDURE function_sign LBRACE qis_1 block RBRACE SEMICOLON"""
    if p[len(p) - 3] and "exit_when_quad_index" in p[len(p) - 3]:
        raise CompilationException("exit when just allowed in loops!!! function: " + p[2]["place"], p.slice[2])
    procedure = p[2]
    p[0] = procedure

    # goto return statements
    exit_procedure_statements_quad_index = code_array.get_next_quad_index()
    return_address_variable = symbol_table.get_new_temp_variable("void*")
    code_array.emit("pop", return_address_variable, None, None)
    code_array.emit("short jump", None, return_address_variable, None)
    begin_procedure_statements_quad_index = code_array.get_next_quad_index()

    # backpatch qis_1 with begin proc statements
    qis_1 = p[4]
    code_array.backpatch_e_list(qis_1["goto_quad_index"], begin_procedure_statements_quad_index)
    # load arguments
    for parameter in procedure["parameters"]:
        code_array.emit("pop", parameter, None, None)
    # goto beginning of proc
    code_array.emit("goto", None, qis_1["quad_index"], None)
    symbol_table.pop_scope()
    return


def p_fucntion_sign(p):
    """function_sign      : psc ID parameters"""
    sign = {"place": p[2]["place"], "quad_index": p[1]["quad_index"], "parameters": p[3]}
    p[0] = sign
    place = sign["place"]
    if place not in symbol_table:
        symbol_table.install_procedure(sign)
    else:
        raise CompilationException("multiple procedure \'" + place + "\' declaration!!", p.slice[2])
    p[0] = sign
    return


def p_parameters(p):
    """parameters       : LPAR declarations_list RPAR
                        | LPAR RPAR"""
    if len(p) == 3:
        p[0] = []
    else:
        p[0] = p[2]
    return


def p_block(p):
    """block        : LBRACE qis statement_list RBRACE"""
    p[0] = p[3]
    return


def p_statement_list(p):
    """statement_list       : statement SEMICOLON
                            | statement_list statement SEMICOLON"""
    if len(p) == 3:
        new_statement = p[1]
        old_statements = None
    else:
        new_statement = p[2]
        old_statements = p[1]
    if new_statement and "exit_when_quad_index" in new_statement:
        if old_statements and "exit_when_quad_index" in old_statements:
            p[0] = {"exit_when_quad_index": code_array.merge_e_lists(new_statement["exit_when_quad_index"],
                                                                     old_statements["exit_when_quad_index"])}
        else:
            p[0] = new_statement
    else:
        p[0] = old_statements
    return


def p_statement_print(p):
    """statement            : PRINT ID
                            | PRINT ID LBRACK expressions RBRACK"""
    symbol_table.check_variable_declaration(p[2], p.slice[2])
    if len(p) == 6:
        var_copy = code_array.setup_array_variable(p[2], p[4], p.slice[2])
        code_array.emit("print", None, var_copy, None)
    else:
        code_array.check_variable_is_not_array(p[2], p.slice[2])
        code_array.emit("print", None, p[2], None)
    return


def p_statement_assignment(p):
    """statement            : ID ASSIGNMENT_SIGN expressions
                            | ID LBRACK expressions RBRACK ASSIGNMENT_SIGN expressions"""
    symbol_table.check_variable_declaration(p[1], p.slice[1])
    p[3] = code_array.store_boolean_expression_in_variable(p[3])
    if len(p) == 4:
        code_array.check_variable_is_not_array(p[1], p.slice[1])
        code_array.emit("=", p[1], p[3], None)
    else:
        p[6] = code_array.store_boolean_expression_in_variable(p[6])
        var_copy = code_array.setup_array_variable(p[1], p[3], p.slice[1])
        code_array.emit("=", var_copy, p[6], None)
    return


###### function call stack ######
# arguments                # TOP
# return address
# return value
# current context
def p_statement_function_call(p):
    """statement            : ID LPAR arguments_list RPAR"""
    procedure = p[1]
    symbol_table.check_procedure_declaration(procedure, p.slice[1])
    if len(p[3]) != len(procedure["parameters"]):
        raise CompilationException(
            "function call didn't match with function \'" + procedure["place"] + "\' declaration!",
            p.slice[1])
    code_array.save_context()
    code_array.emit("store_top", symbol_table.get_current_scope_symbol_table().top_stack_variable, None, None)
    code_array.emit("push", None, {"value": 0, "type": "int"}, None)
    return_address_variable = symbol_table.get_new_temp_variable("void*")
    code_array.emit("&&", return_address_variable, None, None)
    temp_index = code_array.get_current_quad_index()
    code_array.emit("push", None, return_address_variable, None)
    for argument in p[3]:
        code_array.emit("push", None, argument, None)
    code_array.emit("call", None, procedure["quad_index"], None)
    code_array.emit("pop", symbol_table.get_new_temp_variable("int"), None, None)
    code_array.backpatch_e_list([temp_index], code_array.get_current_quad_index())
    code_array.restore_context()
    return


def p_statement_function_return(p):
    """statement            : RETURN expressions"""
    if p[2]["type"] != "int":
        raise CompilationException("return value can only be in int type!! seen type: " + p[2]["type"], p.slice[2])
    # goto return statements
    return_address_variable = symbol_table.get_new_temp_variable("void*")
    code_array.emit("pop", return_address_variable, None, None)
    code_array.emit("pop", symbol_table.get_new_temp_variable("int"), None, None)
    code_array.emit("push", None, p[2], None)
    code_array.emit("short jump", None, return_address_variable, None)
    return


def p_statement_if(p):
    """statement            : IF bool_expressions THEN qis statement
                            | IF bool_expressions THEN qis statement ELSE qis_1 statement"""
    code_array.backpatch_e_list(p[2]["t_list"], p[4]["quad_index"])
    if len(p) == 6:
        code_array.backpatch_e_list(p[2]["f_list"], code_array.get_next_quad_index())
    else:
        code_array.backpatch_e_list(p[2]["f_list"], p[7]["quad_index"])
        code_array.backpatch_e_list(p[7]["goto_quad_index"], code_array.get_next_quad_index())
    return


def p_statement_do_while(p):
    """statement            : DO qis statement WHILE bool_expressions"""
    code_array.backpatch_e_list(p[5]["t_list"], p[2]["quad_index"])
    code_array.backpatch_e_list(p[5]["f_list"], code_array.get_next_quad_index())
    if p[3] and "exit_when_quad_index" in p[3]:
        code_array.backpatch_e_list(p[3]["exit_when_quad_index"], code_array.get_next_quad_index())
    return


def p_statement_for(p):
    """statement            : FOR ID ASSIGNMENT_SIGN counter DO qis_1 statement"""
    symbol_table.check_variable_declaration(p[2], p.slice[2])
    code_array.check_variable_is_not_array(p[2], p.slice[2])
    code_array.emit(p[4]["opt"], p[2], p[2], {"value": 1, "type": "int"})
    code_array.emit("goto", None, code_array.get_next_quad_index() + 2, None)
    code_array.backpatch_e_list(p[6]["goto_quad_index"], code_array.get_next_quad_index())
    code_array.emit("=", p[2], p[4]["from"], None)
    code_array.emit(">", None, p[2], p[4]["to"])
    code_array.emit("goto", None, code_array.get_next_quad_index() + 2, None)
    code_array.emit("goto", None, p[6]["quad_index"], None)
    if p[7] and "exit_when_quad_index" in p[7]:
        code_array.backpatch_e_list(p[7]["exit_when_quad_index"], code_array.get_next_quad_index())
    return


def p_statement_switch(p):
    """statement            : SWITCH expressions qis_1 case_element default END
                            | SWITCH expressions qis_1 case_element END"""
    if p[2]["type"] == "bool" and "place" not in p[2] and "value" not in p[2]:
        p[2] = code_array.store_boolean_expression_in_variable(p[2])
        code_array.emit("goto", None, code_array.get_next_quad_index() + 1, None)
        code_array.backpatch_e_list(p[3]["goto_quad_index"], code_array.get_next_quad_index())
    else:
        code_array.backpatch_e_list(p[3]["goto_quad_index"], code_array.get_next_quad_index())
    next_list = []
    for case_element in p[4]:
        code_array.emit("==", None, p[2], case_element["num_constraint"])
        code_array.emit("goto", None, case_element["starting_quad_index"], None)
        next_list.append(case_element["break_quad_index"])
    if len(p) == 7:
        code_array.emit("goto", None, p[5]["starting_quad_index"], None)
        next_list.append(p[5]["break_quad_index"])
    code_array.backpatch_e_list(next_list, code_array.get_next_quad_index())
    return


def p_statement_exit_when(p):
    """statement            : EXIT WHEN bool_expressions"""
    code_array.backpatch_e_list(p[3]["f_list"], code_array.get_next_quad_index())
    p[0] = {"exit_when_quad_index": p[3]["t_list"]}
    return


def p_statement_block(p):
    """statement            : block
                            | """
    if len(p) == 2:
        p[0] = p[1]
    return


def p_arguments_list(p):
    """arguments_list       : multi_arguments
                            | """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]
    return


def p_multi_arguments(p):
    """multi_arguments      : multi_arguments COMMA expressions 
                            | expressions"""
    if len(p) == 2:
        p[1] = code_array.store_boolean_expression_in_variable(p[1])
        p[0] = [p[1]]
    else:
        p[3] = code_array.store_boolean_expression_in_variable(p[3])
        p[0] = p[1] + [p[3]]
    return


def p_counter(p):
    """counter      : NUMCONST UPTO NUMCONST 
                    | NUMCONST DOWNTO NUMCONST"""
    p[0] = {"from": p[1], "to": p[3]}
    if p[2] == "upto":
        p[0]["opt"] = "+"
    else:
        p[0]["opt"] = "-"
    return


def p_case_element(p):
    """case_element     : CASE NUMCONST COLON qis block
                        | case_element CASE NUMCONST COLON qis block"""
    break_quad_index = code_array.get_next_quad_index()
    code_array.emit("goto", None, None, None)
    if len(p) == 6:
        p[0] = [{"num_constraint": p[2], "starting_quad_index": p[4]["quad_index"],
                 "break_quad_index": break_quad_index}]
    else:
        p[0] = [{"num_constraint": p[3], "starting_quad_index": p[5]["quad_index"],
                 "break_quad_index": break_quad_index}] + p[1]
    return


def p_default(p):
    """default      : DEFAULT COLON qis block"""
    break_quad_index = code_array.get_next_quad_index()
    code_array.emit("goto", None, None, None)
    p[0] = {"starting_quad_index": p[3]["quad_index"], "break_quad_index": break_quad_index}
    return


def p_expressions(p):
    """expressions      : constant_expressions 
                        | bool_expressions 
                        | arithmetic_expressions
                        | ID 
                        | ID LBRACK expressions RBRACK 
                        | LPAR expressions RPAR"""
    if p.slice[1].type == "ID":
        symbol_table.check_variable_declaration(p[1], p.slice[1])
        if len(p) == 5 and p.slice[3].type == "expressions":
            p[0] = code_array.setup_array_variable(p[1], p[3], p.slice[1])
        else:
            code_array.check_variable_is_not_array(p[1], p.slice[1])
            p[0] = p[1]
    elif p.slice[1].type == "constant_expressions":
        p[0] = p[1]
    elif p.slice[1].type == "LPAR":
        p[0] = p[2]
    else:
        p[0] = p[1]
    return


def p_expressions_function_call(p):
    """expressions      : ID LPAR arguments_list RPAR"""
    procedure = p[1]
    symbol_table.check_procedure_declaration(procedure, p.slice[1])
    if len(p[3]) != len(procedure["parameters"]):
        raise CompilationException(
            "function call didn't match with function \'" + procedure["place"] + "\' declaration!",
            p.slice[1])
    code_array.save_context()
    code_array.emit("store_top", symbol_table.get_current_scope_symbol_table().top_stack_variable, None, None)
    code_array.emit("push", None, {"value": 0, "type": "int"}, None)
    return_address_variable = symbol_table.get_new_temp_variable("void*")
    code_array.emit("&&", return_address_variable, None, None)
    temp_index = code_array.get_current_quad_index()
    code_array.emit("push", None, return_address_variable, None)
    for argument in p[3]:
        code_array.emit("push", None, argument, None)
    code_array.emit("call", None, procedure["quad_index"], None)
    p[0] = symbol_table.get_new_temp_variable("int")
    code_array.emit("pop", p[0], None, None)
    code_array.backpatch_e_list([temp_index], code_array.get_current_quad_index())
    code_array.restore_context()
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
    if "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    if "t_list" not in second_arg:
        p[2]["second_quad_index"] = code_array.create_simple_if_check(second_arg)
    temp_var = symbol_table.get_new_temp_variable("bool")
    code_array.emit('=', temp_var, {"value": 1, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["t_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, p[2]["second_quad_index"], None)
    code_array.emit('=', temp_var, {"value": 0, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["f_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, p[2]["second_quad_index"], None)
    code_array.create_simple_if_check(temp_var)
    code_array.backpatch_e_list(second_arg["t_list"], code_array.get_current_quad_index() - 2)
    p[0] = {"t_list": temp_var["t_list"],
            "f_list": code_array.merge_e_lists(temp_var["f_list"], second_arg["f_list"]),
            "type": "bool"}
    return


def p_bool_expressions_or(p):
    """bool_expressions     : OR pair"""
    first_arg = p[2]["first_arg"]
    second_arg = p[2]["second_arg"]
    if "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    if "t_list" not in second_arg:
        p[2]["second_quad_index"] = code_array.create_simple_if_check(second_arg)
    temp_var = symbol_table.get_new_temp_variable("bool")
    code_array.emit('=', temp_var, {"value": 1, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["t_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, p[2]["second_quad_index"], None)
    code_array.emit('=', temp_var, {"value": 0, "type": "bool"}, None)
    code_array.backpatch_e_list(first_arg["f_list"], code_array.get_current_quad_index())
    code_array.emit('goto', None, p[2]["second_quad_index"], None)
    code_array.create_simple_if_check(temp_var)
    code_array.backpatch_e_list(second_arg["f_list"], code_array.get_current_quad_index() - 2)
    p[0] = {"t_list": code_array.merge_e_lists(temp_var["t_list"], second_arg["t_list"]),
            "f_list": temp_var["f_list"],
            "type": "bool"}
    return


def p_bool_expressions_and_then(p):
    """bool_expressions     : AND THEN pair"""
    first_arg = p[3]["first_arg"]
    second_arg = p[3]["second_arg"]
    if "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    if "t_list" not in second_arg:
        p[3]["second_quad_index"] = code_array.create_simple_if_check(second_arg)
    code_array.backpatch_e_list(first_arg["t_list"], p[3]["second_quad_index"])
    p[0] = {"t_list": second_arg["t_list"],
            "f_list": code_array.merge_e_lists(first_arg["f_list"], second_arg["f_list"]),
            "type": "bool"}
    return


def p_bool_expressions_or_else(p):
    """bool_expressions     : OR ELSE pair"""
    first_arg = p[3]["first_arg"]
    second_arg = p[3]["second_arg"]
    if "t_list" not in first_arg:
        code_array.create_simple_if_check(first_arg)
    if "t_list" not in second_arg:
        p[3]["second_quad_index"] = code_array.create_simple_if_check(second_arg)
    code_array.backpatch_e_list(first_arg["f_list"], p[3]["second_quad_index"])
    p[0] = {"f_list": second_arg["f_list"],
            "t_list": code_array.merge_e_lists(first_arg["t_list"], second_arg["t_list"]),
            "type": "bool"}
    return


def p_bool_expressions_not(p):
    """bool_expressions     : NOT expressions"""
    arg = p[2]
    if "t_list" not in arg:
        code_array.create_simple_if_check(arg)
    p[0] = {"t_list": arg["f_list"],
            "f_list": arg["t_list"],
            "type": "bool"}
    return


def p_arithmetic_expressions(p):
    """arithmetic_expressions       : PLUS pair 
                                    | MINUS pair 
                                    | MULT pair 
                                    | DIV pair 
                                    | MOD pair
                                    | MINUS expressions"""
    if p.slice[2].type == "expressions":
        exp_type = get_type_of_arithmetic_expression(p[1], "int", p[2]["type"], p.slice[1])
        p[2] = code_array.store_boolean_expression_in_variable(p[2])
        first_arg = {"value": 0, "type": "int"}
        second_arg = p[2]
    else:
        p[2]["first_arg"] = code_array.store_boolean_expression_in_variable(p[2]["first_arg"])
        p[2]["second_arg"] = code_array.store_boolean_expression_in_variable(p[2]["second_arg"])
        first_arg = p[2]["first_arg"]
        second_arg = p[2]["second_arg"]
        # pattern = r'(\*|\+|\-|\/)'
        # if re.match(pattern, p[1]):
        exp_type = get_type_of_pair_for_arithmetic_expression(p[1], p[2], p.slice[1])
    p[0] = symbol_table.get_new_temp_variable(exp_type)
    code_array.emit(p[1], p[0], first_arg, second_arg)
    if (p[1] == "%" or p[1] == "/") and "value" in second_arg and second_arg["value"] == 0:
        raise CompilationException("division by zero!!", p.slice[2])
    return


def p_pair(p):
    """pair     : LPAR expressions qis COMMA expressions RPAR"""
    p[0] = {"first_arg": p[2], "second_arg": p[5],
            # "first_quad_index": p[2]["quad_index"],
            "second_quad_index": p[3]["quad_index"]}
    return


def p_qis(p):  # qis: quad index saver
    """qis      : """
    p[0] = {"quad_index": code_array.get_next_quad_index()}
    return


def p_qis_1(p):
    """qis_1      : """
    code_array.emit("goto", None, None, None)
    p[0] = {"quad_index": code_array.get_next_quad_index(),
            "goto_quad_index": [code_array.get_current_quad_index()]}
    return


def p_psc(p):  # psc: procedure symbol table creator
    """psc      : """
    symbol_table.create_new_scope_symbol_table("main")
    p[0] = {"quad_index": code_array.get_next_quad_index()}
    return


def get_type_of_arithmetic_expression(operator, first_arg_type, second_arg_type, parameter):
    if operator == "%":
        if second_arg_type in ("float", "char"):
            raise CompilationException("operator: %, invalid second parameter type!!!\t seen type: " + second_arg_type,
                                       parameter)
        if first_arg_type == "int":
            pair_type = "int"
        if first_arg_type == "char":
            if second_arg_type == "int":
                pair_type = "int"
            elif second_arg_type == "bool":
                pair_type = "int"
        if first_arg_type == "float":
            pair_type = "float"
        if first_arg_type == "bool":
            pair_type = "int"
    elif operator == "/":
        if second_arg_type == "char":
            raise CompilationException("operator: /, invalid second parameter type!!!\t seen type: " + second_arg_type,
                                       parameter)
        if first_arg_type == "int":
            if second_arg_type == "int":
                pair_type = "int"
            elif second_arg_type == "char":
                pair_type = "int"
            elif second_arg_type == "float":
                pair_type = "float"
            elif second_arg_type == "bool":
                pair_type = "int"
        if first_arg_type == "char":
            if second_arg_type == "int":
                pair_type = "int"
            elif second_arg_type == "char":
                pair_type = "int"
            elif second_arg_type == "float":
                pair_type = "float"
            elif second_arg_type == "bool":
                pair_type = "int"
        if first_arg_type == "float":
            pair_type = "float"
        if first_arg_type == "bool":
            if second_arg_type == "int":
                pair_type = "int"
            elif second_arg_type == "char":
                pair_type = "int"
            elif second_arg_type == "float":
                pair_type = "float"
            elif second_arg_type == "bool":
                pair_type = "int"
    elif operator in ("+", "-", "*"):
        if first_arg_type == "int":
            if second_arg_type == "int":
                pair_type = "int"
            elif second_arg_type == "char":
                pair_type = "char"
            elif second_arg_type == "float":
                pair_type = "float"
            elif second_arg_type == "bool":
                pair_type = "int"
        if first_arg_type == "char":
            if second_arg_type == "int":
                pair_type = "char"
            elif second_arg_type == "char":
                pair_type = "char"
            elif second_arg_type == "float":
                pair_type = "float"
            elif second_arg_type == "bool":
                pair_type = "char"
        if first_arg_type == "float":
            pair_type = "float"
        if first_arg_type == "bool":
            if second_arg_type == "int":
                pair_type = "int"
            elif second_arg_type == "char":
                pair_type = "char"
            elif second_arg_type == "float":
                pair_type = "float"
            elif second_arg_type == "bool":
                pair_type = "int"
    return pair_type


def get_type_of_pair_for_arithmetic_expression(operator, pair, parameter):
    first_arg_type = pair["first_arg"]["type"]
    second_arg_type = pair["second_arg"]["type"]
    return get_type_of_arithmetic_expression(operator, first_arg_type, second_arg_type, parameter)


def p_error(p):
    msg = "Syntax error in input!\n" + str(p)
    raise CompilationException(msg, p)
    # parser.restart()


def run_compiler(input_file_path, output_file_path):
    code = None
    with open(input_file_path, 'r') as input_file:
        code = input_file.read()
    parser.parse(code, lexer=lexer, debug=False, tracking=True)
    code_array.emit("return 0", None, None, None)
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
    input_file_name = "statements"
    run_compiler("./input/" + input_file_name + ".txt", "./input/" + input_file_name + "_output_code.c")
    from subprocess import check_output
    str_out = check_output("gcc ./input/" + input_file_name + "_output_code.c -o a.out", shell=True).decode()
    if str_out != "":
        return
    else:
        print(str_out)
    str_out = check_output("a.out", shell=True).decode()
    print(str_out)
    return


# Build the parser
parser = yacc.yacc(tabmodule="parsing_table")
try:
    main()
except CompilationException as e:
    print(e.msg)
