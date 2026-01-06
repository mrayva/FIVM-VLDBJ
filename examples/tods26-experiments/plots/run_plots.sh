#!/bin/bash
set -euo pipefail

# Generate throughput plots for all scenarios from the logs in ../output.
# Uses generate_throughput_plots.py to produce one PNG per (scale, mode, pred).

cd "$(dirname "$0")"

python generate_tail_throughput_plots.py \
    --input-dir ../output \
    --output-dir . \
    --dpi 300 \
    --smooth-window 20 \
    --drop-first-tail \
    --per-source


echo "Done."
