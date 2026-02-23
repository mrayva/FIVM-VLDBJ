import sys
from typing import List

class Relation:
    def __init__(self, name: str, variables: dict[str, str], private_keys: set[str]):
        self.name: str = name
        self.variables: dict[str, str] = variables
        self.join_variables: set[str] = set()

    def var_type(self):
        s = ""
        for var in self.variables:
            s += f"\"{var}\": \"{self.variables[var]}\"\n"
        return s

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

path_relations = [
    Relation("R1", {"A1": "int", "A2": "int"}, {"A1", "A2"}),
    Relation("R2", {"A2": "int", "A3": "int"}, {"A2", "A3"}),
    Relation("R3", {"A3": "int", "A4": "int"}, {"A3", "A4"}),
    Relation("R4", {"A4": "int", "A5": "int"}, {"A4", "A5"}),
    Relation("R5", {"A5": "int", "A6": "int"}, {"A5", "A6"}),
    Relation("R6", {"A6": "int", "A7": "int"}, {"A6", "A7"}),
    Relation("R7", {"A7": "int", "A8": "int"}, {"A7", "A8"}),
    Relation("R8", {"A8": "int", "A9": "int"}, {"A8", "A9"}),
    Relation("R9", {"A9": "int", "A10": "int"}, {"A9", "A10"}),
    Relation("R10", {"A10": "int", "A11": "int"}, {"A10", "A11"}),
    Relation("R11", {"A11": "int", "A12": "int"}, {"A11", "A12"}),
    Relation("R12", {"A12": "int", "A13": "int"}, {"A12", "A13"}),
    Relation("R13", {"A13": "int", "A14": "int"}, {"A13", "A14"}),
    Relation("R14", {"A14": "int", "A15": "int"}, {"A14", "A15"}),
    Relation("R15", {"A15": "int", "A16": "int"}, {"A15", "A16"}),
    Relation("R16", {"A16": "int", "A17": "int"}, {"A16", "A17"}),
    Relation("R17", {"A17": "int", "A18": "int"}, {"A17", "A18"}),
    Relation("R18", {"A18": "int", "A19": "int"}, {"A18", "A19"}),
    Relation("R19", {"A19": "int", "A20": "int"}, {"A19", "A20"}),
    Relation("R20", {"A20": "int", "A21": "int"}, {"A20", "A21"})
]


path_sql_type_table = {
    "A0": "INT",
    "A1": "INT",
    "A2": "INT",
    "A3": "INT",
    "A4": "INT",
    "A5": "INT",
    "A6": "INT",
    "A7": "INT",
    "A8": "INT",
    "A9": "INT",
    "A10": "INT",
    "A11": "INT",
    "A12": "INT",
    "A13": "INT",
    "A14": "INT",
    "A15": "INT",
    "A16": "INT",
    "A17": "INT",
    "A18": "INT",
    "A19": "INT",
    "A20": "INT",
    "A21": "INT"
}