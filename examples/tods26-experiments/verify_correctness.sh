#!/bin/bash
set -euo pipefail

# ============================================================================
# verify_correctness.sh
#
# Correctness verification for the FIVM experiment infrastructure (Q3, Q5, Q9).
# For each query and variant (full, count), builds and runs ALL variable orders
# under a single fast configuration (sf0p1, static, pred_on) and checks that
# all VOs produce identical final query results.
#
# Also performs cross-mode checks: for each query (full variant), confirms that
# static and dynamic modes produce the same result (using one VO).
#
# Usage:
#   cd FIVM/examples
#   ./tods26-experiments/verify_correctness.sh
#
# Environment:
#   BATCH_SIZE=10000  (default; override if needed)
#   VERBOSE=1         (set to see build/run output; default: quiet)
# ============================================================================

cd "$(dirname "$0")/.."

BATCH_SIZE="${BATCH_SIZE:-10000}"
VERBOSE="${VERBOSE:-0}"

CPP_DIR="generated/cpp/tods26_verify"
BIN_DIR="bin/tods26_verify"
TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/fivm_verify.XXXXXX")
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$CPP_DIR" "$BIN_DIR"

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
RESULTS=()

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log()  { echo "[verify] $*"; }
pass() { log "PASS: $*"; PASS_COUNT=$((PASS_COUNT + 1)); RESULTS+=("PASS: $*"); }
fail() { log "FAIL: $*"; FAIL_COUNT=$((FAIL_COUNT + 1)); RESULTS+=("FAIL: $*"); }
skip() { log "SKIP: $*"; SKIP_COUNT=$((SKIP_COUNT + 1)); RESULTS+=("SKIP: $*"); }

# ---------------------------------------------------------------------------
# filter_result <file>
#
# Strip FIVM framework metadata lines from stdout, leaving only the query
# result produced by data.serialize().  Known metadata patterns:
#   - "-------------"
#   - "Starting reading from data sources..."
#   - "  <name> (<N>) completed."
#   - "Data sources preloaded in ..."
#   - "1. On begin of processing..."  (and steps 2-5)
#   - "    Run: ..."
#   - lines that are just a timing suffix like "0.123 ms"
#   - blank lines
# ---------------------------------------------------------------------------
filter_result() {
  local file="$1"
  grep -v -E \
    -e '^-+$' \
    -e '^Starting reading from data sources' \
    -e '^[[:space:]]+[A-Z_]+ \([0-9]+\) completed\.' \
    -e '^Data sources preloaded in' \
    -e '^[0-9]+\. ' \
    -e '^[[:space:]]*Run:' \
    -e '^[[:space:]]*[0-9]+(\.[0-9]+)? ms$' \
    -e '^[[:space:]]*$' \
    -e '^Memory ' \
    -e '^[0-9]+ tuples processed at' \
    "$file" \
  | sed -E \
    -e 's/<\/?V_[a-zA-Z_]+[0-9]*>/<V>/g' \
    -e 's/[0-9]+ ms$//' \
  || true
}

# ---------------------------------------------------------------------------
# build_and_run <sql_file> <app_include> <bin_subdir> <output_file>
#
# Generate code, compile, and run the binary (without --no-output) to capture
# the query result.  Stdout goes to <output_file>; metadata is on stdout too
# but we filter it later.
# ---------------------------------------------------------------------------
build_and_run() {
  local sql_file="$1"
  local app_include="$2"
  local bin_subdir="$3"
  local output_file="$4"

  local base
  base=$(basename "$sql_file" .sql)
  local cpp_out="${CPP_DIR}/${base}.hpp"
  local bin_out="${bin_subdir}/${base}"

  if [[ ! -f "$sql_file" ]]; then
    log "  SQL file not found: $sql_file"
    return 1
  fi

  # Generate C++ from SQL
  if [[ "$VERBOSE" == "1" ]]; then
    ../scripts/generate-code.sh -l cpp -o "$cpp_out" "$sql_file"
  else
    ../scripts/generate-code.sh -l cpp -o "$cpp_out" "$sql_file" >/dev/null 2>&1
  fi

  # Build binary
  if [[ "$VERBOSE" == "1" ]]; then
    APP_INCLUDE="$app_include" \
    EXTRA_ARGS="-I include" \
    ../scripts/build-generated-cpp.sh "$cpp_out" "$bin_out"
  else
    APP_INCLUDE="$app_include" \
    EXTRA_ARGS="-I include" \
    ../scripts/build-generated-cpp.sh "$cpp_out" "$bin_out" >/dev/null 2>&1
  fi

  # Run binary (without --no-output so we get the query result on stdout)
  "$bin_out" --num_runs 1 --batch-size "$BATCH_SIZE" > "$output_file" 2>/dev/null

  return 0
}

