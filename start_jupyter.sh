#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

export MPLCONFIGDIR="${MPLCONFIGDIR:-$ROOT_DIR/.jupyter-work/matplotlib}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$ROOT_DIR/.jupyter-work/cache}"
export JUPYTER_CONFIG_DIR="${JUPYTER_CONFIG_DIR:-$ROOT_DIR/.jupyter-work/config}"
export JUPYTER_DATA_DIR="${JUPYTER_DATA_DIR:-$ROOT_DIR/.jupyter-work/data}"
export JUPYTER_RUNTIME_DIR="${JUPYTER_RUNTIME_DIR:-$ROOT_DIR/.jupyter-work/runtime}"
export IPYTHONDIR="${IPYTHONDIR:-$ROOT_DIR/.jupyter-work/ipython}"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p \
  "$MPLCONFIGDIR" \
  "$XDG_CACHE_HOME" \
  "$JUPYTER_CONFIG_DIR" \
  "$JUPYTER_DATA_DIR" \
  "$JUPYTER_RUNTIME_DIR" \
  "$IPYTHONDIR"

cd "$ROOT_DIR"
exec "$PYTHON_BIN" -m jupyterlab \
  --no-browser \
  --ServerApp.ip=127.0.0.1 \
  --ServerApp.root_dir="$ROOT_DIR" \
  --FileContentsManager.preferred_dir="$ROOT_DIR/golem2/notebooks" \
  "$@"
