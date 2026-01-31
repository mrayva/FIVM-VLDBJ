#!/usr/bin/env python3
"""
Cost Model Computation for TPC-H Q10 - All Variable Orders (vo1-vo5)

This script computes all statistics from the TPC-H database and applies
the cost model formulas for each variable order.

Usage: python q10_all_vo_cost.py [--db path/to/tpch.duckdb] [--batch 10000]
"""

import duckdb
import argparse
from dataclasses import dataclass


@dataclass
class Config:
    db_path: str = "tpch.duckdb"
    batch_size: int = 10000
    order_pred: str = "o_orderdate >= '1993-10-01' AND o_orderdate < '1994-01-01'"
    lineitem_pred: str = "l_returnflag = 'R'"
    updates_db: str = None  # optional path to updates.duckdb to derive batch sizes


class Statistics:
    """Container for all statistics needed by the cost model."""

    def __init__(self, con, cfg: Config, with_predicates: bool):
        self.with_predicates = with_predicates
        self.cfg = cfg

        # Get table sizes
        self.table_sizes = self._get_table_sizes(con)

        # Get selectivities
        self.selectivities = self._get_selectivities(con)

        # Compute batch sizes
        self.batch = self._compute_batch_sizes()

        # Compute all degrees
        self.deg = self._compute_all_degrees(con)

        # Compute domain sizes
        self.dom = self._compute_domain_sizes(con)

    def _get_table_sizes(self, con) -> dict:
        sizes = {}
        for table in ['nation', 'customer', 'orders', 'lineitem']:
            sizes[table] = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        sizes['total'] = sum(sizes.values())
        return sizes

    def _get_selectivities(self, con) -> dict:
        sel_o = con.execute(f"""
            SELECT AVG(CASE WHEN {self.cfg.order_pred} THEN 1.0 ELSE 0.0 END) FROM orders
        """).fetchone()[0]
        sel_l = con.execute(f"""
            SELECT AVG(CASE WHEN {self.cfg.lineitem_pred} THEN 1.0 ELSE 0.0 END) FROM lineitem
        """).fetchone()[0]
        return {'orders': sel_o, 'lineitem': sel_l}

    def _compute_batch_sizes(self) -> dict:
        """
        Derive per-table batch sizes. Prefer observed averages from updates.duckdb
        when cfg.updates_db is provided; otherwise fall back to proportional split.
        """
        if self.cfg.updates_db:
            try:
                con_upd = duckdb.connect(self.cfg.updates_db, read_only=True)
                sizes = {}
                for tbl in ['lineitem', 'orders', 'customer', 'nation']:
                    total = con_upd.execute(f"SELECT COUNT(*) FROM {tbl}_updates").fetchone()[0]
                    mx = con_upd.execute(f"SELECT MAX(batch_id) FROM {tbl}_updates").fetchone()[0]
                    if mx and mx > 0:
                        sizes[tbl] = total / mx
                    else:
                        sizes[tbl] = 0.0
                con_upd.close()
                # nation/region may be static (zero); keep them as-is
                return {
                    'U_N': sizes.get('nation', 0.0),
                    'U_C': sizes.get('customer', 0.0),
                    'U_O': sizes.get('orders', 0.0),
                    'U_L': sizes.get('lineitem', 0.0),
                }
            except Exception as e:
                print(f"Warning: failed to load updates DB {self.cfg.updates_db}: {e}. Falling back to proportional split.")

        total = self.table_sizes['total']
        batch = self.cfg.batch_size

        U_N = batch * self.table_sizes['nation'] / total
        U_C = batch * self.table_sizes['customer'] / total
        U_O = batch * self.table_sizes['orders'] / total
        U_L = batch * self.table_sizes['lineitem'] / total

        if self.with_predicates:
            U_O *= self.selectivities['orders']
            U_L *= self.selectivities['lineitem']

        return {'U_N': U_N, 'U_C': U_C, 'U_O': U_O, 'U_L': U_L}

    def _compute_all_degrees(self, con) -> dict:
        """Compute all degrees needed by any view order."""
        deg = {}
        cfg = self.cfg
        wp = self.with_predicates

        # Primary key degrees (always 1)
        deg['C_ckey'] = 1.0
        deg['N_nkey'] = 1.0

        if wp:
            pred_o = f"WHERE {cfg.order_pred}"
            pred_l = f"WHERE {cfg.lineitem_pred}"
            pred_ol = f"WHERE {cfg.order_pred} AND {cfg.lineitem_pred}"
        else:
            pred_o = ""
            pred_l = ""
            pred_ol = ""

        # deg_L(*|okey): O probes L on orderkey
        if wp:
            deg['L_okey'] = con.execute(f"""
                SELECT AVG(l_cnt) FROM (
                    SELECT o.o_orderkey, COALESCE(l.cnt, 0) as l_cnt
                    FROM orders o
                    LEFT JOIN (SELECT l_orderkey, COUNT(*) as cnt FROM lineitem {pred_l} GROUP BY l_orderkey) l
                    ON o.o_orderkey = l.l_orderkey
                    {pred_o}
                )
            """).fetchone()[0] or 0
        else:
            deg['L_okey'] = con.execute("""
                SELECT AVG(l_cnt) FROM (
                    SELECT o.o_orderkey, COUNT(l.l_orderkey) as l_cnt
                    FROM orders o LEFT JOIN lineitem l ON o.o_orderkey = l.l_orderkey
                    GROUP BY o.o_orderkey
                )
            """).fetchone()[0] or 0

        # deg_O(*|okey): L probes O on orderkey
        if wp:
            deg['O_okey'] = con.execute(f"""
                SELECT AVG(o_cnt) FROM (
                    SELECT l.l_orderkey, COALESCE(o.cnt, 0) as o_cnt
                    FROM (SELECT DISTINCT l_orderkey FROM lineitem {pred_l}) l
                    LEFT JOIN (SELECT o_orderkey, 1 as cnt FROM orders {pred_o}) o
                    ON l.l_orderkey = o.o_orderkey
                )
            """).fetchone()[0] or 0
        else:
            deg['O_okey'] = 1.0  # orderkey is PK

        # deg_O(*|ckey): C probes O on custkey
        if wp:
            deg['O_ckey'] = con.execute(f"""
                SELECT AVG(o_cnt) FROM (
                    SELECT c.c_custkey, COALESCE(o.cnt, 0) as o_cnt
                    FROM customer c
                    LEFT JOIN (SELECT o_custkey, COUNT(*) as cnt FROM orders {pred_o} GROUP BY o_custkey) o
                    ON c.c_custkey = o.o_custkey
                )
            """).fetchone()[0] or 0
        else:
            deg['O_ckey'] = con.execute("""
                SELECT AVG(o_cnt) FROM (
                    SELECT c.c_custkey, COUNT(o.o_orderkey) as o_cnt
                    FROM customer c LEFT JOIN orders o ON c.c_custkey = o.o_custkey
                    GROUP BY c.c_custkey
                )
            """).fetchone()[0] or 0

        # deg_C(*|nkey): N probes C on nationkey
        deg['C_nkey'] = con.execute("""
            SELECT AVG(c_cnt) FROM (
                SELECT n.n_nationkey, COUNT(c.c_custkey) as c_cnt
                FROM nation n LEFT JOIN customer c ON n.n_nationkey = c.c_nationkey
                GROUP BY n.n_nationkey
            )
        """).fetchone()[0] or 0

        # View-specific degrees
        self._compute_view_degrees(con, deg)

        return deg

    def _compute_view_degrees(self, con, deg: dict):
        """Compute degrees for materialized views."""
        cfg = self.cfg
        wp = self.with_predicates

        if wp:
            # V_OL: O^P ⋈ L^P aggregated by custkey
            # deg_V_OL(*|ckey): C probes V_OL
            deg['V_OL_ckey'] = con.execute(f"""
                SELECT AVG(vol_cnt) FROM (
                    SELECT c.c_custkey, COALESCE(vol.cnt, 0) as vol_cnt
                    FROM customer c
                    LEFT JOIN (
                        SELECT DISTINCT o.o_custkey, 1 as cnt
                        FROM orders o JOIN lineitem l ON o.o_orderkey = l.l_orderkey
                        WHERE {cfg.order_pred} AND {cfg.lineitem_pred}
                    ) vol ON c.c_custkey = vol.o_custkey
                )
            """).fetchone()[0] or 0

            # V_COL: C ⋈ V_OL
            # deg_V_COL(*|nkey): N probes V_COL
            deg['V_COL_nkey'] = con.execute(f"""
                SELECT AVG(vcol_cnt) FROM (
                    SELECT n.n_nationkey, COALESCE(vcol.cnt, 0) as vcol_cnt
                    FROM nation n
                    LEFT JOIN (
                        SELECT c.c_nationkey, COUNT(DISTINCT c.c_custkey) as cnt
                        FROM customer c JOIN orders o ON c.c_custkey = o.o_custkey
                        JOIN lineitem l ON o.o_orderkey = l.l_orderkey
                        WHERE {cfg.order_pred} AND {cfg.lineitem_pred}
                        GROUP BY c.c_nationkey
                    ) vcol ON n.n_nationkey = vcol.c_nationkey
                )
            """).fetchone()[0] or 0

            # V_CO: C ⋈ O^P (for vo2)
            # deg_V_CO(*|okey): L probes V_CO
            deg['V_CO_okey'] = con.execute(f"""
                SELECT AVG(vco_cnt) FROM (
                    SELECT l.l_orderkey, COALESCE(vco.cnt, 0) as vco_cnt
                    FROM (SELECT DISTINCT l_orderkey FROM lineitem WHERE {cfg.lineitem_pred}) l
                    LEFT JOIN (
                        SELECT o.o_orderkey, 1 as cnt
                        FROM orders o WHERE {cfg.order_pred}
                    ) vco ON l.l_orderkey = vco.o_orderkey
                )
            """).fetchone()[0] or 0

            # V_NC: N ⋈ C (for vo3, vo5)
            # deg_V_NC(*|ckey): O probes V_NC / V_OL probes V_NC
            deg['V_NC_ckey'] = con.execute("""
                SELECT AVG(vnc_cnt) FROM (
                    SELECT o.o_custkey, COALESCE(vnc.cnt, 0) as vnc_cnt
                    FROM (SELECT DISTINCT o_custkey FROM orders) o
                    LEFT JOIN (
                        SELECT c.c_custkey, 1 as cnt FROM customer c
                    ) vnc ON o.o_custkey = vnc.c_custkey
                )
            """).fetchone()[0] or 0

            # V_NCO: V_NC ⋈ O^P (for vo3, vo4)
            # deg_V_NCO(*|okey): L probes V_NCO
            deg['V_NCO_okey'] = con.execute(f"""
                SELECT AVG(vnco_cnt) FROM (
                    SELECT l.l_orderkey, COALESCE(vnco.cnt, 0) as vnco_cnt
                    FROM (SELECT DISTINCT l_orderkey FROM lineitem WHERE {cfg.lineitem_pred}) l
                    LEFT JOIN (
                        SELECT o.o_orderkey, 1 as cnt
                        FROM customer c JOIN orders o ON c.c_custkey = o.o_custkey
                        WHERE {cfg.order_pred}
                    ) vnco ON l.l_orderkey = vnco.o_orderkey
                )
            """).fetchone()[0] or 0

            # V_CO for vo4: C ⋈ O^P
            # deg_V_CO(*|nkey): N probes V_CO
            deg['V_CO_nkey'] = con.execute(f"""
                SELECT AVG(vco_cnt) FROM (
                    SELECT n.n_nationkey, COALESCE(vco.cnt, 0) as vco_cnt
                    FROM nation n
                    LEFT JOIN (
                        SELECT c.c_nationkey, COUNT(*) as cnt
                        FROM customer c JOIN orders o ON c.c_custkey = o.o_custkey
                        WHERE {cfg.order_pred}
                        GROUP BY c.c_nationkey
                    ) vco ON n.n_nationkey = vco.c_nationkey
                )
            """).fetchone()[0] or 0

        else:  # No predicates
            deg['V_OL_ckey'] = con.execute("""
                SELECT AVG(vol_cnt) FROM (
                    SELECT c.c_custkey, COALESCE(vol.cnt, 0) as vol_cnt
                    FROM customer c
                    LEFT JOIN (SELECT DISTINCT o_custkey, 1 as cnt FROM orders) vol
                    ON c.c_custkey = vol.o_custkey
                )
            """).fetchone()[0] or 0

            deg['V_COL_nkey'] = con.execute("""
                SELECT AVG(vcol_cnt) FROM (
                    SELECT n.n_nationkey, COALESCE(vcol.cnt, 0) as vcol_cnt
                    FROM nation n
                    LEFT JOIN (SELECT c_nationkey, COUNT(*) as cnt FROM customer GROUP BY c_nationkey) vcol
                    ON n.n_nationkey = vcol.c_nationkey
                )
            """).fetchone()[0] or 0

            deg['V_CO_okey'] = 1.0  # Each order has one customer

            deg['V_NC_ckey'] = 1.0  # Each customer exists

            deg['V_NCO_okey'] = 1.0  # Each order has one customer

            deg['V_CO_nkey'] = deg['C_nkey'] * deg['O_ckey']  # Approx

    def _compute_domain_sizes(self, con) -> dict:
        """Compute aggregation domain sizes."""
        cfg = self.cfg
        dom = {}

        if self.with_predicates:
            # |Dom(custkey)| in O^P ⋈ L^P
            dom['custkey_OL'] = con.execute(f"""
                SELECT COUNT(DISTINCT o.o_custkey)
                FROM orders o JOIN lineitem l ON o.o_orderkey = l.l_orderkey
                WHERE {cfg.order_pred} AND {cfg.lineitem_pred}
            """).fetchone()[0]

            # |Dom(orderkey)| in O^P ⋈ L^P
            dom['orderkey_OL'] = con.execute(f"""
                SELECT COUNT(DISTINCT o.o_orderkey)
                FROM orders o JOIN lineitem l ON o.o_orderkey = l.l_orderkey
                WHERE {cfg.order_pred} AND {cfg.lineitem_pred}
            """).fetchone()[0]
        else:
            dom['custkey_OL'] = con.execute("SELECT COUNT(DISTINCT o_custkey) FROM orders").fetchone()[0]
            dom['orderkey_OL'] = con.execute("SELECT COUNT(DISTINCT o_orderkey) FROM orders").fetchone()[0]

        return dom


