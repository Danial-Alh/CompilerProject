import copy
import re


class SymbolTable:
    temp_variable_counter = 0
    last_id_seen = ""

    class ScopeSymbolTable:
        def __init__(self, function_name, parent):
            if parent is None:
                self.depth = 0
            else:
                self.depth = parent.depth + 1
            self.function_name = function_name
            self.parent = parent
            self.size = 0
            self.symbols = []
            # self.top_stack_variable = symbol_table.get_new_temp_variable("type")
            self.top_stack_variable = None
            return

    def __init__(self):
        self.root = None
        self.table_stack = []
        return

    def __contains__(self, item):
        current_table = self.table_stack[-1]
        while current_table is not None:
            for symbol in current_table.symbols:
                if symbol["place"] == item:
                    return True
            current_table = current_table.parent
        return False

    def __getitem__(self, item):
        return item["sym_table"].symbols[item["local_index"]]

    def current_scope_has_variable(self, item):
        current_table = self.table_stack[-1]
        for symbol in current_table.symbols:
            if symbol["place"] == item:
                return True
        return False

    def index(self, object, start: int = 0, stop: int = ...):
        current_table = self.table_stack[-1]
        while current_table is not None:
            for i in range(0, len(current_table.symbols)):
                if current_table.symbols[i]["place"] == object:
                    return current_table.symbols[i]["index"]
            current_table = current_table.parent
        return None

    def get_new_temp_variable(self, type):
        place = "T" + str(self.temp_variable_counter)
        self.temp_variable_counter += 1
        symbol_table_entry = self.get_new_variable_dictionary(place)
        symbol_table_entry["type"] = type
        index = self.install_variable(symbol_table_entry)
        return symbol_table_entry

    def get_new_variable_dictionary(self, place):
        return {"declared": False, "index": None,
                "is_array": False, "type": None, "place": place, "initializer": None, "should_be_declared": True}

    def get_variable_size(self, variable):
        type_size = {"int": 4, "float": 4, "char": 1, "bool": 1, "void*": 8}
        if variable["is_array"]:
            return 8
        else:
            return type_size[variable["type"]]

    def check_variable_declaration(self, variable, param):
        if not variable["declared"]:
            msg = "variable \'" + variable["place"] + "\' not declared!!"
            raise CompilationException(msg, param)

    def check_procedure_declaration(self, procedure, param):
        if not procedure["declared"]:
            msg = "procedure \'" + procedure["place"] + "\' not declared!!"
            raise CompilationException(msg, param)

    def create_new_scope_symbol_table(self, function_name):
        if len(self.table_stack) == 0:
            parent_table = None
        else:
            parent_table = self.table_stack[-1]
        new_scope_symbol_table = self.ScopeSymbolTable(function_name, parent_table)
        self.table_stack.append(new_scope_symbol_table)
        return new_scope_symbol_table

    def install_variable(self, variable):
        current_table = self.table_stack[-1]
        current_table.symbols.append(variable)
        current_table.size += self.get_variable_size(variable)
        variable["index"] = {"local_index": len(current_table.symbols) - 1, "sym_table": current_table}
        variable["declared"] = True
        return variable["index"]

    def install_procedure(self, procedure):
        procedure_table = self.table_stack[-1]
        procedure_table.function_name = procedure["place"]
        parent_table = self.table_stack[-2]
        parent_table.symbols.append(procedure)
        procedure["sym_table"] = procedure_table
        procedure["type"] = "procedure"
        procedure["index"] = {"local_index": len(parent_table.symbols) - 1, "sym_table": parent_table}
        procedure["declared"] = True
        procedure["should_be_declared"] = True
        return len(parent_table.symbols) - 1

    def pop_scope(self):
        self.table_stack.pop()
        return

    def set_root(self):
        self.root = self.table_stack.pop()
        return

    def get_current_scope_symbol_table(self):
        return self.table_stack[-1].symbols

    def get_root(self):
        return self.root


