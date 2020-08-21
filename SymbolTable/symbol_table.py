from collections import defaultdict


class SymbolTable:
    def __init__(self):
        self.table = defaultdict(tuple)
        self.index_runner = defaultdict(int)

    def start_subroutine(self):
        self.table.clear()
        self.index_runner.clear()

    def define(self, name, type_, kind):
        self.index_runner[kind] += 1
        self.table[name] = (type_, kind, self.index_runner[kind])

    def var_count(self, kind):
        return self.index_runner[kind]

    def type_of(self, name):
        return self.table[name][0]

    def kind_of(self, name):
        return self.table[name][1]

    def index_of(self, name):
        return self.table[name][2]

    def contains(self, name):
        return bool(len(self.table[name]) > 0)
