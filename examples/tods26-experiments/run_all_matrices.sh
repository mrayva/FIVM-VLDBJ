#!/bin/bash
set -euo pipefail

# ============================================================================
# run_all_matrices.sh
#
# Runs all experiment matrices sequentially (Q3, Q5, Q9 — full + count).
# Designed to be run overnight unattended.
#
# Usage:
#   cd FIVM/examples
#   nohup ./tods26-experiments/run_all_matrices.sh > tods26-experiments/output/run_all.log 2>&1 &
#
# Progress is logged to stdout. Each sub-script also writes per-combination
# CSV logs to tods26-experiments/output/.
# ============================================================================

cd "$(dirname "$0")/.."

export RUN_TIMEOUT="${RUN_TIMEOUT:-600}"  # 10 min default per combination

echo "============================================================"
echo "Starting full experiment matrix run"
echo "Date: $(date)"
echo "Host: $(hostname)"
echo "============================================================"
echo ""

SCRIPTS=(
  "tods26-experiments/run_q3_matrix.sh"
  "tods26-experiments/run_q3_count_matrix.sh"
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
    echo "[PASS] $script completed successfully at $(date)"
    PASSED=$((PASSED + 1))
  else
    echo ""
    echo "[FAIL] $script failed at $(date)"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "============================================================"
echo "ALL MATRICES COMPLETE"
echo "Date: $(date)"
echo "Passed: $PASSED / $TOTAL    Failed: $FAILED / $TOTAL"
echo "============================================================"

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
