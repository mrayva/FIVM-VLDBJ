from variable_order import Relation

Part = Relation(
    "part",
    {
        "partkey": "int",
        "p_name": "string",
        "p_mfgr": "string",
        "p_brand": "string",
        "p_type": "string",
        "p_size": "int",
        "p_container": "string",
        "p_retailprice": "double",
        "p_comment": "string",
    },
    {"partkey"},
)
Supplier = Relation(
    "supplier",
    {
        "suppkey": "int",
        "s_name": "string",
        "s_address": "string",
        "s_nationkey": "int",
        "s_phone": "string",
        "s_acctbal": "double",
        "s_comment": "string",
    },
    {"suppkey", "s_nationkey"},
)
PartSupp = Relation(
    "partsupp",
    {
        "partkey": "int",
        "suppkey": "int",
        "ps_availqty": "int",
        "ps_supplycost": "double",
        "ps_comment": "string",
    },
    {"partkey", "suppkey"},
)
Customer = Relation(
    "customer",
    {
        "custkey": "int",
        "c_name": "string",
        "c_address": "string",
        "nationkey": "int",
        "c_phone": "string",
        "c_acctbal": "double",
        "c_mktsegment": "string",
        "c_comment": "string",
    },
    {"custkey", "nationkey"},
)
Orders = Relation(
    "orders",
    {
        "orderkey": "int",
        "custkey": "int",
        "o_orderstatus": "char",
        "o_totalprice": "double",
        "o_orderdate": "date",
        "o_orderpriority": "string",
        "o_clerk": "string",
        "o_shippriority": "int",
        "o_comment": "string",
    },
    {"orderkey"},
)
Lineitem = Relation(
    "lineitem",
    {
        "orderkey": "int",
        "partkey": "int",
        "suppkey": "int",
        "l_linenumber": "int",
        "l_quantity": "double",
        "l_extendedprice": "double",
        "l_discount": "double",
        "l_tax": "double",
        "l_returnflag": "char",
        "l_linestatus": "char",
        "l_shipdate": "date",
        "l_commitdate": "date",
        "l_receiptdate": "date",
        "l_shipinstruct": "string",
        "l_shipmode": "string",
        "l_comment": "string",
    },
    {"orderkey", "partkey", "suppkey"},
)
Nation = Relation(
    "nation",
    {"nationkey": "int", "n_name": "string", "regionkey": "int", "n_comment": "string"},
    {"nationkey"},
)
Region = Relation(
    "region",
    {"regionkey": "int", "r_name": "string", "r_comment": "string"},
    {"regionkey"},
)
TPCH_1_Q2 = Relation(
    "q2",
    {
        "orderkey": "int",
        "partkey": "int",
        "suppkey": "int",
        "l_quantity": "double",
        "o_totalprice": "double",
    },
    {"partkey", "suppkey"},
)


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
    "l_shipdate": "DATE",
    "l_commitdate": "DATE",
    "l_receiptdate": "DATE",
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
    "o_orderdate": "DATE",
    "o_orderpriority": "CHAR(15)",
    "o_clerk": "CHAR(15)",
    "o_shippriority": "INT",
    "o_comment": "VARCHAR(79)",
    "n_name": "CHAR(25)",
    "regionkey": "INT",
    "n_comment": "VARCHAR(152)",
    "r_name": "CHAR(25)",
    "r_comment": "VARCHAR(152)",
}


tpch_relations = [Part, Supplier, PartSupp, Customer, Orders, Lineitem, Nation, Region]
