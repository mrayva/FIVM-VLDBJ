#!/bin/bash
set -euo pipefail

# Run remaining full-query matrices overnight (Q5 full + Q9 full).
# Q3 done, all count queries done. 10-min timeout per combination.
#
# Usage:
#   cd FIVM/examples
#   nohup ./tods26-experiments/run_full_overnight.sh > tods26-experiments/output/run_full_overnight.log 2>&1 &

cd "$(dirname "$0")/.."

export RUN_TIMEOUT=600

echo "============================================================"
echo "Full-query matrices (Q5 + Q9), 10-min timeout"
echo "Date: $(date)"
echo "============================================================"

SCRIPTS=(
  "tods26-experiments/run_q5_matrix.sh"
  "tods26-experiments/run_q9_matrix.sh"
)

TOTAL=${#SCRIPTS[@]}
PASSED=0
FAILED=0

for i in "${!SCRIPTS[@]}"; do
  script="${SCRIPTS[$i]}"
  idx=$((i + 1))
  echo ""
  echo "============================================================"
  echo "[$idx/$TOTAL] Running: $script"
  echo "Started: $(date)"
  echo "============================================================"
  echo ""
  if bash "$script"; then
    echo "[PASS] $script completed at $(date)"
    PASSED=$((PASSED + 1))
  else
    echo "[FAIL] $script failed at $(date)"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "============================================================"
echo "DONE — Passed: $PASSED / $TOTAL  Failed: $FAILED / $TOTAL"
echo "Date: $(date)"
echo "============================================================"
