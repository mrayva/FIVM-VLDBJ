#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${OUT_DIR:-/tmp/fivm-smoke-housing}"
GENERATED_HPP="${OUT_DIR}/housing_regression.hpp"
APP_BIN="${OUT_DIR}/housing_regression_app"

mkdir -p "${OUT_DIR}"

"${ROOT_DIR}/scripts/generate-code.sh" \
  -l cpp \
  "${ROOT_DIR}/examples/queries/housing/housing_regression.sql" \
  -o "${GENERATED_HPP}"

APP_INCLUDE="${ROOT_DIR}/examples/include/application/housing/application_housing_regression.hpp" \
EXTRA_ARGS="-I ${ROOT_DIR}/examples/include" \
"${ROOT_DIR}/scripts/build-generated-cpp.sh" \
  "${GENERATED_HPP}" \
  "${APP_BIN}"

(
  cd "${ROOT_DIR}/examples"
  "${APP_BIN}" --num-runs 1 --batch-size 1000 --no-output
)
