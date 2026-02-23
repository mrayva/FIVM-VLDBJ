import sys
from typing import List



def generate_retailer_all():
    root = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    ksn = VariableOrderNode("ksn")
    zip = VariableOrderNode("zip")
    root.add_child(dateid)
    dateid.add_child(ksn)
    root.add_child(zip)
    relations = [Inventory, Location, Census, Item, Weather]
    free_vars = {"locn", "dateid", "ksn", "zip", "category", "snow"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_3():
    root = VariableOrderNode("ksn")
    relations = [Item, Inventory]
    free_vars = {"locn", "dateid", "ksn", "category", "price"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_4Q1a():
    root = VariableOrderNode("ksn")
    locn = VariableOrderNode("locn")
    root.add_child(locn)
    relations = [Item, Inventory, Location]
    free_vars = {"locn", "ksn", "category", "zip"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_4Q1b():
    ksn = VariableOrderNode("ksn")
    root = VariableOrderNode("locn")
    root.add_child(ksn)
    relations = [Item, Inventory, Location]
    free_vars = {"locn", "ksn", "category", "zip"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_4Q2():
    root = VariableOrderNode("ksn")
    relations = [Item, Inventory]
    free_vars = {"locn", "ksn", "category", "price"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_1Q1b():
    root = VariableOrderNode("ksn")
    locn = VariableOrderNode("locn")
    root.add_child(locn)
    dateid = VariableOrderNode("dateid")
    locn.add_child(dateid)
    relations = [Item, Inventory, Location, Weather]
    free_vars = {"locn", "ksn", "category", "price"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_1Q1c():
    root = VariableOrderNode("ksn")
    relations = [Item, Retailer_1_Q2]
    free_vars = {"locn", "ksn", "category", "dateid", "rain", "zip"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_retailer_3Q1c():
    root = VariableOrderNode("locn")
    dateid = VariableOrderNode("dateid")
    root.add_child(dateid)
    relations = [Retailer_3_Q2, Weather, Location]
    free_vars = {"locn", "dateid", "rain", "zip", "category", "ksn"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_3Q2():
    root = VariableOrderNode("suppkey")
    part = VariableOrderNode("partkey")
    root.add_child(part)
    relations = [Supplier, PartSupp, Lineitem]
    free_vars = {"suppkey", "partkey", "l_quantity",
                 "ps_availqty", "ps_supplycost", "s_name"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_1Q1b():
    root = VariableOrderNode("partkey")
    supp = VariableOrderNode("suppkey")
    order = VariableOrderNode("orderkey")
    root.add_child(supp)
    supp.add_child(order)
    relations = [Part, PartSupp, Lineitem, Orders]
    free_vars = {"orderkey", "suppkey", "partkey",
                 "l_quantity", "ps_availqty", "p_name", "o_totalprice"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_1Q1c():
    root = VariableOrderNode("partkey")
    supp = VariableOrderNode("suppkey")
    root.add_child(supp)
    relations = [Part, PartSupp, TPCH_1_Q2]
    free_vars = {"orderkey", "suppkey", "partkey",
                 "l_quantity", "ps_availqty", "p_name", "o_totalprice"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_4Q3():
    root = VariableOrderNode("custkey")
    relations = [Customer, Orders]
    free_vars = {"custkey", "orderkey", "nationkey"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_5_Q1():
    nation = VariableOrderNode("nationkey")
    part = VariableOrderNode("partkey")
    supp = VariableOrderNode("suppkey")
    supp.add_child(part)
    supp.add_child(nation)
    relations = [Nation, Supplier, Customer, Part, PartSupp]
    free_vars = {"nationkey", "partkey", "suppkey",
                 "n_name", "s_name", "p_name", "ps_availqty"}
    res = generate_txt(relations, supp, free_vars)
    return res


def generate_TPCH_5_Q2():
    nation = VariableOrderNode("nationkey")
    relations = [Nation, Supplier, Customer]
    free_vars = {"nationkey", "suppkey", "n_name",
                 "s_name", "s_address", "custkey"}
    res = generate_txt(relations, nation, free_vars)
    return res


def generate_TPCH_5_Q3():
    part = VariableOrderNode("partkey")
    relations = [Part, PartSupp]
    free_vars = {"partkey", "suppkey", "ps_availqty", "p_name"}
    res = generate_txt(relations, part, free_vars)
    return res


def generate_retailer_aggr_Q1():
    root = VariableOrderNode("ksn")
    relations = [Inventory]
    free_vars = {"ksn"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_3_Q3():
    root = VariableOrderNode("suppkey")
    relations = [Supplier, PartSupp]
    free_vars = {"suppkey", "ps_availqty", "ps_supplycost", "s_name"}
    res = generate_txt(relations, root, free_vars)
    return res


def generate_TPCH_7_Q1():
    root = VariableOrderNode("regionkey")
    relations = [Nation, Region]
    free_vars = {"regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment"}

    return (root, relations, free_vars)

    # res = generate_txt(relations, root, free_vars) if not sql else generate_sql_text(
    #     relations, root, free_vars, query_group, q, path)
    # return res


def generate_TPCH_7_Q2():
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    nation.add_child(region)

    relations = [Nation, Region, Customer]
    free_vars = {"custkey", "c_name", "regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment"}

    return (nation, relations, free_vars)

    # res = generate_txt(relations, nation, free_vars) if not sql else generate_sql_text(
    #     relations, nation, free_vars, query_group, q, path)
    # res += "\n"
    # return res


def generate_TPCH_7_Q3():
    root = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    root.add_child(nation)
    nation.add_child(region)

    relations = [Nation, Region, Customer, Orders]
    free_vars = {"custkey", "c_name", "regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment", "orderkey", "o_orderstatus"}

    return (root, relations, free_vars)


def generate_TPCH_7_Q4():
    root = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    root.add_child(custkey)
    custkey.add_child(nation)
    nation.add_child(region)

    relations = [Nation, Region, Customer, Orders, Lineitem]
    free_vars = {"custkey", "c_name", "regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment", "orderkey", "o_orderstatus", "partkey", "l_quantity", "suppkey"}

    return (root, relations, free_vars)


def generate_TPCH_7_Q5():
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    orderkey.add_child(partkey)

    orderkey.add_child(custkey)
    custkey.add_child(nation)
    nation.add_child(region)

    relations = [Nation, Region, Customer, Orders, Lineitem, PartSupp, Part]
    free_vars = {"custkey", "c_name", "regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment", "orderkey", "o_orderstatus", "partkey", "l_quantity", "suppkey", "ps_avalqty", "p_name"}

    return (orderkey, relations, free_vars)


def generate_TPCH_7_Q6():
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    orderkey.add_child(partkey)

    orderkey.add_child(custkey)
    custkey.add_child(nation)
    nation.add_child(region)

    relations = [Nation, Region, Customer, Orders, Lineitem, PartSupp, Part]
    free_vars = {"custkey", "c_name", "regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment", "orderkey", "o_orderstatus", "partkey", "l_quantity", "suppkey", "ps_avalqty", "p_name"}

    return (orderkey, relations, free_vars)


def generate_TPCH_7_Q7():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    orderkey.add_child(partkey)
    partkey.add_child(suppkey)

    orderkey.add_child(custkey)
    custkey.add_child(nation)
    nation.add_child(region)

    relations = [Nation, Region, Customer, Orders,
                 Lineitem, PartSupp, Part, Supplier]
    free_vars = {"custkey", "c_name", "regionkey", "nationkey", "n_name",
                 "r_name", "r_comment", "n_comment", "orderkey", "o_orderstatus", "partkey", "l_quantity", "suppkey", "ps_avalqty", "p_name", "s_name"}

    return (orderkey, relations, free_vars)

def generate_TPCH_8_Q1():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    suppkey.add_child(partkey)

    relations = [PartSupp, Lineitem]
    free_vars = {"ps_avalqty", "partkey", "suppkey", "l_quantity", "orderkey"}

    return (suppkey, relations, free_vars)

def generate_TPCH_8_Q2():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    relations = [Orders, Customer]
    free_vars = {"orderkey", "custkey", "o_orderstatus", "c_name"}

    return (custkey, relations, free_vars)

def generate_TPCH_8_Q3():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    orderkey.add_child(partkey)
    partkey.add_child(suppkey)

    relations = [PartSupp, Lineitem, Orders]
    free_vars = {"ps_avalqty", "partkey", "suppkey", "l_quantity", "orderkey", "o_orderstatus", "custkey"}

    return (orderkey, relations, free_vars)

def generate_TPCH_8_Q4():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")

    suppkey.add_child(partkey)

    relations = [PartSupp, Lineitem, Part]
    free_vars = {"ps_avalqty", "partkey", "suppkey", "l_quantity", "orderkey", "p_name"}

    return (suppkey, relations, free_vars)

def generate_TPCH_8_Q5():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")
    nation = VariableOrderNode("nationkey")
    region = VariableOrderNode("regionkey")


    orderkey.add_child(partkey)
    partkey.add_child(suppkey)
    orderkey.add_child(custkey)

    relations = [PartSupp, Lineitem, Orders, Customer]
    free_vars = {"ps_avalqty", "partkey", "suppkey", "l_quantity", "orderkey", "o_orderstatus", "custkey", "c_name"}

    return (orderkey, relations, free_vars)

def generate_TPCH_8_Q6():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")

    orderkey.add_child(partkey)
    partkey.add_child(suppkey)
    orderkey.add_child(custkey)

    relations = [PartSupp, Lineitem, Orders, Customer, Part]
    free_vars = {"ps_avalqty", "partkey", "suppkey", "l_quantity", "orderkey", "o_orderstatus", "custkey", "c_name", "p_name"}

    return (orderkey, relations, free_vars)

def generate_TPCH_8_Q7():
    suppkey = VariableOrderNode("suppkey")
    partkey = VariableOrderNode("partkey")
    orderkey = VariableOrderNode("orderkey")
    custkey = VariableOrderNode("custkey")

    orderkey.add_child(partkey)
    partkey.add_child(suppkey)
    orderkey.add_child(custkey)

    relations = [PartSupp, Lineitem, Orders, Customer, Part, Supplier]
    free_vars = {"ps_avalqty", "partkey", "suppkey", "l_quantity", "orderkey", "o_orderstatus", "custkey", "c_name", "p_name", "s_name"}

    return (orderkey, relations, free_vars)

def construct_balanced(attrs):
    if len(attrs) == 0:
        return None
    if len(attrs) == 1:
        return VariableOrderNode(f"A{attrs[0]}")
    
    m = len(attrs) // 2
    root = VariableOrderNode(f"A{attrs[m]}")
    left = construct_balanced(attrs[:m])
    right = construct_balanced(attrs[m+1:])

    if left is not None:
        root.add_child(left)
    if right is not None:
        root.add_child(right)

    return root

def construct_left_deep(attrs):
    if len(attrs) == 0:
        return None

    root = VariableOrderNode(f"A{attrs[0]}")
    left = construct_left_deep(attrs[1:])
    if left is not None:
        root.add_child(left)

    return root

def generate_path_query(n):
    attrs = [i+1 for i in range(n+1)]
    # root = construct_balanced(attrs)
    root = construct_left_deep(attrs)
    relations = [path_relations[i] for i in range(n)]
    free_vars = set([f"A{i}" for i in range(n+1)])

    return (root, relations, free_vars)


def main(args):
    # big queries
    query_group = args[0] # prefix of the query name
    q = args[1] # query name
    path = args[2] # path to dataset
    is_sql = args[3]
    ring = args[4]
    # if args has 5 elements, then we are redirecting the output to a file
    redirect = len(args) == 6

    path_len = int(q.split("-")[0][1:])
    # path_len = int(q[1:])

    root, relations, free_vars = generate_path_query(path_len)

    res = ""

    
    ring_txt = ""
    if ring == "factorized":
        ring_txt = "RingFactorizedRelation"
    elif ring == "listing":
        ring_txt = "RingRelation"


    if is_sql == "sql":
        res = generate_sql_text(relations, root, free_vars, query_group, q, path, ring_txt)
    elif is_sql == "vo":
        res = generate_txt(relations, root, free_vars)
    elif is_sql == "app":
        res = generate_application_text(relations, query_group, q, path)


    res += "\n"

    if not redirect:
        visualize_node(root)

    return res


if __name__ == "__main__":
    # Pass the command-line arguments (excluding the script name) to the main function
    main(sys.argv[1:])
