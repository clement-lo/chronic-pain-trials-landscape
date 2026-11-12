#!/usr/bin/env bash
# Run the whole pipeline.
#   ./run_pipeline.sh              pull today's data (re-using today's cache), then rebuild
#   ./run_pipeline.sh YYYY-MM-DD   rebuild from a pull already saved in data/raw/, no download
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

if [ $# -eq 0 ]; then
  $PY src/pull.py
fi
$PY src/build.py "$@"
$PY src/analyse.py
$PY src/figures.py
$PY src/report.py
$PY tests/check_numbers.py
