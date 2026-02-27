#!/bin/bash
set -euo pipefail

# Count queries first (fast), then full queries.
# Q3 already done. 10-min timeout per combination.

cd "$(dirname "$0")/.."

export RUN_TIMEOUT=600

echo "============================================================"
echo "Remaining matrices: counts first, then full"
echo "Date: $(date)"
echo "============================================================"

SCRIPTS=(
  "tods26-experiments/run_q5_count_matrix.sh"
  "tods26-experiments/run_q9_count_matrix.sh"
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