def compute_vo1(stats: Statistics, U_N: float) -> dict:
    """
    vo1: orderkey -> custkey -> nationkey

    V_NCOL (root, @orderkey, AGG -> custkey,nationkey)
    ├── L^P
    └── V_NCO (@custkey)
        ├── O^P
        └── V_NC (@nationkey)
            ├── N
            └── C
    """
    b = stats.batch
    d = stats.deg
    dom = stats.dom['orderkey_OL']

    # L path: L -> V_NCOL (agg at root)
    delta_join_L = b['U_L'] * d['V_NCO_okey']
    delta_agg_L = min(delta_join_L, dom)
    S_L = delta_join_L + delta_agg_L

    # O path: O -> V_NCO -> V_NCOL (agg)
    delta_O = b['U_O'] * d['V_NC_ckey']
    delta_join_O = delta_O * d['L_okey']
    delta_agg_O = min(delta_join_O, dom)
    S_O = delta_O + delta_join_O + delta_agg_O

    # C path: C -> V_NC -> V_NCO -> V_NCOL (agg)
    delta_C1 = b['U_C'] * d['N_nkey']
    delta_C2 = delta_C1 * d['O_ckey']
    delta_join_C = delta_C2 * d['L_okey']
    delta_agg_C = min(delta_join_C, dom)
    S_C = delta_C1 + delta_C2 + delta_join_C + delta_agg_C

    # N path: N -> V_NC -> V_NCO -> V_NCOL (agg)
    delta_N1 = U_N * d['C_nkey']
    delta_N2 = delta_N1 * d['O_ckey']
    delta_join_N = delta_N2 * d['L_okey']
    delta_agg_N = min(delta_join_N, dom)
    S_N = delta_N1 + delta_N2 + delta_join_N + delta_agg_N

    return {'S_N': S_N, 'S_C': S_C, 'S_O': S_O, 'S_L': S_L,
            'total': S_N + S_C + S_O + S_L}


