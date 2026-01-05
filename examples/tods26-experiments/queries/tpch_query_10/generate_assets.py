#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4] / "aux"))

from variable_order import VariableOrderNode, generate_txt  # type: ignore
import tpch_schema as tpch  # type: ignore


PERMUTATIONS = [
    ("order", "cust", "nation"),
    ("order", "nation", "cust"),
    ("cust", "order", "nation"),
    ("cust", "nation", "order"),
    ("nation", "order", "cust"),
    ("nation", "cust", "order"),
]

SCALES = ["sf0p1", "sf1"]
MODES = ["static", "dynamic"]
PRED_FLAGS = ["on", "off"]

BASE_DIR = Path(__file__).resolve().parent
VO_DIR = BASE_DIR / "variable_orders"
SQL_DIR = BASE_DIR / "sql_files"


def build_vo_chain(ordering):
    nodes = {name: VariableOrderNode(f"{name}key") for name in ordering}
    for parent, child in zip(ordering, ordering[1:]):
        nodes[parent].add_child(nodes[child])
    root = nodes[ordering[0]]
    relations = [tpch.Orders, tpch.Customer, tpch.Lineitem, tpch.Nation]
    return root, relations, {}


def write_vo_files():
    VO_DIR.mkdir(parents=True, exist_ok=True)
    for ordering in PERMUTATIONS:
        root, relations, free_vars = build_vo_chain(ordering)
        name = f"tpch_q10_{'_'.join(ordering)}.txt"
        out_path = VO_DIR / name
        content = generate_txt(relations, root, free_vars)
        out_path.write_text(content)
        print(f"Wrote VO: {out_path}")


def sql_template(mode, scale, pred_on, vo_file):
    base_path = f"./datasets/updates_{scale}_b10000_{mode}"
    nation_decl = f"""
CREATE TABLE NATION (
        nationkey      INT,
        n_name         CHAR(25),
        regionkey      INT,
        n_comment      VARCHAR(152)
    )
  FROM FILE '{base_path}/nation.csv'
  LINE DELIMITED CSV (delimiter := '|');
"""
    nation_stream = f"""
CREATE STREAM NATION (
        nationkey      INT,
        n_name         CHAR(25),
        regionkey      INT,
        n_comment      VARCHAR(152)
    )
  FROM FILE '{base_path}/nation.csv'
  LINE DELIMITED CSV (delimiter := '|', predefined_batches := 'true');
"""
    where_clause = (
        "WHERE   o_orderdate >= DATE('1993-10-01')\n"
        "  AND   o_orderdate < DATE('1994-01-01')\n"
        "  AND   l_returnflag = 'R'\n"
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

{nation_decl if mode == 'static' else nation_stream}

SELECT  custkey, c_name, 
        c_acctbal,
        n_name,
        c_address,
        c_phone,
        c_comment,
        SUM(l_extendedprice * (1 - l_discount))
FROM    customer NATURAL JOIN orders NATURAL JOIN lineitem NATURAL JOIN nation
{where_clause}GROUP BY custkey, c_name, c_acctbal, c_phone, n_name, c_address, c_comment;
"""
    return sql


def write_sql_files():
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    vo_files = [p.name for p in VO_DIR.glob("tpch_q10_*.txt")]
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
