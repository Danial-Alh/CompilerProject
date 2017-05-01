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
        return {"opt": None, "first_arg": None, "second_arg": None, "label": None}

    def get_new_entry(self, opt, first_arg, second_arg, label):
        return {"opt": opt, "first_arg": first_arg, "second_arg": second_arg, "label": label}


symbol_table = SymbolTable()
code_array = CodeArray()
