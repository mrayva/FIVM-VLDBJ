#!/bin/bash
set -euo pipefail

# Generate per-log round plots for all CSV logs in ../output.

cd "$(dirname "$0")"

INPUT_DIR="${INPUT_DIR:-../output}"
OUTPUT_DIR="${OUTPUT_DIR:-.}"
DPI="${DPI:-120}"

mkdir -p "$OUTPUT_DIR"

for log in "$INPUT_DIR"/*.csv; do
  [ -e "$log" ] || continue
  base=$(basename "$log" .csv)
  out="$OUTPUT_DIR/${base}.rounds.png"
  echo "Plotting $log -> $out"
  python generate_round_plots.py "$log" --output "$out" --dpi "$DPI"
done

echo "Done."
