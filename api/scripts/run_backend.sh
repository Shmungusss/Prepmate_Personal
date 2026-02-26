#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
source .venv/bin/activate

export PYTHONPATH="$(pwd)/src:${PYTHONPATH}"

uvicorn src.app:app --reload --reload-dir src --reload-exclude .venv --host 0.0.0.0 --port 8000