from variable_order import Relation

Inventory = Relation("Inventory", {"locn": "int", "dateid": "int",
                     "ksn": "int", "inventoryunits": "int"}, {"locn", "dateid", "ksn"})
Location = Relation("Location",
                    {"locn": "int", "zip": "int", "rgn_cd": "int", "clim_zn_nbr": "int", "tot_area_sq_ft": "int",
                     "sell_area_sq_ft": "int", "avghhi": "int", "supertargetdistance": "double",
                     "supertargetdrivetime": "double", "targetdistance": "double", "targetdrivetime": "double",
                     "walmartdistance": "double", "walmartdrivetime": "double",
                     "walmartsupercenterdistance": "double", "walmartsupercenterdrivetime": "double"}, {"locn"})
Census = Relation("Census", {"zip": "int", "population": "int", "white": "int", "asian": "int", "pacific": "int",
                             "blackafrican": "int", "medianage": "double", "occupiedhouseunits": "int",
                             "houseunits": "int", "families": "int", "households": "int", "husbwife": "int",
                             "males": "int", "females": "int", "householdschildren": "int", "hispanic": "int"}, {"zip"})
Item = Relation("Item", {"ksn": "int", "subcategory": "int", "category": "int", "categoryCluster": "int",
                         "prize": "double"}, {"ksn"})
Weather = Relation("Weather", {"locn": "int", "dateid": "int", "rain": "int", "snow": "int", "maxtemp": "int",
                               "mintemp": "int", "meanwind": "double", "thunder": "int"}, {"locn", "dateid"})
Retailer_1_Q2 = Relation("q2", {"ksn": "int", "locn": "int", "dateid": "int",
                         "maxtemp": "int", "zip": "int", "rain": "int"}, {"ksn"})
Retailer_3_Q2 = Relation("R3q2", {"ksn": "int", "locn": "int", "dateid": "int",
                         "price": "double", "category": "int"}, {"ksn", "locn", "dateid"})


Part = Relation("part", {"partkey": "int", "p_name": "string", "p_mfgr": "string", "p_brand": "string", "p_type": "string",
                "p_size": "int", "p_container": "string", "p_retailprice": "double", "p_comment": "string"}, {"partkey"})
Supplier = Relation("supplier", {"suppkey": "int", "s_name": "string", "s_address": "string", "s_nationkey": "int",
                    "s_phone": "string", "s_acctbal": "double", "s_comment": "string"}, {"suppkey", "s_nationkey"})
PartSupp = Relation("partsupp", {"partkey": "int", "suppkey": "int", "ps_availqty": "int",
                    "ps_supplycost": "double", "ps_comment": "string"}, {"partkey", "suppkey"})
Customer = Relation("customer", {"custkey": "int", "c_name": "string", "c_address": "string", "nationkey": "int",
                    "c_phone": "string", "c_acctbal": "double", "c_mktsegment": "string", "c_comment": "string"}, {"custkey", "nationkey"})
Orders = Relation("orders", {"orderkey": "int", "custkey": "int", "o_orderstatus": "char", "o_totalprice": "double", "o_orderdate": "string",
                  "o_orderpriority": "string", "o_clerk": "string", "o_shippriority": "int", "o_comment": "string"}, {"orderkey"})
Lineitem = Relation("lineitem", {"orderkey": "int", "partkey": "int", "suppkey": "int", "l_linenumber": "int", "l_quantity": "double", "l_extendedprice": "double", "l_discount": "double", "l_tax": "double", "l_returnflag": "char",
                    "l_linestatus": "char", "l_shipdate": "string", "l_commitdate": "string", "l_receiptdate": "string", "l_shipinstruct": "string", "l_shipmode": "string", "l_comment": "string"}, {"orderkey", "partkey", "suppkey"})
Nation = Relation("nation", {"nationkey": "int", "n_name": "string",
                  "regionkey": "int", "n_comment": "string"}, {"nationkey"})
Region = Relation("region", {
                  "regionkey": "int", "r_name": "string", "r_comment": "string"}, {"regionkey"})
TPCH_1_Q2 = Relation("q2", {"orderkey": "int", "partkey": "int", "suppkey": "int",
                     "l_quantity": "double", "o_totalprice": "double"}, {"partkey", "suppkey"})


tpch_sql_type_table = {
    "custkey": "INT",
    "c_name": "VARCHAR(25)",
    "c_address": "VARCHAR(40)",
    "nationkey": "INT",
    "s_nationkey": "INT",
    "c_phone": "CHAR(15)",
    "c_acctbal": "DECIMAL",
    "c_mktsegment": "CHAR(10)",
    "c_comment": "VARCHAR(117)",
    "orderkey": "INT",
    "partkey": "INT",
    "suppkey": "INT",
    "l_linenumber": "INT",
    "l_quantity": "DECIMAL",
    "l_extendedprice": "DECIMAL",
    "l_discount": "DECIMAL",
    "l_tax": "DECIMAL",
    "l_returnflag": "CHAR(1)",
    "l_linestatus": "CHAR(1)",
    "l_shipdate": "CHAR(10)",
    "l_commitdate": "CHAR(10)",
    "l_receiptdate": "CHAR(10)",
    "l_shipinstruct": "CHAR(25)",
    "l_shipmode": "CHAR(10)",
    "l_comment": "VARCHAR(44)",
    "p_name": "VARCHAR(55)",
    "p_mfgr": "CHAR(25)",
    "p_brand": "CHAR(10)",
    "p_type": "VARCHAR(25)",
    "p_size": "INT",
    "p_container": "CHAR(10)",
    "p_retailprice": "DECIMAL",
    "p_comment": "VARCHAR(23)",
    "ps_availqty": "INT",
    "ps_supplycost": "DECIMAL",
    "ps_comment": "VARCHAR(199)",
    "s_name": "CHAR(25)",
    "s_address": "VARCHAR(40)",
    "s_phone": "CHAR(15)",
    "s_acctbal": "DECIMAL",
    "s_comment": "VARCHAR(101)",
    "o_custkey": "INT",
    "o_orderstatus": "CHAR(1)",
    "o_totalprice": "DECIMAL",
    "o_orderdate": "CHAR(10)",
    "o_orderpriority": "CHAR(15)",
    "o_clerk": "CHAR(15)",
    "o_shippriority": "INT",
    "o_comment": "VARCHAR(79)",
    "n_name": "CHAR(25)",
    "regionkey": "INT",
    "n_comment": "VARCHAR(152)",
    "r_name": "CHAR(25)",
    "r_comment": "VARCHAR(152)"
}


tpch_relations = [Part, Supplier, PartSupp,
                  Customer, Orders, Lineitem, Nation, Region]


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