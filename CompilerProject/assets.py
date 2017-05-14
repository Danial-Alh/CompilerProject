import copy


class SymbolTable(list):
    temp_variable_counter = 0

    def __contains__(self, item):
        for symbol in self:
            if symbol["place"] == item:
                return True
        return False

    def index(self, object, start: int = 0, stop: int = ...):
        for i in range(0, len(self)):
            if self[i]["place"] == object:
                return i
        return -1

    def get_new_temp_variable(self, type):
        place = "T" + str(self.temp_variable_counter)
        self.temp_variable_counter += 1
        index = self.install_id(self.get_new_variable_dictionary(place))
        self[index]["declared"] = True
        self[index]["index"] = index
        self[index]["type"] = type
        return self[index]

    def get_new_variable_dictionary(self, place):
        return {"declared": False, "index": None,
                "is_array": False, "type": None, "place": place, "initializer": None}

    def install_id(self, identifier):
        self.append(identifier)
        return len(self) - 1


class CodeArray(list):
    def get_new_entry(self):
        return {"opt": None, "first_arg": None, "second_arg": None, "result": None, "label_used": None}

    def get_new_entry(self, opt, result, first_arg, second_arg, label_used):
        return {"opt": opt, "result": result, "first_arg": first_arg, "second_arg": second_arg,
                "label_used": label_used}

    def emit(self, opt, result, first_arg, second_arg):
        if opt == "goto" and first_arg is not None:
            self[first_arg]["label_used"] = True
        self.append(self.get_new_entry(opt, result, first_arg, second_arg, False))
        return

    def get_next_quad_index(self):
        return len(self)

    def get_current_quad_index(self):
        return len(self) - 1

    def create_simple_if_check(self, arg):
        arg["t_list"] = [code_array.get_next_quad_index() + 1]
        arg["f_list"] = [code_array.get_next_quad_index() + 2]
        arg["starting_quad_index"] = code_array.get_next_quad_index()
        code_array.append(code_array.get_new_entry("if", None, arg, None, None))
        code_array.append(code_array.get_new_entry("goto", None, None, None, None))
        code_array.append(code_array.get_new_entry("goto", None, None, None, None))
        return

    def backpatch_e_list(self, e_list, target):
        code_array[target]["label_used"] = True
        for quad_entry_index in e_list:
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
                index_string = code_array.get_variable_string(variable["array_index"])
                result += "[" + str(index_string) + "]"
        return result

    def initialize_variable(self, variable):
        if variable["is_array"]:
            code_array.append(
                code_array.get_new_entry("malloc", variable, None, None, None))
            if variable["initializer"] is not None:
                for i in range(0, len(variable["initializer"]["initial_value"])):
                    temp_variable = copy.deepcopy(variable)
                    temp_variable["array_index"] = i
                    code_array.append(
                        code_array.get_new_entry("=", variable, variable["initializer"]["initial_value"][i], None,
                                                 None))
        elif variable["initializer"] is not None:
            code_array.emit("=", variable, variable["initializer"]["initial_value"][0], None)
        return

    def store_boolean_expression_in_variable(self, bool_exp):
        temp_var = symbol_table.get_new_temp_variable("bool")
        self.emit("=", temp_var, {"value": 1, "type": "bool"}, None)
        self.backpatch_e_list(bool_exp["t_list"], self.get_current_quad_index())
        self.emit("=", temp_var, {"value": 0, "type": "bool"}, None)
        self.backpatch_e_list(bool_exp["f_list"], self.get_current_quad_index())
        return temp_var


class CodeGenerator:
    def __init__(self):
        self.number_of_indentation = 0
        self.should_indent = False
        self.result_code = ""

    def generate_code(self):
        self.result_code = ""
        self.__add_to_result_code("#include <stdlib.h>")
        self.__add_to_result_code("#include <stdbool.h>")
        self.__add_to_result_code("int main()")
        self.__add_to_result_code("{")
        self.number_of_indentation = 1
        self.__generate_variables()
        self.__generate_statements()
        self.__add_to_result_code("return 0;")
        self.number_of_indentation = 0
        self.__add_to_result_code("}")
        return self.result_code

    def __generate_variables(self):
        result = ""
        for entry in symbol_table:
            declaration_code = entry["type"] + " "
            if entry["is_array"]:
                declaration_code += "*"
            declaration_code += entry["place"]
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
                entry_code += entry["result"]["place"] + " = " + str(arg1) + " " + opt + " " + str(
                    arg2) + ";"
            ########################################################################################################
            elif opt == '=':
                arg1 = code_array.get_variable_string(entry["first_arg"])
                entry_code += entry["result"]["place"] + " = " + str(arg1) + ";"
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
            else:
                entry_code += str(entry)
            self.__add_to_result_code(entry_code)
        return

    def __add_indentations(self):
        for i in range(0, self.number_of_indentation):
            self.result_code += "\t"
        return

    def __add_to_result_code(self, code):
        self.__add_indentations()
        self.result_code += code + "\n"


symbol_table = SymbolTable()
code_array = CodeArray()