# ---------------------------------------------------------------------------
# Query configuration table
# ---------------------------------------------------------------------------
# Format: query_num  query_dir_suffix  vo_prefix  app_include
#
# Full variants
declare -A FULL_QUERY_DIR FULL_VO_PREFIX FULL_APP_INCLUDE
FULL_QUERY_DIR[3]="tpch_query_3"
FULL_VO_PREFIX[3]="tpch_q3"
FULL_APP_INCLUDE[3]="include/application/tpch/application_tpch_query3.hpp"

FULL_QUERY_DIR[5]="tpch_query_5"
FULL_VO_PREFIX[5]="tpch_q5"
FULL_APP_INCLUDE[5]="include/application/tpch/application_tpch_query5.hpp"

FULL_QUERY_DIR[9]="tpch_query_9"
FULL_VO_PREFIX[9]="tpch_q9"
FULL_APP_INCLUDE[9]="include/application/tpch/application_tpch_query9.hpp"

# Count variants
declare -A COUNT_QUERY_DIR COUNT_VO_PREFIX COUNT_APP_INCLUDE
COUNT_QUERY_DIR[3]="tpch_query_3_count"
COUNT_VO_PREFIX[3]="tpch_q3cnt"
COUNT_APP_INCLUDE[3]="include/application/tpch/application_tpch_query3.hpp"

COUNT_QUERY_DIR[5]="tpch_query_5_count"
COUNT_VO_PREFIX[5]="tpch_q5cnt"
COUNT_APP_INCLUDE[5]="include/application/tpch/application_tpch_query5.hpp"

COUNT_QUERY_DIR[9]="tpch_query_9_count"
COUNT_VO_PREFIX[9]="tpch_q9cnt"
COUNT_APP_INCLUDE[9]="include/application/tpch/application_tpch_query9.hpp"

QUERIES=(3 5 9)
SCALE="sf0p1"
PRED="on"

# ============================================================================
# TEST 1: VO agreement (full variant)
#
# For each query, build and run all VOs with (sf0p1, static, pred_on).
# All VOs must produce identical results.
# ============================================================================
log ""
log "================================================================"
log "TEST 1: VO agreement -- full variant (sf0p1, static, pred_on)"
log "================================================================"

