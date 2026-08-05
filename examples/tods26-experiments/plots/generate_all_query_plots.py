#!/usr/bin/env python3
"""Generate throughput plots for Q3, Q5, Q9, Q10 — one set per query."""

import csv
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_BASE = Path(__file__).parent
INPUT_DIR = Path(__file__).parent.parent / "output"

QUERIES = ["q3", "q5", "q9", "q10"]


def load_series(path):
    """Load CSV and return list of (pct, throughput_rows_per_sec) per round."""
    rows = []
    with path.open() as f:
        for row in csv.DictReader(f):
            rows.append(row)
    if not rows:
        return []

    # Source cycle
    src_order = []
    seen = set()
    for r in rows:
        s = r["source"]
        if s not in seen:
            src_order.append(s)
            seen.add(s)
    if not src_order:
        return []

    cycle = len(src_order)
    rounds = [rows[i:i+cycle] for i in range(0, len(rows), cycle) if len(rows[i:i+cycle]) == cycle]

    total_rows = sum(int(r["rows"]) for r in rows)
    if total_rows == 0:
        return []

    cum = 0
    points = []
    for rnd in rounds:
        rr = sum(int(r["rows"]) for r in rnd)
        ms = sum(float(r["duration_ms"]) for r in rnd)
        cum += rr
        pct = cum / total_rows * 100
        thr = rr / (ms / 1000) if ms > 0 else 0
        points.append((pct, thr))
    return points


def main():
    for query in QUERIES:
        out_dir = OUTPUT_BASE / query
        out_dir.mkdir(parents=True, exist_ok=True)

        # Find all CSV files for this query
        pattern = re.compile(
            rf"tpch_{query}_(vo\d+)_(.+)_sf(0p1|1)_(static|dynamic)_pred_(on|off)\.csv$"
        )

        groups = defaultdict(dict)  # (scale, mode, pred) -> {vo_label: path}
        for f in sorted(INPUT_DIR.glob(f"tpch_{query}_*.csv")):
            m = pattern.match(f.name)
            if not m:
                continue
            vo, vo_name, scale, mode, pred = m.groups()
            key = (f"sf{scale}", mode, pred)
            label = f"{vo}"
            groups[key][label] = f

        if not groups:
            print(f"No data for {query}")
            continue

        for (scale, mode, pred), vo_paths in sorted(groups.items()):
            fig, ax = plt.subplots(figsize=(12, 6))

            for vo_label, path in sorted(vo_paths.items()):
                series = load_series(path)
                if not series:
                    continue
                x = [p[0] for p in series]
                y = [p[1] / 1e6 for p in series]  # Convert to M rows/s
                ax.plot(x, y, label=vo_label, linewidth=1.2)

            ax.set_xlabel("Percent processed (%)")
            ax.set_ylabel("Throughput (M rows/s)")
            ax.set_title(f"{query.upper()} — {scale}, {mode}, predicates {pred}")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(bottom=0)

            fname = f"throughput_{scale}_{mode}_pred_{pred}.png"
            fig.savefig(out_dir / fname, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"  {query}/{fname}")

    print("Done.")


if __name__ == "__main__":
    main()