def compute_vo2(stats: Statistics, U_N: float) -> dict:
    """
    vo2: orderkey -> nationkey -> custkey

    V_NCOL (root, @orderkey, AGG -> custkey,nationkey)
    ├── L^P
    └── V_NCO (@nationkey)
        ├── N
        └── V_CO (@custkey)
            ├── C
            └── O^P
    """
    b = stats.batch
    d = stats.deg
    dom = stats.dom['orderkey_OL']

    # L path: L -> V_NCOL (agg at root)
    delta_join_L = b['U_L'] * d['V_NCO_okey']
    delta_agg_L = min(delta_join_L, dom)
    S_L = delta_join_L + delta_agg_L

    # N path: N -> V_NCO -> V_NCOL (agg)
    delta_N = U_N * d['V_CO_nkey']
    delta_join_N = delta_N * d['L_okey']
    delta_agg_N = min(delta_join_N, dom)
    S_N = delta_N + delta_join_N + delta_agg_N

    # C path: C -> V_CO -> V_NCO -> V_NCOL (agg)
    delta_C1 = b['U_C'] * d['O_ckey']
    delta_C2 = delta_C1 * d['N_nkey']
    delta_join_C = delta_C2 * d['L_okey']
    delta_agg_C = min(delta_join_C, dom)
    S_C = delta_C1 + delta_C2 + delta_join_C + delta_agg_C

    # O path: O -> V_CO -> V_NCO -> V_NCOL (agg)
    delta_O1 = b['U_O'] * d['C_ckey']
    delta_O2 = delta_O1 * d['N_nkey']
    delta_join_O = delta_O2 * d['L_okey']
    delta_agg_O = min(delta_join_O, dom)
    S_O = delta_O1 + delta_O2 + delta_join_O + delta_agg_O

    return {'S_N': S_N, 'S_C': S_C, 'S_O': S_O, 'S_L': S_L,
            'total': S_N + S_C + S_O + S_L}


