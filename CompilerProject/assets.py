class SymbolTable(list):
    temp_variable_counter = 0

    def get_new_temp_variable(self):
        place = "T" + str(self.temp_variable_counter)
        self.temp_variable_counter += 1
        return place

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


class CodeArray(list):
    def get_new_entry(self):
        return {"opt": None, "first_arg": None, "second_arg": None}


def install_id(identifier):
    symbol_table.append(identifier)
    return len(symbol_table) - 1


symbol_table = SymbolTable()
code_array = CodeArray()
