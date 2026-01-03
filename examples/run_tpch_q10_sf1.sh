#!/bin/bash
set -euo pipefail

# Run Q10 on SF=1, b=10000 datasets (static and dynamic) with predefined batches.
# Uses --no-output to suppress result printing and captures wall time via /usr/bin/time.

cd "$(dirname "$0")"

STATIC_BIN="./bin/tpch/tpch_query10_predefined_sf1_static"
DYNAMIC_BIN="./bin/tpch/tpch_query10_predefined_sf1_dynamic"
BATCH_SIZE=10000

if [[ ! -x "$STATIC_BIN" || ! -x "$DYNAMIC_BIN" ]]; then
  echo "Error: Q10 binaries not found. Build them first."
  exit 1
fi

echo "Running Q10 SF=1 static..."
/usr/bin/time -f "Elapsed (static): %E" "$STATIC_BIN" --num_runs 1 --batch-size "$BATCH_SIZE" --no-output

echo ""
echo "Running Q10 SF=1 dynamic..."
/usr/bin/time -f "Elapsed (dynamic): %E" "$DYNAMIC_BIN" --num_runs 1 --batch-size "$BATCH_SIZE" --no-output

echo ""
echo "Done."