def compute_vo3(stats: Statistics, U_N: float) -> dict:
    """
    vo3: nationkey -> custkey -> orderkey

    V_NCOL (root, @nationkey)
    ├── N
    └── V_COL (@custkey)
        ├── C
        └── V_OL (@orderkey, AGG -> custkey)
            ├── O^P
            └── L^P
    """
    b = stats.batch
    d = stats.deg
    dom = stats.dom['custkey_OL']

    # Path multiplier for O/L path: through V_OL, V_COL, V_NCOL
    path_mult = 1 + d['C_ckey'] * (1 + d['N_nkey'])  # = 3

    S_N = U_N * d['V_COL_nkey']
    S_C = b['U_C'] * d['V_OL_ckey'] * (1 + d['N_nkey'])

    delta_join_O = b['U_O'] * d['L_okey']
    delta_agg_O = min(delta_join_O, dom)
    S_O = (delta_join_O + delta_agg_O) * path_mult

    delta_join_L = b['U_L'] * d['O_okey']
    delta_agg_L = min(delta_join_L, dom)
    S_L = (delta_join_L + delta_agg_L) * path_mult

    return {'S_N': S_N, 'S_C': S_C, 'S_O': S_O, 'S_L': S_L,
            'total': S_N + S_C + S_O + S_L}


