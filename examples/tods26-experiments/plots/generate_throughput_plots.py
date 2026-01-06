#!/usr/bin/env python3
"""
Generate throughput plots from experiment logs.

Expected log format (CSV): rows,inserts,deletes,duration_ms
Filename pattern: <vo>_<scale>_<mode>_pred_<on|off>.csv
  e.g., tpch_q10_order_cust_nation_sf0p1_static_pred_on.csv

Usage:
  python generate_throughput_plots.py \
      --input-dir ../output \
      --output-dir . \
      --dpi 120
"""
import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import re

import matplotlib.pyplot as plt


@dataclass
class SeriesPoint:
    pct: float
    throughput: float


def parse_filename(path: Path):
    """
    Extract vo, scale, mode, pred flag from filename.
    Expected: <vo>_sf<0p1|1>_<static|dynamic>_pred_<on|off>.csv
    """
    stem = path.stem
    m = re.match(r"(.+)_sf(0p1|1)_(static|dynamic)_pred_(on|off)$", stem)
    if not m:
        return None
    vo = m.group(1)
    scale = f"sf{m.group(2)}"
    mode = m.group(3)
    pred_flag = m.group(4)
    return vo, scale, mode, pred_flag


def load_series(path: Path) -> List[SeriesPoint]:
    rows: List[dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    if not rows:
        return []

    # Group by round: assume fixed cycle order among sources seen in the log
    # Build rounds by fixed cycle over sources (ignore batch_id).
    # Determine distinct source order by first occurrence.
    src_order: List[str] = []
    seen = set()
    for r in rows:
        src = r["source"]
        if src not in seen:
            src_order.append(src)
            seen.add(src)

    if not src_order:
        return []

    round_size = len(src_order)
    rounds: List[List[dict]] = []
    current: List[dict] = []
    pos = 0
    for r in rows:
        current.append(r)
        pos += 1
        if pos == round_size:
            rounds.append(current)
            current = []
            pos = 0
    if current:
        rounds.append(current)

    total_rows = sum(int(r["rows"]) for r in rows)
    if total_rows == 0:
        return []

    # cumulative percent processed based on total_rows
    total_rows = sum(int(r["rows"]) for r in rows)
    cum_rows = 0
    points: List[SeriesPoint] = []

    for rnd in rounds:
        round_rows = sum(int(r["rows"]) for r in rnd)
        round_ms = sum(float(r["duration_ms"]) for r in rnd)
        cum_rows += round_rows
        pct = (cum_rows / total_rows) * 100.0
        throughput = round_rows / (round_ms / 1000.0) if round_ms > 0 else math.nan
        points.append(SeriesPoint(pct=pct, throughput=throughput / 1000.0))

    return points


def group_logs(input_dir: Path):
    groups: Dict[tuple, Dict[str, Path]] = defaultdict(dict)
    for path in sorted(input_dir.glob("*.csv")):
        meta = parse_filename(path)
        if not meta:
            continue
        vo, scale, mode, pred_flag = meta
        groups[(scale, mode, pred_flag)][vo] = path
    return groups


def plot_group(scale: str, mode: str, pred: str, vo_paths: Dict[str, Path], output_dir: Path, dpi: int):
    plt.figure(figsize=(10, 6))
    for vo, path in vo_paths.items():
        series = load_series(path)
        if not series:
            continue
        x = [p.pct for p in series]
        y = [p.throughput for p in series]
        plt.plot(x, y, label=vo)

    plt.xlabel("Percent processed (%)")
    plt.ylabel("Throughput (tuples/sec)")
    plt.title(f"Q10 Throughput — {scale}, {mode}, predicates {pred}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"throughput_{scale}_{mode}_pred_{pred}.png"
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Wrote plot: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate throughput plots from logs.")
    parser.add_argument("--input-dir", default="../output", help="Directory containing CSV logs")
    parser.add_argument("--output-dir", default=".", help="Directory to write plots")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    groups = group_logs(input_dir)
    if not groups:
        print(f"No logs found in {input_dir}")
        return

    for (scale, mode, pred), vo_paths in groups.items():
        plot_group(scale, mode, pred, vo_paths, output_dir, args.dpi)


if __name__ == "__main__":
    main()