class CodeArray(list):
    def get_new_entry(self):
        return {"opt": None, "first_arg": None, "second_arg": None, "result": None, "label_used": None}

    def get_new_entry(self, opt, result, first_arg, second_arg, label_used):
        return {"opt": opt, "result": result, "first_arg": first_arg, "second_arg": second_arg,
                "label_used": label_used}

    def emit(self, opt, result, first_arg, second_arg):
        if opt == "push" and "value" in first_arg:
            temp_var = symbol_table.get_new_temp_variable(first_arg["type"])
            self.emit("=", temp_var, first_arg, None)
            first_arg = temp_var
        # if first_arg == 115:
        #     print("ok")
        self.append(self.get_new_entry(opt, result, first_arg, second_arg, False))
        return

    def get_next_quad_index(self):
        return len(self)

    def get_current_quad_index(self):
        return len(self) - 1

    def create_simple_if_check(self, arg):
        starting_quad_index = code_array.get_next_quad_index()
        arg["t_list"] = [code_array.get_next_quad_index() + 1]
        arg["f_list"] = [code_array.get_next_quad_index() + 2]
        code_array.emit("if", None, arg, None)
        code_array.emit("goto", None, None, None)
        code_array.emit("goto", None, None, None)
        return starting_quad_index

    def backpatch_e_list(self, e_list, target):
        for quad_entry_index in e_list:
            # if quad_entry_index == 115:
            #     print("ok")
            code_array[quad_entry_index]["first_arg"] = target
        return

    def merge_e_lists(self, e_list_1, e_list_2):
        return e_list_1 + e_list_2

    def get_variable_string(self, variable):
        if variable is None:
            return None
        result = ""
        if "value" in variable:
            result = str(variable["value"])
        else:
            result = str(variable["place"])
            if variable["is_array"]:
                if "array_index" in variable:
                    index_string = code_array.get_variable_string(variable["array_index"])
                    result += "[" + str(index_string) + "]"
        return result

    def get_variable_type(self, variable):
        variable_type = variable["type"]
        if "value" not in variable:
            if variable["is_array"]:
                variable_type += "*"
        return variable_type

    def initialize_variable(self, variable):
        if variable["is_array"]:
            code_array.emit("malloc", variable, None, None)
            if variable["initializer"] is not None:
                for i in range(0, len(variable["initializer"]["initial_value"])):
                    temp_variable = copy.deepcopy(variable)
                    temp_variable["array_index"] = {"value": i, "type": "int"}
                    code_array.emit("=", temp_variable, variable["initializer"]["initial_value"][i], None)
        elif variable["initializer"] is not None:
            code_array.emit("=", variable, variable["initializer"]["initial_value"][0], None)
        return

    def store_boolean_expression_in_variable(self, exp):
        if exp["type"] == "bool" and "place" not in exp and "value" not in exp:
            if "value" in exp:
                self.create_simple_if_check(exp)
            temp_var = symbol_table.get_new_temp_variable("bool")
            self.emit("=", temp_var, {"value": 1, "type": "bool"}, None)
            self.backpatch_e_list(exp["t_list"], self.get_current_quad_index())
            self.emit("goto", None, self.get_next_quad_index() + 2, None)
            self.emit("=", temp_var, {"value": 0, "type": "bool"}, None)
            self.backpatch_e_list(exp["f_list"], self.get_current_quad_index())
            exp = temp_var
        return exp

    def setup_array_variable(self, target_variable, index, variable_param):
        if not target_variable["is_array"]:
            raise CompilationException("non array variable \'" + target_variable["place"] + "\' with index!!",
                                       variable_param)
        var_copy = copy.deepcopy(target_variable)
        index = code_array.store_boolean_expression_in_variable(index)
        array_index_variable = symbol_table.get_new_temp_variable("int")
        code_array.emit("-", array_index_variable, index, var_copy["range"]["from"])
        var_copy["array_index"] = array_index_variable
        return var_copy

    def save_context(self):
        for i in range(0, len(symbol_table.get_current_scope_symbol_table())):
            entry = symbol_table.get_current_scope_symbol_table()[i]
            if entry["type"] == "procedure" or re.match(r'T([0-9]+)', entry["place"]):
                continue
            else:
                self.emit("push", None, entry, None)
        return

    def restore_context(self):
        for i in reversed(range(0, len(symbol_table.get_current_scope_symbol_table()))):
            entry = symbol_table.get_current_scope_symbol_table()[i]
            if entry["type"] == "procedure" or re.match(r'T([0-9]+)', entry["place"]):
                continue
            else:
                self.emit("pop", entry, None, None)
        return

    def check_variable_is_not_array(self, variable, param):
        if variable["is_array"]:
            raise CompilationException("array \'" + variable["place"] + "\' without index!!!", param)
        return


