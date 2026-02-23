
class Relation:
    def __init__(self, name: str, variables: dict[str, str], private_keys: set[str]):
        self.name: str = name.upper()
        self.variables: dict[str, str] = variables
        self.private_keys: set[str] = private_keys
        self.last_variable: "VariableOrderNode | None" = None
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


def visualize_node(node, level: int = 0):
    # each level of the tree adds two spaces to the indentation
    print(" " * level * 4 + node.name)
    for child in node.children:
        # recursive call with increased indentation level
        visualize_node(child, level + 1)


def compute_descendants(node):
    for child in node.children:
        node.descendants.append(child)
        # add all descendants of the child to the current node's descendants
        node.descendants += compute_descendants(child)
    return node.descendants


class VariableOrderNode:
    def __init__(self, name: str, data_type: str = "int", all_non_join_below: bool = False):
        self.name: str = name
        self.children: "List[VariableOrderNode]" = []
        # add descendants attribute
        self.descendants: "List[VariableOrderNode]" = []
        self.parent: "VariableOrderNode | None" = None
        self.id = -1
        self.data_type = data_type
        self.all_non_join_below = all_non_join_below

    def add_child(self, child: "VariableOrderNode"):
        self.children.append(child)
        child.parent = self

    def descendants_variables(self):
        res: set[str] = set()
        for child in self.descendants:
            res.add(child.name)
        return res

    def child_variables(self):
        res: set[str] = set()
        for child in self.children:
            res.update(child.child_variables())
            res.add(child.name)
        return res

    def parent_variables(self):
        if self.parent is None:
            return set()
        return self.parent.parent_variables().union({self.parent.name})

    def parent_ids(self):
        if self.parent is None:
            return set()
        return self.parent.parent_ids().union({self.parent.id})

    def set_id(self, _id):
        self.id = _id
        next_id = _id + 1
        for child in self.children:
            next_id = child.set_id(next_id)
        return next_id

    def generate_config(self):
        res = f"{self.id} {self.name} {map_data_type(self.data_type)} {self.parent.id if self.parent is not None else -1} {{{','.join([str(x) for x in self.parent_ids()])}}} 0\n"
        for child in self.children:
            res += child.generate_config()
        return res

    def generate_sql(self, ring):

        (s, n) = self.generate_sql_line(ring)

        if self.all_non_join_below:
            return s

        # remove duplicates in children based on name
        self.children = list({v.name: v for v in self.children}.values())
        vars = self.children

        # sort children by all_non_join_below with all_non_join_below = False first
        vars.sort(key=lambda x: x.all_non_join_below, reverse=True)

        for child in vars:
            s += child.generate_sql(ring)

        return s

    def generate_sql_line(self, ring_txt):

        if self.all_non_join_below:

            # materialise all descendant in a list (there is only one path)
            descendants = [self]
            iterator = self
            while len(iterator.children) > 0:
                iterator = iterator.children[0]
                descendants.append(iterator)

            descendants_types = ",".join(
                [path_sql_type_table[x.name] for x in descendants])
            descendants_names = ",".join([x.name for x in descendants])
            # generate the SQL
            s = f"\t[lift<{self.id}>: {ring_txt}<[{self.id}, {descendants_types}]>]({descendants_names}) *\n"
            return (s, len(descendants))

        else:
            s = f"\t[lift<{self.id}>: {ring_txt}<[{self.id}, {path_sql_type_table[self.name]}]>]({self.name}) *\n"
            return (s, 1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def map_data_type(data_type: str):
    if data_type == "INT" or data_type == "int":
        return "int"
    elif "CHAR" in data_type:
        return "string"
    elif data_type == "FLOAT" or data_type == "DECIMAL":
        return "double"
    else:
        print(f"Unknown data type: {data_type}")


# generate the variable order (d-tree file)
def generate_txt(all_relations: "List[Relation]", root: "VariableOrderNode", free_variables: set[str]):
    for relation in all_relations:
        iterator = root
        while True:
            if set(iterator.child_variables()).isdisjoint(set(relation.variables.keys())):
                # append the free variables to iterator to make sure they are on top of the bound variables
                variables_to_add = set(relation.variables.keys()).difference(
                    iterator.parent_variables().union({iterator.name}))

                for variable in variables_to_add.intersection(free_variables):
                    new_node = VariableOrderNode(
                        variable, relation.variables[variable])
                    iterator.add_child(new_node)
                    iterator = new_node

                for variable in variables_to_add.difference(free_variables):
                    new_node = VariableOrderNode(
                        variable, relation.variables[variable])
                    iterator.add_child(new_node)
                    iterator = new_node
                relation.last_variable = iterator
                break
            else:
                for child in iterator.children:
                    if not (set(child.child_variables()).union({child.name})).isdisjoint(set(relation.variables.keys())):
                        iterator = child
                        break

    root.set_id(0)
    all_vars = set()
    for rel in all_relations:
        all_vars.update(rel.variables.keys())
    config_start = f"{len(all_vars)} {len(all_relations)}\n"
    config_file = config_start + root.generate_config()
    for relation in all_relations:
        config_file += f"{relation.name} {relation.last_variable.id} {','.join(relation.variables.keys())}\n"
    print(config_file)

    return config_file


def compute_join_variables(relations):
    join_vars = set(relations[0].variables.keys())
    for rel in relations:
        join_vars = join_vars.intersection(set(rel.variables.keys()))
    return join_vars


def generate_sql_stream_text(all_relations: "List[Relation]", root: "VariableOrderNode", free_variables: set[str], q: str, path: str, ring_txt: str):
    # join_variables = compute_join_variables(all_relations)

    for relation in all_relations:
        iterator = root
        while True:
            if set(iterator.child_variables()).isdisjoint(set(relation.variables.keys())):
                # append the free variables to iterator
                variables_to_add = set(relation.variables.keys()).difference(
                    iterator.parent_variables().union({iterator.name}))

                for variable in variables_to_add.intersection(free_variables):
                    new_node = VariableOrderNode(
                        variable, relation.variables[variable])
                    iterator.add_child(new_node)
                    iterator = new_node
                    iterator.all_non_join_below = True
                relation.last_variable = iterator
                break
            else:
                for child in iterator.children:
                    if not (set(child.child_variables()).union({child.name})).isdisjoint(set(relation.variables.keys())):
                        iterator = child
                        break

    # visualize_node(root)


    s = f"IMPORT DTREE FROM FILE '{q}.txt';"
    s += "\n\n"

    s += "CREATE DISTRIBUTED TYPE RingFactorizedRelation\n"
    s += f"FROM FILE 'ring/{ring_txt}.hpp'\n"
    s += "WITH PARAMETER SCHEMA (dynamic_min);\n\n"

    for relation in all_relations:
        s += generate_relation_sql_text(relation, path)
        s += "\n"

    print(s)

    return s


def generate_sql_text(all_relations: "List[Relation]", root: "VariableOrderNode", free_variables: set[str], query_group: str, q: str, path: str, ring_txt: str):

    # join_variables = compute_join_variables(all_relations)

    for relation in all_relations:
        iterator = root
        while True:
            if set(iterator.child_variables()).isdisjoint(set(relation.variables.keys())):
                # append the free variables to iterator
                variables_to_add = set(relation.variables.keys()).difference(
                    iterator.parent_variables().union({iterator.name}))

                for variable in variables_to_add.intersection(free_variables):
                    new_node = VariableOrderNode(
                        variable, relation.variables[variable])
                    iterator.add_child(new_node)
                    iterator = new_node
                    iterator.all_non_join_below = True
                relation.last_variable = iterator
                break
            else:
                for child in iterator.children:
                    if not (set(child.child_variables()).union({child.name})).isdisjoint(set(relation.variables.keys())):
                        iterator = child
                        break

    # visualize_node(root)


    s = f"IMPORT DTREE FROM FILE '{query_group}-{q}.txt';"
    s += "\n\n"

    s += "CREATE DISTRIBUTED TYPE RingFactorizedRelation\n"
    s += f"FROM FILE 'ring/{ring_txt}.hpp'\n"
    s += "WITH PARAMETER SCHEMA (dynamic_min);\n\n"

    for relation in all_relations:
        s += generate_relation_sql_text(relation, path)
        s += "\n"

    s += "\n"
    root.set_id(0)
    s += "SELECT SUM(\n"

    s += root.generate_sql(ring_txt)
    # remove the last *
    s = s[::-1].replace('*', "", 1)[::-1]
    s += ")\nFROM "
    s += " NATURAL JOIN ".join([rel.name for rel in all_relations])
    s += ";\n\n"

    print(s)

    return s


def generate_relation_sql_text(relation: "Relation", path: str):
    s = f"CREATE STREAM {relation.name} (\n"
    for key, value in relation.variables.items():
        # s += f"\t{key} \t {path_sql_type_table[key]}, \n"
        s += f"\t{key} \t {value}, \n"
    s = s[:-3]
    s += f") \nFROM FILE './datasets/{path}/{relation.name}.csv' \nLINE DELIMITED CSV (delimiter := '|');\n"
    return s

def generate_application_text(all_relations: "List[Relation]", query_group: str, q: str, path: str):

    s = f"#ifndef APPLICATION_{query_group.upper()}_{q.upper()}_BASE_HPP\n"
    s += f"#define APPLICATION_{query_group.upper()}_{q.upper()}_BASE_HPP\n\n"
    s += "#include \"../application.hpp\"\n\n"
    s += f"const string dataPath = \"data/{path}\";\n\n"
    s += f"void Application::init_relations() {{\n"
    s += "\tclear_relations();\n\n"

    for relation in all_relations:
        s += generate_stream_text(relation)
        s += "\n"

    s += "\n"

    s += "}"

    s += "\tvoid Application::on_snapshot(dbtoaster::data_t& data) {\n"
    s += "\t\ton_end_processing(data, false);\n"
    s += "\t}\n\n"

    s += "\tvoid Application::on_begin_processing(dbtoaster::data_t& data) {\n\n"
    s += "\t}\n\n"

    s += "\tvoid Application::on_end_processing(dbtoaster::data_t& data, bool print_result) {\n"
    s += "\t\tif (print_result) {\n"
    s += "\t\t\tdata.serialize(std::cout, 0);\n"
    s += "\t\t}\n"
    s += "\t}\n\n"

    s += "\n\n"
    s += f"#endif /* APPLICATION_{query_group.upper()}_{q.upper()}_BASE_HPP */\n"
    
    
    print(s)

    return s

def generate_stream_text(relation_name):
    code = ""

    code += f"""#if defined(RELATION_{relation_name}_STATIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<{relation_name}_entry>(
            "{relation_name}", dataPath + "/{relation_name}.tbl", '|', true,
            [](dbtoaster::data_t& data) {{
                return [&]({relation_name}_entry& t) {{
                    data.on_insert_{relation_name}(t);
                }};
            }}
    )));
#elif defined(RELATION_{relation_name}_DYNAMIC) && defined(BATCH_SIZE)
    typedef const std::vector<DELTA_{relation_name}_entry>::iterator CIterator{relation_name};
    relations.push_back(std::unique_ptr<IRelation>(
        new BatchDispatchableRelation<DELTA_{relation_name}_entry>(
            "{relation_name}", dataPath + "/{relation_name}.tbl", '|', false,
            [](dbtoaster::data_t& data) {{
                return [&](CIterator{relation_name}& begin, CIterator{relation_name}& end) {{
                    data.on_batch_update_{relation_name}(begin, end);
                }};
            }}
    )));
#elif defined(RELATION_{relation_name}_DYNAMIC)
    relations.push_back(std::unique_ptr<IRelation>(
        new EventDispatchableRelation<{relation_name}_entry>(
            "{relation_name}", dataPath + "/{relation_name}.tbl", '|', false,
            [](dbtoaster::data_t& data) {{
                return [&]({relation_name}_entry& t) {{
                    data.on_insert_{relation_name}(t);
                }};
            }}
    )));
#endif"""

    return code