def compute_vo4(stats: Statistics, U_N: float) -> dict:
    """
    vo4: nationkey -> orderkey -> custkey

    V_NCOL (root, @nationkey)
    ├── N
    └── V_COL (@orderkey, AGG -> custkey)
        ├── L^P
        └── V_CO (@custkey)
            ├── C
            └── O^P
    """
    b = stats.batch
    d = stats.deg
    dom = stats.dom['custkey_OL']

    S_N = U_N * d['V_COL_nkey']

    # L path: L -> V_COL (agg) -> V_NCOL
    delta_join_L = b['U_L'] * d['V_CO_okey']
    delta_agg_L = min(delta_join_L, dom)
    S_L = (delta_join_L + delta_agg_L) * (1 + d['N_nkey'])

    # C path: C -> V_CO -> V_COL (agg) -> V_NCOL
    delta_C = b['U_C'] * d['O_ckey']
    delta_join_C = delta_C * d['L_okey']
    delta_agg_C = min(delta_join_C, dom)
    S_C = delta_C + (delta_join_C + delta_agg_C) * (1 + d['N_nkey'])

    # O path: O -> V_CO -> V_COL (agg) -> V_NCOL
    delta_O = b['U_O'] * d['C_ckey']
    delta_join_O = delta_O * d['L_okey']
    delta_agg_O = min(delta_join_O, dom)
    S_O = delta_O + (delta_join_O + delta_agg_O) * (1 + d['N_nkey'])

    return {'S_N': S_N, 'S_C': S_C, 'S_O': S_O, 'S_L': S_L,
            'total': S_N + S_C + S_O + S_L}


