#!/usr/bin/env python3
"""
Generate throughput plots split into head/tail panels.
Rounds are inferred by cycling through sources in the order they first appear;
batch_id is ignored.
The head/tail split defaults to the first round where every source has seen
both inserts and deletes (i.e., all tables in full mode). If that cannot be
detected, a --cutoff percent is used.
Outputs one plot per scenario (scale, mode, pred) with lines for all VOs.
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
    m = re.match(r"(.+)_sf(0p1|1)_(static|dynamic)_pred_(on|off)$", path.stem)
    if not m:
        return None
    vo = m.group(1)
    scale = f"sf{m.group(2)}"
    mode = m.group(3)
    pred_flag = m.group(4)
    return vo, scale, mode, pred_flag


def load_round_series(path: Path) -> Tuple[List[SeriesPoint], float, List[str], List[List[dict]]]:
    rows: List[dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    if not rows:
        return [], None, [], []

    # infer source order
    order = []
    seen = set()
    for r in rows:
        src = r["source"]
        if src not in seen:
            order.append(src)
            seen.add(src)
    if not order:
        return []
    round_size = len(order)

    # group into rounds
    rounds: List[List[dict]] = []
    cur = []
    pos = 0
    for r in rows:
        cur.append(r)
        pos += 1
        if pos == round_size:
            rounds.append(cur)
            cur = []
            pos = 0
    if cur:
        rounds.append(cur)

    total_rows = sum(int(r["rows"]) for r in rows)
    if total_rows == 0:
        return [], None, order, rounds

    cum_rows = 0
    points: List[SeriesPoint] = []
    # track when all sources have seen both inserts and deletes
    seen_ins = {src: False for src in order}
    seen_del = {src: False for src in order}
    full_phase_pct = None

    for rnd in rounds:
        round_rows = sum(int(r["rows"]) for r in rnd)
        round_ms = sum(float(r["duration_ms"]) for r in rnd)
        for r in rnd:
            src = r["source"]
            ins = int(r.get("inserts", 0))
            dels = int(r.get("deletes", 0))
            if ins > 0:
                seen_ins[src] = True
            if dels > 0:
                seen_del[src] = True
        if full_phase_pct is None and all(seen_ins.values()) and all(seen_del.values()):
            full_phase_pct = (cum_rows + round_rows) / total_rows * 100.0

        cum_rows += round_rows
        pct = (cum_rows / total_rows) * 100.0
        throughput = round_rows / (round_ms / 1000.0) if round_ms > 0 else math.nan
        points.append(SeriesPoint(pct=pct, throughput=throughput / 1000.0))

    return points, full_phase_pct, order, rounds


def smooth_series(points: List[SeriesPoint], window: int) -> List[SeriesPoint]:
    """Apply a simple trailing moving average over throughput."""
    if window <= 1:
        return points
    smoothed: List[SeriesPoint] = []
    buf: List[float] = []
    for p in points:
        buf.append(p.throughput)
        if len(buf) > window:
            buf.pop(0)
        smoothed.append(SeriesPoint(pct=p.pct, throughput=sum(buf) / len(buf)))
    return smoothed


def build_per_source_series(order: List[str], rounds: List[List[dict]]) -> Dict[str, List[SeriesPoint]]:
    """Compute per-source throughput series; pct is relative to that source's total rows."""
    totals: Dict[str, int] = {src: 0 for src in order}
    for rnd in rounds:
        for r in rnd:
            src = r["source"]
            totals[src] += int(r["rows"])
    series: Dict[str, List[SeriesPoint]] = {src: [] for src in order}
    running: Dict[str, int] = {src: 0 for src in order}
    for rnd in rounds:
        for r in rnd:
            src = r["source"]
            rows = int(r["rows"])
            ms = float(r["duration_ms"])
            running[src] += rows
            pct = (running[src] / totals[src] * 100.0) if totals[src] > 0 else 0.0
            throughput = rows / (ms / 1000.0) / 1000.0 if ms > 0 else math.nan
            series[src].append(SeriesPoint(pct=pct, throughput=throughput))
    return series


def group_logs(input_dir: Path):
    groups: Dict[tuple, Dict[str, Path]] = defaultdict(dict)
    for path in sorted(input_dir.glob("*.csv")):
        meta = parse_filename(path)
        if not meta:
            continue
        vo, scale, mode, pred_flag = meta
        groups[(scale, mode, pred_flag)][vo] = path
    return groups


