#!/usr/bin/env bash
set -euo pipefail

python3 ryot_monitor.py --watch --interval "${RYOT_MONITOR_INTERVAL:-10}"
