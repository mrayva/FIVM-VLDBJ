#!/bin/bash
set -euo pipefail

# Run remaining experiment matrices (Q3 already done).
# Uses 10-minute timeout per combination.
#
# Usage:
#   cd FIVM/examples
#   nohup ./tods26-experiments/run_remaining_matrices.sh > tods26-experiments/output/run_remaining.log 2>&1 &

cd "$(dirname "$0")/.."

export RUN_TIMEOUT=600  # 10 minutes

echo "============================================================"
echo "Running remaining matrices (10-min timeout per combo)"
echo "Date: $(date)"
echo "============================================================"

SCRIPTS=(
  "tods26-experiments/run_q5_matrix.sh"
  "tods26-experiments/run_q5_count_matrix.sh"
  "tods26-experiments/run_q9_matrix.sh"
  "tods26-experiments/run_q9_count_matrix.sh"
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
    echo ""
    echo "[PASS] $script completed at $(date)"
    PASSED=$((PASSED + 1))
  else
    echo ""
    echo "[FAIL] $script failed at $(date)"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "============================================================"
echo "REMAINING MATRICES COMPLETE"
echo "Date: $(date)"
echo "Passed: $PASSED / $TOTAL    Failed: $FAILED / $TOTAL"
echo "============================================================"
