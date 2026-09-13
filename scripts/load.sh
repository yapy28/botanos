#!/bin/bash
set -e

# BOTANOS load script: builds the QLever index from the N-Quads file and starts the server.
#
# Prerequisites:
#   pip install qlever
#   python3 scripts/build_rdf.py  (generates data/rdf/plants.nq)
#
# Usage:
#   ./scripts/load.sh          # index + start server
#   ./scripts/load.sh index    # index only
#   ./scripts/load.sh start    # start server only (assumes index exists)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
QLEVER_DIR="${ROOT_DIR}/qlever"
QLEVERFILE="${ROOT_DIR}/Qleverfile"

mkdir -p "${QLEVER_DIR}"
cd "${QLEVER_DIR}"

# Copy the N-Quads file into qlever/ so Docker can access it
cp "${ROOT_DIR}/data/rdf/plants.nq" "${QLEVER_DIR}/plants.nq"

ACTION="${1:-all}"

case "$ACTION" in
  index)
    echo "Building QLever index..."
    qlever --qleverfile "${QLEVERFILE}" index
    echo "Index built. Run 'scripts/load.sh start' to start the server."
    ;;
  start)
    echo "Starting QLever server on port 7019..."
    qlever --qleverfile "${QLEVERFILE}" start
    ;;
  all|*)
    echo "Building QLever index..."
    qlever --qleverfile "${QLEVERFILE}" index
    echo ""
    echo "Starting QLever server on port 7019..."
    qlever --qleverfile "${QLEVERFILE}" start
    ;;
esac
