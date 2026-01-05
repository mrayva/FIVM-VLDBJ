#!/bin/bash
set -euo pipefail

# End-to-end driver for TPCH Q10 experiments (predicate on/off × static/dynamic × sf0.1/sf1 × VO).
# Builds generated C++ and binaries, then runs with logging enabled.
#
# Outputs:
#   - Logs written to tods26-experiments/output/<scale>_<mode>_<pred>.csv
#   - Binaries in bin/tods26/
#   - Generated C++ in generated/cpp/tods26/
#
# Usage:
#   ./run_q10_matrix.sh              # run all combos
#   BATCH_SIZE=5000 ./run_q10_matrix.sh   # override batch size

cd "$(dirname "$0")/.."

BATCH_SIZE="${BATCH_SIZE:-10000}"
TEST_MODE="${TEST_MODE:-0}" # 1 = run only the first combo (sanity check)
TIME_CMD="${TIME_CMD:-$(command -v time || true)}"

SCALES=("sf0p1" "sf1")
MODES=("static" "dynamic")
PREDS=("on" "off")
VO_LIST=()

SQL_DIR="tods26-experiments/queries/tpch_query_10/sql_files"
CPP_DIR="generated/cpp/tods26"
BIN_DIR="bin/tods26"
OUT_DIR="tods26-experiments/output"

# Collect available VOs
while IFS= read -r f; do
  base=$(basename "$f")
  base=${base%.txt}
  VO_LIST+=("$base")
done < <(find tods26-experiments/queries/tpch_query_10/variable_orders -maxdepth 1 -type f -name "tpch_q10_*.txt" | sort)

if [[ "${#VO_LIST[@]}" -eq 0 ]]; then
  echo "No VO files found in variable_orders/. Please run generate_assets.py first."
  exit 1
fi

mkdir -p "$CPP_DIR" "$BIN_DIR" "$OUT_DIR"

build_and_run() {
  local scale="$1" mode="$2" pred="$3"
  local vo_name="$4"

  local sql_file
  if [[ "$pred" == "on" ]]; then
    sql_file="${SQL_DIR}/${vo_name}_${scale}_${mode}_pred_on.sql"
  else
    sql_file="${SQL_DIR}/${vo_name}_${scale}_${mode}_pred_off.sql"
  fi

  local cpp_out="${CPP_DIR}/${vo_name}_${scale}_${mode}_pred_${pred}.hpp"
  local bin_out="${BIN_DIR}/${vo_name}_${scale}_${mode}_pred_${pred}"
  local log_out="${OUT_DIR}/${vo_name}_${scale}_${mode}_pred_${pred}.csv"

  echo "=== ${vo_name} ${scale} ${mode} pred:${pred} ==="
  echo "SQL: ${sql_file}"

  ../scripts/generate-code.sh -l cpp -o "$cpp_out" "$sql_file"

  APP_INCLUDE=include/application/tpch/application_tpch_query10.hpp \
  EXTRA_ARGS="-I include" \
  ../scripts/build-generated-cpp.sh "$cpp_out" "$bin_out"

  mkdir -p "$(dirname "$log_out")"
  rm -f "$log_out"

  if [[ -n "$TIME_CMD" && -x "$TIME_CMD" ]]; then
    FIVM_BATCH_LOG="$log_out" \
      "$TIME_CMD" -f "Elapsed: %E" \
      "$bin_out" --num_runs 1 --batch-size "$BATCH_SIZE" --no-output
  else
    FIVM_BATCH_LOG="$log_out" \
      "$bin_out" --num_runs 1 --batch-size "$BATCH_SIZE" --no-output
  fi

  echo "Log written to $log_out"
  echo ""
}

echo "Running with:"
echo "  VOs (${#VO_LIST[@]}): ${VO_LIST[*]}"
echo "  Scales (${#SCALES[@]}): ${SCALES[*]}"
echo "  Modes (${#MODES[@]}): ${MODES[*]}"
echo "  Predicates (${#PREDS[@]}): ${PREDS[*]}"
echo "  Batch size: ${BATCH_SIZE}"
echo "  Test mode: ${TEST_MODE}"
echo "#Combinations: ${#VO_LIST[@]} * ${#SCALES[@]} * ${#MODES[@]} * ${#PREDS[@]} = $((${#VO_LIST[@]} * ${#SCALES[@]} * ${#MODES[@]} * ${#PREDS[@]}))"
echo ""

count=0
for vo in "${VO_LIST[@]}"; do
  for scale in "${SCALES[@]}"; do
    for mode in "${MODES[@]}"; do
      for pred in "${PREDS[@]}"; do
        build_and_run "$scale" "$mode" "$pred" "$vo"
        count=$((count + 1))
        if [[ "$TEST_MODE" == "1" ]]; then
          echo "Test mode enabled; stopping after first combination."
          echo "Ran 1 combination."
          exit 0
        fi
      done
    done
  done
done

echo "All runs completed. Total combinations run: $count"
