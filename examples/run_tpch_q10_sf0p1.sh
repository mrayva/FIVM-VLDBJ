#!/bin/bash
set -euo pipefail

# Run Q10 on SF=0.1, b=10000 datasets (static and dynamic) with predefined batches.
# Suppresses result printing via --no-output; reports wall time for each run.

cd "$(dirname "$0")"

STATIC_BIN="./bin/tpch/tpch_query10_predefined_sf0p1_static"
DYNAMIC_BIN="./bin/tpch/tpch_query10_predefined_sf0p1_dynamic"
BATCH_SIZE=10000

if [[ ! -x "$STATIC_BIN" || ! -x "$DYNAMIC_BIN" ]]; then
  echo "Error: Q10 binaries not found. Build them first."
  exit 1
fi

echo "Running Q10 SF=0.1 static..."
"$STATIC_BIN" --num_runs 1 --batch_size "$BATCH_SIZE" --no-output

echo ""
echo "Running Q10 SF=0.1 dynamic..."
"$DYNAMIC_BIN" --num_runs 1 --batch_size "$BATCH_SIZE" --no-output

echo ""
echo "Done."
