#!/bin/bash

# Script to plot results for tpch_query03
# Usage: ./plot_q3.sh

WORK_DIR="/home/user/zhang/FIVM-static-dynamic/examples/static-experiments"

cd $WORK_DIR

QUERY="tpch_query03"
INPUT_DIR="output/static"
OUTPUT_DIR="plots"
CSV_FILE="${QUERY}_results.csv"

# Run the plotting script
python3 plot_results.py \
    --query $QUERY \
    --input-dir $INPUT_DIR \
    --output-dir $OUTPUT_DIR \
    --csv $CSV_FILE

echo ""
echo "Results aggregated to: $CSV_FILE"
echo "Plots saved to: $OUTPUT_DIR/"