def plot_head_tail(scale: str, mode: str, pred: str, vo_paths: Dict[str, Path], output_dir: Path, dpi: int, cutoff_pct: float, smooth_window: int, drop_first_tail: bool, per_source: bool):
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    series_by_vo: Dict[str, List[SeriesPoint]] = {}
    detected_cutoff = None
    per_source_series: Dict[str, Dict[str, List[SeriesPoint]]] = {}

    for vo, path in vo_paths.items():
        points, full_pct, order, rounds = load_round_series(path)
        if not points:
            continue
        series_by_vo[vo] = smooth_series(points, smooth_window)
        if per_source:
            src_series = build_per_source_series(order, rounds)
            per_source_series[vo] = {src: smooth_series(s, smooth_window) for src, s in src_series.items()}
        if full_pct is not None:
            detected_cutoff = full_pct if detected_cutoff is None else min(detected_cutoff, full_pct)

    if not series_by_vo:
        print(f"No valid data for {scale} {mode} pred {pred}")
        plt.close(fig)
        return

    min_tail_pct = detected_cutoff if detected_cutoff is not None else cutoff_pct

    drop_n = max(1, smooth_window) if drop_first_tail else 0

    for vo, series in series_by_vo.items():
        head = [p for p in series if p.pct < min_tail_pct]
        tail = [p for p in series if p.pct >= min_tail_pct]
        if drop_n > 0 and len(tail) > 0:
            tail = tail[drop_n:]
        if head:
            axes[0].plot([p.pct for p in head], [p.throughput for p in head], label=vo)
        if tail:
            axes[1].plot([p.pct for p in tail], [p.throughput for p in tail], label=vo)

    axes[0].set_ylabel(f"Throughput (tuples/ms)\nHead (0-{min_tail_pct:.1f}%)")
    axes[0].grid(True, alpha=0.3)
    axes[1].set_xlabel("Percent processed (%)")
    axes[1].set_ylabel(f"Throughput (tuples/ms)\nTail ({min_tail_pct:.1f}-100%)")
    axes[1].grid(True, alpha=0.3)
    axes[0].legend()
    cutoff_note = f"detected cutoff {min_tail_pct:.1f}%" if detected_cutoff is not None else f"cutoff {cutoff_pct:.1f}%"
    smooth_note = f", smooth window {smooth_window}" if smooth_window > 1 else ""
    outlier_note = ", drop first tail point" if drop_first_tail else ""
    fig.suptitle(f"Q10 Throughput — {scale}, {mode}, predicates {pred} ({cutoff_note}{smooth_note}{outlier_note})")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"throughput_head_tail_{scale}_{mode}_pred_{pred}.png"
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote plot: {out_path}")

    if per_source:
        # One figure per source with all VOs
        sources = sorted({src for vo_map in per_source_series.values() for src in vo_map.keys()})
        for src in sources:
            fig2, axes2 = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
            for vo, vo_map in per_source_series.items():
                series = vo_map.get(src, [])
                if not series:
                    continue
                head = [p for p in series if p.pct < min_tail_pct]
                tail = [p for p in series if p.pct >= min_tail_pct]
                if drop_n > 0 and len(tail) > 0:
                    tail = tail[drop_n:]
                if head:
                    axes2[0].plot([p.pct for p in head], [p.throughput for p in head], label=vo)
                if tail:
                    axes2[1].plot([p.pct for p in tail], [p.throughput for p in tail], label=vo)
            axes2[0].set_ylabel(f"{src} throughput (tuples/ms)\nHead (0-{min_tail_pct:.1f}%)")
            axes2[0].grid(True, alpha=0.3)
            axes2[1].set_xlabel(f"{src} percent processed (%)")
            axes2[1].set_ylabel(f"{src} throughput (tuples/ms)\nTail ({min_tail_pct:.1f}-100%)")
            axes2[1].grid(True, alpha=0.3)
            axes2[0].legend()
            fig2.suptitle(f"{src} — {scale}, {mode}, predicates {pred} ({cutoff_note}{smooth_note}{outlier_note})")
            out_path2 = output_dir / f"throughput_head_tail_{scale}_{mode}_pred_{pred}_{src.lower()}.png"
            fig2.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig2.savefig(out_path2, dpi=dpi, bbox_inches="tight")
            plt.close(fig2)
            print(f"Wrote plot: {out_path2}")


def main():
    parser = argparse.ArgumentParser(description="Generate tail throughput plots (last fraction).")
    parser.add_argument("--input-dir", default="../output", help="Directory containing CSV logs")
    parser.add_argument("--output-dir", default=".", help="Directory to write plots")
    parser.add_argument("--dpi", type=int, default=120, help="Output DPI")
    parser.add_argument("--cutoff", type=float, default=75.0, help="Cutoff percent for head/tail split (default 75)")
    parser.add_argument("--smooth-window", type=int, default=1, help="Trailing moving-average window over throughput (in rounds)")
    parser.add_argument("--drop-first-tail", action="store_true", help="Drop the first point after the cutoff to reduce outlier impact")
    parser.add_argument("--per-source", action="store_true", help="Also emit per-source throughput plots")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    groups = group_logs(input_dir)
    if not groups:
        print(f"No logs found in {input_dir}")
        return

    for (scale, mode, pred), vo_paths in groups.items():
        plot_head_tail(
            scale,
            mode,
            pred,
            vo_paths,
            output_dir,
            args.dpi,
            args.cutoff,
            args.smooth_window,
            args.drop_first_tail,
            args.per_source,
        )


if __name__ == "__main__":
    main()