def compute_vo5(stats: Statistics, U_N: float) -> dict:
    """
    vo5: bushy (custkey root)

    V_NCOL (root, @custkey)
    ├── V_NC (@nationkey)
    │   ├── N
    │   └── C
    └── V_OL (@orderkey, AGG -> custkey)
        ├── O^P
        └── L^P
    """
    b = stats.batch
    d = stats.deg
    dom = stats.dom['custkey_OL']

    # Path multipliers correspond to sibling fanouts:
    # Root joins V_NC delta with V_OL (fanout deg_V_OL_ckey) and vice versa.
    # V_NC joins N/C on nationkey; V_OL aggregates on custkey.

    # C path: C -> V_NC (join with N) -> root (join with V_OL)
    delta_C1 = b['U_C'] * d['N_nkey']            # join N fanout at V_NC
    delta_C2 = delta_C1 * d['V_OL_ckey']         # join with V_OL at root
    S_C = delta_C1 + delta_C2

    # N path: N -> V_NC (join with C) -> root (join with V_OL)
    delta_N1 = U_N * d['C_nkey']                 # join C fanout at V_NC
    delta_N2 = delta_N1 * d['V_OL_ckey']         # join with V_OL at root
    S_N = delta_N1 + delta_N2

    # O path: O -> V_OL (agg) -> root (join with V_NC)
    delta_join_O = b['U_O'] * d['L_okey']
    delta_agg_O = min(delta_join_O, dom)
    delta_O2 = (delta_join_O + delta_agg_O) * d['V_NC_ckey']  # join with V_NC at root
    S_O = delta_join_O + delta_agg_O + delta_O2

    # L path: L -> V_OL (agg) -> root (join with V_NC)
    delta_join_L = b['U_L'] * d['O_okey']
    delta_agg_L = min(delta_join_L, dom)
    delta_L2 = (delta_join_L + delta_agg_L) * d['V_NC_ckey']
    S_L = delta_join_L + delta_agg_L + delta_L2

    return {'S_N': S_N, 'S_C': S_C, 'S_O': S_O, 'S_L': S_L,
            'total': S_N + S_C + S_O + S_L}


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)


def print_stats(stats: Statistics, label: str):
    """Print statistics summary."""
    print(f"\n--- {label} ---")
    print(f"  Batch sizes: U_C={stats.batch['U_C']:.1f}, U_O={stats.batch['U_O']:.1f}, U_L={stats.batch['U_L']:.1f}")
    print(f"  Key degrees: deg_L_okey={stats.deg['L_okey']:.2f}, deg_O_okey={stats.deg['O_okey']:.3f}")
    print(f"  View degrees: deg_V_OL_ckey={stats.deg['V_OL_ckey']:.3f}, deg_V_COL_nkey={stats.deg['V_COL_nkey']:.1f}")
    print(f"  Domain: |Dom(custkey)|={stats.dom['custkey_OL']}, |Dom(orderkey)|={stats.dom['orderkey_OL']}")