for q in "${QUERIES[@]}"; do
  query_dir="${FULL_QUERY_DIR[$q]}"
  vo_prefix="${FULL_VO_PREFIX[$q]}"
  app_include="${FULL_APP_INCLUDE[$q]}"
  sql_dir="tods26-experiments/queries/${query_dir}/sql_files"
  vo_dir="tods26-experiments/queries/${query_dir}/variable_orders"

  log ""
  log "--- Q${q} full ---"

  # Collect VOs
  vo_list=()
  while IFS= read -r f; do
    base=$(basename "$f" .txt)
    vo_list+=("$base")
  done < <(find "$vo_dir" -maxdepth 1 -type f -name "${vo_prefix}_*.txt" 2>/dev/null | sort)

  if [[ "${#vo_list[@]}" -eq 0 ]]; then
    skip "Q${q} full -- no VO files found in ${vo_dir}"
    continue
  fi

  log "  VOs (${#vo_list[@]}): ${vo_list[*]}"

  all_match=true
  reference_file=""

  for vo in "${vo_list[@]}"; do
    sql_file="${sql_dir}/${vo}_${SCALE}_static_pred_${PRED}.sql"
    raw_out="${TMP_DIR}/q${q}_full_${vo}_raw.txt"
    result_out="${TMP_DIR}/q${q}_full_${vo}_result.txt"

    log "  Building and running ${vo} ..."

    if ! build_and_run "$sql_file" "$app_include" "$BIN_DIR" "$raw_out"; then
      fail "Q${q} full -- build/run failed for ${vo}"
      all_match=false
      continue
    fi

    filter_result "$raw_out" > "$result_out"

    if [[ -z "$reference_file" ]]; then
      reference_file="$result_out"
      log "  Reference VO: ${vo} ($(wc -l < "$result_out") result lines)"
    else
      if diff -q "$reference_file" "$result_out" >/dev/null 2>&1; then
        log "  ${vo}: matches reference"
      else
        log "  ${vo}: MISMATCH with reference!"
        if [[ "$VERBOSE" == "1" ]]; then
          diff "$reference_file" "$result_out" || true
        fi
        all_match=false
      fi
    fi
  done

  if [[ "$all_match" == true && "${#vo_list[@]}" -ge 2 ]]; then
    pass "Q${q} full -- all ${#vo_list[@]} VOs agree"
  elif [[ "$all_match" == true && "${#vo_list[@]}" -eq 1 ]]; then
    pass "Q${q} full -- only 1 VO, trivially passes"
  elif [[ "$all_match" == false ]]; then
    fail "Q${q} full -- VO outputs disagree"
  fi
done

# ============================================================================
# TEST 2: VO agreement (count variant)
#
# For each query, build and run all VOs with (sf0p1, static, pred_on).
# All VOs must produce identical results.
# ============================================================================
log ""
log "================================================================"
log "TEST 2: VO agreement -- count variant (sf0p1, static, pred_on)"
log "================================================================"

for q in "${QUERIES[@]}"; do
  query_dir="${COUNT_QUERY_DIR[$q]}"
  vo_prefix="${COUNT_VO_PREFIX[$q]}"
  app_include="${COUNT_APP_INCLUDE[$q]}"
  sql_dir="tods26-experiments/queries/${query_dir}/sql_files"
  vo_dir="tods26-experiments/queries/${query_dir}/variable_orders"

  log ""
  log "--- Q${q} count ---"

  # Collect VOs
  vo_list=()
  while IFS= read -r f; do
    base=$(basename "$f" .txt)
    vo_list+=("$base")
  done < <(find "$vo_dir" -maxdepth 1 -type f -name "${vo_prefix}_*.txt" 2>/dev/null | sort)

  if [[ "${#vo_list[@]}" -eq 0 ]]; then
    skip "Q${q} count -- no VO files found in ${vo_dir}"
    continue
  fi

  log "  VOs (${#vo_list[@]}): ${vo_list[*]}"

  all_match=true
  reference_file=""

  for vo in "${vo_list[@]}"; do
    sql_file="${sql_dir}/${vo}_${SCALE}_static_pred_${PRED}.sql"
    raw_out="${TMP_DIR}/q${q}_count_${vo}_raw.txt"
    result_out="${TMP_DIR}/q${q}_count_${vo}_result.txt"

    log "  Building and running ${vo} ..."

    if ! build_and_run "$sql_file" "$app_include" "$BIN_DIR" "$raw_out"; then
      fail "Q${q} count -- build/run failed for ${vo}"
      all_match=false
      continue
    fi

    filter_result "$raw_out" > "$result_out"

    if [[ -z "$reference_file" ]]; then
      reference_file="$result_out"
      log "  Reference VO: ${vo} ($(wc -l < "$result_out") result lines)"
    else
      if diff -q "$reference_file" "$result_out" >/dev/null 2>&1; then
        log "  ${vo}: matches reference"
      else
        log "  ${vo}: MISMATCH with reference!"
        if [[ "$VERBOSE" == "1" ]]; then
          diff "$reference_file" "$result_out" || true
        fi
        all_match=false
      fi
    fi
  done

  if [[ "$all_match" == true && "${#vo_list[@]}" -ge 2 ]]; then
    pass "Q${q} count -- all ${#vo_list[@]} VOs agree"
  elif [[ "$all_match" == true && "${#vo_list[@]}" -eq 1 ]]; then
    pass "Q${q} count -- only 1 VO, trivially passes"
  elif [[ "$all_match" == false ]]; then
    fail "Q${q} count -- VO outputs disagree"
  fi