class CodeGenerator:
    def __init__(self):
        self.number_of_indentation = 0
        self.should_indent = False
        self.result_code = ""

    def generate_code(self):
        for entry in code_array:
            if entry["opt"] in ("goto", "&&", "call"):
                if entry["first_arg"] is None:
                    raise CompilationException("goto with no arg!!\n\t" + str(entry))
                code_array[entry["first_arg"]]["label_used"] = True
        self.result_code = ""
        self.__add_to_result_code("#include <stdlib.h>")
        self.__add_to_result_code("#include <stdbool.h>")
        self.__add_to_result_code("#include <stdio.h>")
        self.__add_to_result_code("#include <string.h>")
        self.__add_to_result_code("int main()")
        self.__add_to_result_code("{")
        self.number_of_indentation = 1
        self.__add_to_result_code("char _stack_[10000] = {0};")
        self.__add_to_result_code("int _top_ = 0;")
        self.__generate_variables(symbol_table.get_root(), [])
        self.__generate_statements()
        self.number_of_indentation = 0
        self.__add_to_result_code("}")
        return self.result_code

    def __generate_variables(self, curr_sym_table, variable_names):
        for entry in curr_sym_table.symbols:
            if not entry["should_be_declared"]:
                continue
            if entry["type"] == "procedure":
                self.__generate_variables(entry["sym_table"], variable_names)
                continue
            if entry["place"] in variable_names:
                continue
            declaration_code = entry["type"] + " "
            if entry["is_array"]:
                declaration_code += "*"
            declaration_code += entry["place"]
            variable_names.append(entry["place"])
            declaration_code += ";"
            self.__add_to_result_code(declaration_code)
        return

    def __generate_statements(self):
        for i in range(0, len(code_array)):
            entry = code_array[i]
            entry_code = ""
            if entry["label_used"]:
                entry_code += "label_" + str(i) + ": "
            opt = entry["opt"]
            ########################################################################################################
            if opt == "malloc":
                array_size = code_array.get_variable_string(entry["result"]["array_size"])
                entry_code += entry["result"]["place"] + " = (" + entry["result"]["type"] + "*) malloc(" + str(
                    array_size) + ");"
            ########################################################################################################
            elif opt == '+' or opt == '-' or opt == '*' or opt == '/' or opt == '%':
                arg1 = code_array.get_variable_string(entry["first_arg"])
                arg2 = code_array.get_variable_string(entry["second_arg"])
                entry_code += entry["result"]["place"] + " = (" + entry["first_arg"]["type"] + ") " + str(
                    arg1) + " " + opt + " " + str(
                    arg2) + ";"
            ########################################################################################################
            elif opt == '=':
                arg1 = code_array.get_variable_string(entry["first_arg"])
                entry_code += code_array.get_variable_string(entry["result"]) + " = (" + entry["first_arg"][
                    "type"] + ") " + str(arg1) + ";"
            ########################################################################################################
            elif opt == '<' or opt == '<=' or opt == '>' or opt == '>=' or opt == '==' or opt == '!=':
                arg1 = code_array.get_variable_string(entry["first_arg"])
                arg2 = code_array.get_variable_string(entry["second_arg"])
                entry_code += "if (" + str(arg1) + " " + opt + " " + str(arg2) + ")"
                self.should_indent = True
            ########################################################################################################
            elif opt == 'goto':
                if self.should_indent:
                    entry_code += "\t"
                    self.should_indent = False
                entry_code += "goto label_" + str(entry["first_arg"]) + ";"
            ########################################################################################################
            elif opt == 'if':
                arg1 = code_array.get_variable_string(entry["first_arg"])
                entry_code += "if (" + str(arg1) + ")"
                self.should_indent = True
            ########################################################################################################
            elif opt == 'print':
                arg1 = code_array.get_variable_string(entry["first_arg"])
                char_type = "%d"
                if entry["first_arg"]["type"] == "char":
                    char_type = "%c"
                elif entry["first_arg"]["type"] == "float":
                    char_type = "%f"
                entry_code += "printf(\"" + char_type + "\\n\", " + arg1 + ");"
            elif opt == '&&':
                arg1 = "label_" + str(entry["first_arg"])
                entry_code += code_array.get_variable_string(entry["result"]) + " = &&" + arg1 + ";"
            elif opt == 'push':
                variable_type = code_array.get_variable_type(entry["first_arg"])
                entry_code += "memcpy(_stack_+_top_, &" + code_array.get_variable_string(
                    entry["first_arg"]) + ", sizeof(" + variable_type + "));\t"
                entry_code += "_top_ += sizeof(" + variable_type + ");"
            elif opt == 'pop':
                variable_type = code_array.get_variable_type(entry["result"])
                entry_code += "memcpy(&" + code_array.get_variable_string(
                    entry["result"]) + ", _stack_+_top_-sizeof(" + variable_type + "), sizeof(" + \
                              variable_type + "));\t"
                entry_code += "_top_ -= sizeof(" + variable_type + ");"
            elif opt == 'call':
                entry_code += "goto label_" + str(entry["first_arg"]) + ";"
            elif opt == 'short jump':
                entry_code += "goto *" + code_array.get_variable_string(entry["first_arg"]) + ";"
            elif opt == 'return 0':
                entry_code += "return 0;"
            else:
                # raise CompilationException("operator \'" + opt + "\' not implemented!")
                print("operator \'" + opt + "\' not implemented!")
            self.__add_to_result_code(entry_code)
        return

    def __add_indentations(self):
        for i in range(0, self.number_of_indentation):
            self.result_code += "\t"
        return

    def __add_to_result_code(self, code):
        self.__add_indentations()
        self.result_code += code + "\n"


class CompilationException(Exception):
    def __init__(self, msg, params=None):
        if params is not None:
            msg += "\tline: " + str(params.lineno)
        self.msg = msg
        Exception.__init__(self, msg)
        return


symbol_table = SymbolTable()
code_array = CodeArray()
