class SymbolTable(list):
    temp_variable_counter = 0

    def __contains__(self, item):
        for symbol in self:
            if symbol["variable_info"]["place"] == item:
                return True
        return False

    def index(self, object, start: int = 0, stop: int = ...):
        for i in range(0, len(self)):
            if self[i]["variable_info"]["place"] == object:
                return i
        return -1

    def get_new_temp_variable(self, type):
        place = "T" + str(self.temp_variable_counter)
        self.temp_variable_counter += 1
        index = self.install_id(self.get_new_variable_dictionary(place))
        self[index]["variable_info"]["declared"] = True
        self[index]["variable_info"]["index"] = index
        self[index]["variable_info"]["type"] = type
        return self[index]

    def get_new_variable_dictionary(self, place):
        return {"variable_info": {"declared": False, "index": None,
                                  "is_array": False, "type": None, "place": place}, "initializer": None}

    def install_id(self, identifier):
        self.append(identifier)
        return len(self) - 1


class CodeArray(list):
    def get_new_entry(self):
        return {"opt": None, "first_arg": None, "second_arg": None, "result": None, "label": None}

    def get_new_entry(self, opt, result, first_arg, second_arg, label):
        return {"opt": opt, "result": result, "first_arg": first_arg, "second_arg": second_arg, "label": label}

    def get_next_quad_index(self):
        return len(self)

    def create_simple_if_check(self, arg):
        arg["t_list"] = [code_array.get_next_quad_index() + 1]
        arg["f_list"] = [code_array.get_next_quad_index() + 2]
        arg["starting_quad_index"] = code_array.get_next_quad_index()
        code_array.append(code_array.get_new_entry("if", None, arg, None, None))
        code_array.append(code_array.get_new_entry("goto", None, None, None, None))
        code_array.append(code_array.get_new_entry("goto", None, None, None, None))
        return

    def backpatch_e_list(self, e_list, target):
        for quad_entry_index in e_list:
            code_array[quad_entry_index]["first_arg"] = target
        return

    def merge_e_lists(self, e_list_1, e_list_2):
        return e_list_1 + e_list_2

    def get_variable_string(self, variable):
        if variable is None:
            return None
        result = ""
        if "variable_info" in variable:
            result = str(variable["variable_info"]["place"])
            if variable["variable_info"]["is_array"]:
                index_string = self.get_variable_string(variable["variable_info"]["array_index_variable"])
                result += "[" + str(index_string) + "]"
        else:
            result = str(variable["value"])
        return result

    def generate_code(self):
        self.generate_variables()
        self.generate_statements()
        return

    def generate_variables(self):
        for entry in symbol_table:
            declaration_code = entry["variable_info"]["type"] + " " + entry["variable_info"]["place"]
            if entry["variable_info"]["is_array"]:
                array_size_place = entry["variable_info"]["array_size"]["variable_info"]["place"]
                declaration_code += "[" + array_size_place + "]"
                if entry["initializer"] is not None:
                    declaration_code += "{"
                    for initial_value in entry["initializer"]["initial_value"]:
                        declaration_code += str(initial_value["value"]) + ", "
                    declaration_code = declaration_code[0:len(declaration_code) - 2]
                    declaration_code += "}"
            else:
                if entry["initializer"] is not None:
                    declaration_code += " = " + str(entry["initializer"]["initial_value"][0]["value"])
            declaration_code += ";"
            print(declaration_code)
        return

    def generate_statements(self):
        should_indent = False
        for i in range(0, len(self)):
            entry = self[i]
            entry_code = ""
            opt = entry["opt"]
            ########################################################################################################
            if opt == '+' or opt == '-' or opt == '*' or opt == '/' or opt == '%':
                arg1 = self.get_variable_string(entry["first_arg"])
                arg2 = self.get_variable_string(entry["second_arg"])
                entry_code += entry["result"]["variable_info"]["place"] + " = " + str(arg1) + " " + opt + " " + str(
                    arg2) + ";"
            ########################################################################################################
            elif opt == '=':
                arg1 = self.get_variable_string(entry["first_arg"])
                entry_code += entry["result"]["variable_info"]["place"] + " = " + str(arg1) + ";"
            ########################################################################################################
            elif opt == '<' or opt == '<=' or opt == '>' or opt == '>=' or opt == '==' or opt == '!=':
                arg1 = self.get_variable_string(entry["first_arg"])
                arg2 = self.get_variable_string(entry["second_arg"])
                entry_code += "if (" + str(arg1) + " " + opt + " " + str(arg2) + ")"
                should_indent = True
            ########################################################################################################
            elif opt == 'goto':
                if should_indent:
                    entry_code += "\t"
                entry_code += "goto " + str(entry["first_arg"]) + ";"
                should_indent = False
            ########################################################################################################
            elif opt == 'if':
                arg1 = self.get_variable_string(entry["first_arg"])
                entry_code += "if (" + str(arg1) + ")"
                should_indent = True
            ########################################################################################################
            else:
                entry_code += str(entry)
            print(str(i) + ":\t" + entry_code)
        return


symbol_table = SymbolTable()
code_array = CodeArray()
