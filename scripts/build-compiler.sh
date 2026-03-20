#!/bin/bash
set -euo pipefail

SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
COMPILER_DIR=${SCRIPTS_DIR}/../compiler
SBT_CACHE_DIR=${SBT_CACHE_DIR:-/tmp/fivm-sbt-cache}
IVY_CACHE_DIR=${IVY_CACHE_DIR:-/tmp/fivm-ivy2}
RUNTIME_CACHE_DIR=${RUNTIME_CACHE_DIR:-/tmp/fivm-sbt-runtime}

mkdir -p "${SBT_CACHE_DIR}" "${IVY_CACHE_DIR}" "${RUNTIME_CACHE_DIR}"
export XDG_RUNTIME_DIR="${RUNTIME_CACHE_DIR}"
LOCK_FILE="${SBT_CACHE_DIR}/assembly.lock"

echo "Compiling F-IVM..."
cd ${COMPILER_DIR}
exec 9>"${LOCK_FILE}"
flock 9
sbt \
  --batch \
  --no-share \
  --sbt-dir "${SBT_CACHE_DIR}/global" \
  --sbt-boot "${SBT_CACHE_DIR}/boot" \
  --sbt-cache "${SBT_CACHE_DIR}/cache" \
  --ivy "${IVY_CACHE_DIR}" \
  assembly
cd -
echo "Done."
