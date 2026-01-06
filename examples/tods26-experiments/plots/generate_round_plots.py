#!/usr/bin/env python3
"""
Generate per-source round-duration and throughput plots from a single log file.

Log format: source,batch_id,rows,inserts,deletes,duration_ms

Grouping into rounds:
- Infer source order by first occurrence.
- A round is a consecutive block covering each source once in that order
  (batch_id is ignored).

Outputs a PNG with 5 panels:
  - 4 panels: duration_ms per round for each source.
  - 1 panel: throughput (rows/ms) per round, one line per source.
"""
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Tuple

import matplotlib.pyplot as plt


def load_rows(path: Path) -> List[Dict[str, str]]:
    with path.open() as f:
        reader = csv.DictReader(f)
        return list(reader)


def split_rounds(rows: List[Dict[str, str]]) -> Tuple[List[str], List[List[Dict[str, str]]]]:
    # infer source order by first occurrence
    order = []
    seen = set()
    for r in rows:
        src = r["source"]
        if src not in seen:
            order.append(src)
            seen.add(src)
    if not order:
        return [], []
    round_size = len(order)
    rounds = []
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
    return order, rounds


def compute_per_round(order: List[str], rounds: List[List[Dict[str, str]]]):
    durations = {src: [] for src in order}
    throughput = {src: [] for src in order}
    for rnd in rounds:
        for src in order:
            # find entry for this src in round
            entry = next((r for r in rnd if r["source"] == src), None)
            if entry is None:
                durations[src].append(float("nan"))
                throughput[src].append(float("nan"))
            else:
                dur = float(entry["duration_ms"])
                rows = int(entry["rows"])
                durations[src].append(dur)
                throughput[src].append(rows / dur if dur > 0 else float("nan"))
    return durations, throughput


def plot_rounds(order: List[str], durations, throughput, out_path: Path, title: str, dpi: int):
    fig, axes = plt.subplots(5, 1, figsize=(10, 14), sharex=True)
    for i, src in enumerate(order):
        axes[i].plot(durations[src], marker="o")
        axes[i].set_ylabel(f"{src}\nms")
        axes[i].grid(alpha=0.3)
    # throughput panel
    ax = axes[4]
    for src in order:
        ax.plot(throughput[src], label=src, marker="o")
    ax.set_ylabel("rows/ms")
    ax.set_xlabel("Round index")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.suptitle(title)
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Generate round-based plots from a single log.")
    parser.add_argument("logfile", help="CSV log file path")
    parser.add_argument("--output", help="PNG output path", default=None)
    parser.add_argument("--dpi", type=int, default=120)
    args = parser.parse_args()

    log_path = Path(args.logfile).resolve()
    rows = load_rows(log_path)
    order, rounds = split_rounds(rows)
    if not order or not rounds:
        print("No data to plot.")
        return
    durations, throughput = compute_per_round(order, rounds)
    title = f"{log_path.name}"
    out = Path(args.output) if args.output else log_path.with_suffix(".rounds.png")
    plot_rounds(order, durations, throughput, out, title, args.dpi)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