done

# ============================================================================
# TEST 3: Cross-mode check (static vs dynamic)
#
# For each query (full variant only), run one VO under both static and dynamic
# modes with (sf0p1, pred_on).  Results must agree.
# ============================================================================
log ""
log "================================================================"
log "TEST 3: Cross-mode check -- static vs dynamic (sf0p1, pred_on)"
log "================================================================"

for q in "${QUERIES[@]}"; do
  query_dir="${FULL_QUERY_DIR[$q]}"
  vo_prefix="${FULL_VO_PREFIX[$q]}"
  app_include="${FULL_APP_INCLUDE[$q]}"
  sql_dir="tods26-experiments/queries/${query_dir}/sql_files"
  vo_dir="tods26-experiments/queries/${query_dir}/variable_orders"

  log ""
  log "--- Q${q} full: static vs dynamic ---"

  # Pick the first VO
  first_vo=""
  while IFS= read -r f; do
    first_vo=$(basename "$f" .txt)
    break
  done < <(find "$vo_dir" -maxdepth 1 -type f -name "${vo_prefix}_*.txt" 2>/dev/null | sort)

  if [[ -z "$first_vo" ]]; then
    skip "Q${q} cross-mode -- no VO files found"
    continue
  fi

  log "  Using VO: ${first_vo}"

  # Static run
  sql_static="${sql_dir}/${first_vo}_${SCALE}_static_pred_${PRED}.sql"
  raw_static="${TMP_DIR}/q${q}_crossmode_static_raw.txt"
  result_static="${TMP_DIR}/q${q}_crossmode_static_result.txt"

  log "  Building and running static ..."
  if ! build_and_run "$sql_static" "$app_include" "$BIN_DIR" "$raw_static"; then
    fail "Q${q} cross-mode -- static build/run failed"
    continue
  fi
  filter_result "$raw_static" > "$result_static"

  # Dynamic run
  sql_dynamic="${sql_dir}/${first_vo}_${SCALE}_dynamic_pred_${PRED}.sql"
  raw_dynamic="${TMP_DIR}/q${q}_crossmode_dynamic_raw.txt"
  result_dynamic="${TMP_DIR}/q${q}_crossmode_dynamic_result.txt"

  log "  Building and running dynamic ..."
  if ! build_and_run "$sql_dynamic" "$app_include" "$BIN_DIR" "$raw_dynamic"; then
    fail "Q${q} cross-mode -- dynamic build/run failed"
    continue
  fi
  filter_result "$raw_dynamic" > "$result_dynamic"

  # Compare
  if diff -q "$result_static" "$result_dynamic" >/dev/null 2>&1; then
    pass "Q${q} cross-mode -- static and dynamic agree"
  else
    fail "Q${q} cross-mode -- static and dynamic DISAGREE"
    if [[ "$VERBOSE" == "1" ]]; then
      diff "$result_static" "$result_dynamic" || true
    fi
  fi
done

# ============================================================================
# Summary
# ============================================================================
log ""
log "================================================================"
log "SUMMARY"
log "================================================================"

for r in "${RESULTS[@]}"; do
  log "  $r"
done

log ""
log "Passed: ${PASS_COUNT}   Failed: ${FAIL_COUNT}   Skipped: ${SKIP_COUNT}"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  log ""
  log "VERIFICATION FAILED -- see failures above."
  exit 1
else
  log ""
  log "ALL CHECKS PASSED."
  exit 0
fi