def main():
    parser = argparse.ArgumentParser(description='Compute cost model for all variable orders')
    parser.add_argument('--db', default='tpch.duckdb', help='Path to DuckDB database')
    parser.add_argument('--batch', type=int, default=10000, help='Global batch size')
    parser.add_argument('--updates-db', default=None, help='Path to updates.duckdb to derive observed batch sizes')
    args = parser.parse_args()

    cfg = Config(db_path=args.db, batch_size=args.batch, updates_db=args.updates_db)

    print(f"TPC-H Q10 - All Variable Orders Cost Computation")
    print(f"Database: {cfg.db_path}")
    print(f"Batch size: {cfg.batch_size:,}")
    if cfg.updates_db:
        print(f"Using observed batch sizes from: {cfg.updates_db}")

    con = duckdb.connect(cfg.db_path, read_only=True)

    # Compute statistics for both cases
    print_section("Statistics")
    stats_wp = Statistics(con, cfg, with_predicates=True)
    stats_np = Statistics(con, cfg, with_predicates=False)

    print_stats(stats_wp, "With Predicates")
    print_stats(stats_np, "No Predicates")

    # Compute costs for all variable orders
    vo_funcs = [
        ('vo1', compute_vo1),
        ('vo2', compute_vo2),
        ('vo3', compute_vo3),
        ('vo4', compute_vo4),
        ('vo5', compute_vo5),
    ]

    results = {}

    for scenario, U_N in [('Static', 0), ('Dynamic', 1)]:
        print_section(f"Costs - {scenario} (U_N={U_N})")

        print(f"\n  {'VO':<6} {'With Pred':>12} {'No Pred':>12} {'Ratio':>8}")
        print(f"  {'-'*6} {'-'*12} {'-'*12} {'-'*8}")

        for vo_name, vo_func in vo_funcs:
            cost_wp = vo_func(stats_wp, U_N)
            cost_np = vo_func(stats_np, U_N)
            ratio = cost_np['total'] / cost_wp['total'] if cost_wp['total'] > 0 else float('inf')

            print(f"  {vo_name:<6} {cost_wp['total']:>12,.0f} {cost_np['total']:>12,.0f} {ratio:>7.1f}×")

            results[(vo_name, scenario)] = {'wp': cost_wp, 'np': cost_np}

    # Detailed breakdown
    print_section("Detailed Breakdown (With Predicates, Static)")
    for vo_name, vo_func in vo_funcs:
        cost = vo_func(stats_wp, 0)
        print(f"\n  {vo_name}: S_N={cost['S_N']:.0f}, S_C={cost['S_C']:.0f}, S_O={cost['S_O']:.0f}, S_L={cost['S_L']:.0f} -> Total={cost['total']:.0f}")

    print_section("Detailed Breakdown (No Predicates, Static)")
    for vo_name, vo_func in vo_funcs:
        cost = vo_func(stats_np, 0)
        print(f"\n  {vo_name}: S_N={cost['S_N']:.0f}, S_C={cost['S_C']:.0f}, S_O={cost['S_O']:.0f}, S_L={cost['S_L']:.0f} -> Total={cost['total']:.0f}")

    # Ranking
    print_section("Rankings (lower is better)")

    for scenario in ['Static', 'Dynamic']:
        for pred_label, pred_key in [('With Predicates', 'wp'), ('No Predicates', 'np')]:
            costs = [(vo_name, results[(vo_name, scenario)][pred_key]['total']) for vo_name, _ in vo_funcs]
            costs.sort(key=lambda x: x[1])
            ranking = ' < '.join([f"{name}({cost:.0f})" for name, cost in costs])
            print(f"\n  {scenario}, {pred_label}:")
            print(f"    {ranking}")

    con.close()
    print()


if __name__ == '__main__':
    main()
