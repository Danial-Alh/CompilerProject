class SymbolTable(list):
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
