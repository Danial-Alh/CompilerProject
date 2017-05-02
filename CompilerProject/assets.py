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

    def get_new_temp_variable(self):
        place = "T" + str(self.temp_variable_counter)
        self.temp_variable_counter += 1
        index = self.install_id(self.get_new_variable_dictionary(place))
        self[index]["variable_info"]["declared"] = True
        self[index]["variable_info"]["index"] = index
        return self[index]

    def get_new_variable_dictionary(self, place):
        return {"variable_info": {"declared": False, "index": None,
                                  "is_array": None, "type": None, "place": place}}

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

    def generate_code(self):
        should_indent = False
        for i in range(0, len(self)):
            entry = self[i]
            entry_code = ""
            opt = entry["opt"]
            ########################################################################################################
            if opt == '+' or opt == '-' or opt == '*' or opt == '/' or opt == '%':
                if "variable_info" in entry["first_arg"]:
                    arg1 = entry["first_arg"]["variable_info"]["place"]
                else:
                    arg1 = entry["first_arg"]["value"]
                if "second_arg" in entry:
                    arg2 = None
                elif "variable_info" in entry["second_arg"]:
                    arg2 = entry["second_arg"]["variable_info"]["place"]
                else:
                    arg2 = entry["second_arg"]["value"]
                entry_code += entry["result"]["variable_info"]["place"] + " = " + str(arg1) + " " + opt + " " + str(
                    arg2) + ";"
            ########################################################################################################
            elif opt == '=':
                if "variable_info" in entry["first_arg"]:
                    arg1 = entry["first_arg"]["variable_info"]["place"]
                else:
                    arg1 = entry["first_arg"]["value"]
                entry_code += entry["result"]["variable_info"]["place"] + " = " + str(arg1) + ";"
            ########################################################################################################
            elif opt == '<' or opt == '<=' or opt == '>' or opt == '>=' or opt == '==' or opt == '!=':
                if "variable_info" in entry["first_arg"]:
                    arg1 = entry["first_arg"]["variable_info"]["place"]
                else:
                    arg1 = entry["first_arg"]["value"]
                if "variable_info" in entry["second_arg"]:
                    arg2 = entry["second_arg"]["variable_info"]["place"]
                else:
                    arg2 = entry["second_arg"]["value"]
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
                if "variable_info" in entry["first_arg"]:
                    arg1 = entry["first_arg"]["variable_info"]["place"]
                else:
                    arg1 = entry["first_arg"]["value"]
                entry_code += "if (" + str(arg1) + ")"
                should_indent = True
            ########################################################################################################
            else:
                entry_code += str(entry)
            print(str(i) + ":\t" + entry_code)


symbol_table = SymbolTable()
code_array = CodeArray()
