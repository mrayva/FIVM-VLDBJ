#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4] / "aux"))

from variable_order import Relation, VariableOrderNode, generate_txt  # type: ignore
import tpch_schema as tpch  # type: ignore


KEY_MAP = {
    "nation": "nationkey",
    "cust": "custkey",
    "order": "orderkey",
    "supp": "suppkey",
}

SUPPLIER_SHARED = Relation(
    "supplier",
    {
        "suppkey": "int",
        "s_name": "string",
        "s_address": "string",
        "nationkey": "int",
        "s_phone": "string",
        "s_acctbal": "double",
        "s_comment": "string",
    },
    {"suppkey", "nationkey"},
)


def query_relations():
    return [tpch.Customer, tpch.Orders, tpch.Lineitem, SUPPLIER_SHARED, tpch.Nation, tpch.Region]


def build_chain(ordering):
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in ordering}
    for parent, child in zip(ordering, ordering[1:]):
        nodes[parent].add_child(nodes[child])
    root = nodes[ordering[0]]
    return root, query_relations(), {}


def build_bushy_vo5():
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in KEY_MAP}
    root = nodes["nation"]
    root.add_child(nodes["order"])
    nodes["order"].add_child(nodes["cust"])
    nodes["order"].add_child(nodes["supp"])
    return root, query_relations(), {}


def build_bushy_vo6():
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in KEY_MAP}
    root = nodes["order"]
    root.add_child(nodes["nation"])
    nodes["nation"].add_child(nodes["cust"])
    nodes["nation"].add_child(nodes["supp"])
    return root, query_relations(), {}


def build_bushy_vo7():
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in KEY_MAP}
    root = nodes["cust"]
    root.add_child(nodes["supp"])
    nodes["supp"].add_child(nodes["nation"])
    nodes["supp"].add_child(nodes["order"])
    return root, query_relations(), {}


VO_CONFIGS = [
    ("tpch_q5_vo1_nation_cust_order_supp", lambda: build_chain(["nation", "cust", "order", "supp"])),
    ("tpch_q5_vo2_order_supp_nation_cust", lambda: build_chain(["order", "supp", "nation", "cust"])),
    ("tpch_q5_vo3_supp_order_cust_nation", lambda: build_chain(["supp", "order", "cust", "nation"])),
    ("tpch_q5_vo4_cust_order_supp_nation", lambda: build_chain(["cust", "order", "supp", "nation"])),
    ("tpch_q5_vo5_nation_root_order_child_bushy", build_bushy_vo5),
    ("tpch_q5_vo6_order_root_nation_child_bushy", build_bushy_vo6),
    ("tpch_q5_vo7_cust_root_supp_child_bushy", build_bushy_vo7),
]

SCALES = ["sf0p1", "sf1"]
MODES = ["static", "dynamic"]
PRED_FLAGS = ["on", "off"]

BASE_DIR = Path(__file__).resolve().parent
VO_DIR = BASE_DIR / "variable_orders"
SQL_DIR = BASE_DIR / "sql_files"


def write_vo_files():
    VO_DIR.mkdir(parents=True, exist_ok=True)
    for existing in VO_DIR.glob("tpch_q5_*.txt"):
        existing.unlink()
    for name, builder in VO_CONFIGS:
        root, relations, free_vars = builder()
        out_path = VO_DIR / f"{name}.txt"
        content = generate_txt(relations, root, free_vars)
        out_path.write_text(content)
        print(f"Wrote VO: {out_path}")


def sql_template(mode, scale, pred_on, vo_file):
    base_path = f"./datasets/updates_{scale}_b10000_{mode}"
    where_clause = (
        "WHERE   r_name = 'ASIA'\n"
        "  AND   o_orderdate >= DATE('1994-01-01')\n"
        "  AND   o_orderdate < DATE('1995-01-01')\n"
        if pred_on
        else ""
    )

    sql = f"""IMPORT DTREE FROM FILE '../variable_orders/{vo_file}';

CREATE STREAM LINEITEM (
        orderkey         INT,
        partkey          INT,
        suppkey          INT,
        l_linenumber     INT,
        l_quantity       DECIMAL,
        l_extendedprice  DECIMAL,
        l_discount       DECIMAL,
        l_tax            DECIMAL,
        l_returnflag     CHAR(1),
        l_linestatus     CHAR(1),
        l_shipdate       DATE,
        l_commitdate     DATE,
        l_receiptdate    DATE,
        l_shipinstruct   CHAR(25),
        l_shipmode       CHAR(10),
        l_comment        VARCHAR(44)
    )
  FROM FILE '{base_path}/lineitem.csv'
  LINE DELIMITED CSV (delimiter := '|', predefined_batches := 'true');

CREATE STREAM ORDERS (
        orderkey         INT,
        custkey          INT,
        o_orderstatus    CHAR(1),
        o_totalprice     DECIMAL,
        o_orderdate      DATE,
        o_orderpriority  CHAR(15),
        o_clerk          CHAR(15),
        o_shippriority   INT,
        o_comment        VARCHAR(79)
    )
  FROM FILE '{base_path}/orders.csv'
  LINE DELIMITED CSV (delimiter := '|', predefined_batches := 'true');

CREATE STREAM CUSTOMER (
        custkey        INT,
        c_name         VARCHAR(25),
        c_address      VARCHAR(40),
        nationkey      INT,
        c_phone        CHAR(15),
        c_acctbal      DECIMAL,
        c_mktsegment   CHAR(10),
        c_comment      VARCHAR(117)
    )
  FROM FILE '{base_path}/customer.csv'
  LINE DELIMITED CSV (delimiter := '|', predefined_batches := 'true');

CREATE STREAM SUPPLIER (
        suppkey        INT,
        s_name         CHAR(25),
        s_address      VARCHAR(40),
        nationkey      INT,
        s_phone        CHAR(15),
        s_acctbal      DECIMAL,
        s_comment      VARCHAR(101)
    )
  FROM FILE '{base_path}/supplier.csv'
  LINE DELIMITED CSV (delimiter := '|', predefined_batches := 'true');

CREATE TABLE NATION (
        nationkey      INT,
        n_name         CHAR(25),
        regionkey      INT,
        n_comment      VARCHAR(152)
    )
  FROM FILE '{base_path}/nation.csv'
  LINE DELIMITED CSV (delimiter := '|');

CREATE TABLE REGION (
        regionkey      INT,
        r_name         CHAR(25),
        r_comment      VARCHAR(152)
    )
  FROM FILE '{base_path}/region.csv'
  LINE DELIMITED CSV (delimiter := '|');

SELECT n_name, SUM(l_extendedprice * (1 - l_discount))
FROM customer NATURAL JOIN orders NATURAL JOIN lineitem NATURAL JOIN supplier NATURAL JOIN nation NATURAL JOIN region
{where_clause}GROUP BY n_name;
"""
    return sql


def write_sql_files():
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    for existing in SQL_DIR.glob("tpch_q5_*.sql"):
        existing.unlink()
    vo_files = sorted(p.name for p in VO_DIR.glob("tpch_q5_*.txt"))
    for vo in vo_files:
        base = vo.removesuffix(".txt")
        for scale in SCALES:
            for mode in MODES:
                for pred in PRED_FLAGS:
                    pred_on = pred == "on"
                    out_name = f"{base}_{scale}_{mode}_pred_{pred}.sql"
                    out_path = SQL_DIR / out_name
                    out_path.write_text(sql_template(mode, scale, pred_on, vo))
                    print(f"Wrote SQL: {out_path}")


def main():
    write_vo_files()
    write_sql_files()


if __name__ == "__main__":
    main()
