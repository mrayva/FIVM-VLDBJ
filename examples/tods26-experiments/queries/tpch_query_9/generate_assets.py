#!/usr/bin/env python3
import sys
from copy import deepcopy
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4] / "aux"))

from variable_order import Relation, VariableOrderNode, generate_txt  # type: ignore
import tpch_schema as tpch  # type: ignore


KEY_MAP = {
    "order": "orderkey",
    "part": "partkey",
    "supp": "suppkey",
    "nation": "nationkey",
}


def build_supplier_relation():
    supplier = deepcopy(tpch.Supplier)
    supplier.variables = dict(supplier.variables)
    supplier.private_keys = set(supplier.private_keys)
    if "s_nationkey" in supplier.variables:
        supplier.variables["nationkey"] = supplier.variables.pop("s_nationkey")
        supplier.private_keys.discard("s_nationkey")
        supplier.private_keys.add("nationkey")
    return supplier


def build_relations() -> list[Relation]:
    return [tpch.Part, tpch.PartSupp, tpch.Lineitem, tpch.Orders, build_supplier_relation(), tpch.Nation]


def build_chain(ordering):
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in ordering}
    for parent, child in zip(ordering, ordering[1:]):
        nodes[parent].add_child(nodes[child])
    root = nodes[ordering[0]]
    return root, build_relations(), {}


def build_bushy_supp_root():
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in KEY_MAP}
    root = nodes["supp"]
    root.add_child(nodes["order"])
    nodes["order"].add_child(nodes["part"])
    root.add_child(nodes["nation"])
    return root, build_relations(), {}


def build_bushy_order_root():
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in KEY_MAP}
    root = nodes["order"]
    root.add_child(nodes["supp"])
    nodes["supp"].add_child(nodes["part"])
    nodes["supp"].add_child(nodes["nation"])
    return root, build_relations(), {}


def build_bushy_part_root():
    nodes = {name: VariableOrderNode(KEY_MAP[name]) for name in KEY_MAP}
    root = nodes["part"]
    root.add_child(nodes["supp"])
    nodes["supp"].add_child(nodes["order"])
    nodes["supp"].add_child(nodes["nation"])
    return root, build_relations(), {}


VO_CONFIGS = [
    ("tpch_q9_vo1_nation_supp_order_part", lambda: build_chain(["nation", "supp", "order", "part"])),
    ("tpch_q9_vo2_order_part_supp_nation", lambda: build_chain(["order", "part", "supp", "nation"])),
    ("tpch_q9_vo3_part_order_supp_nation", lambda: build_chain(["part", "order", "supp", "nation"])),
    ("tpch_q9_vo4_supp_order_part_nation", lambda: build_chain(["supp", "order", "part", "nation"])),
    ("tpch_q9_vo5_nation_supp_part_order", lambda: build_chain(["nation", "supp", "part", "order"])),
    ("tpch_q9_vo6_supp_root_bushy", build_bushy_supp_root),
    ("tpch_q9_vo7_order_root_bushy", build_bushy_order_root),
    ("tpch_q9_vo8_part_root_bushy", build_bushy_part_root),
]

SCALES = ["sf0p1", "sf1"]
MODES = ["static", "dynamic"]
PRED_FLAGS = ["on", "off"]

BASE_DIR = Path(__file__).resolve().parent
VO_DIR = BASE_DIR / "variable_orders"
SQL_DIR = BASE_DIR / "sql_files"


def write_vo_files():
    VO_DIR.mkdir(parents=True, exist_ok=True)
    for existing in VO_DIR.glob("tpch_q9_*.txt"):
        existing.unlink()
    for name, builder in VO_CONFIGS:
        root, relations, free_vars = builder()
        out_path = VO_DIR / f"{name}.txt"
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
    where_clause = "WHERE p_name LIKE '%green%'\n" if pred_on else ""

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

CREATE STREAM PART (
        partkey        INT,
        p_name         VARCHAR(55),
        p_mfgr         CHAR(25),
        p_brand        CHAR(10),
        p_type         VARCHAR(25),
        p_size         INT,
        p_container    CHAR(10),
        p_retailprice  DECIMAL,
        p_comment      VARCHAR(23)
    )
  FROM FILE '{base_path}/part.csv'
  LINE DELIMITED CSV (delimiter := '|', predefined_batches := 'true');

CREATE STREAM PARTSUPP (
        partkey         INT,
        suppkey         INT,
        ps_availqty     INT,
        ps_supplycost   DECIMAL,
        ps_comment      VARCHAR(199)
    )
  FROM FILE '{base_path}/partsupp.csv'
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

{nation_decl}

SELECT n_name,
       EXTRACT(year FROM o_orderdate),
       SUM((l_extendedprice * (1 - l_discount)) - (ps_supplycost * l_quantity))
FROM PART NATURAL JOIN PARTSUPP NATURAL JOIN LINEITEM NATURAL JOIN ORDERS NATURAL JOIN SUPPLIER NATURAL JOIN NATION
{where_clause}GROUP BY n_name, EXTRACT(year FROM o_orderdate);
"""
    return sql


def write_sql_files():
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    for existing in SQL_DIR.glob("tpch_q9_*.sql"):
        existing.unlink()
    vo_files = sorted(p.name for p in VO_DIR.glob("tpch_q9_*.txt"))
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
