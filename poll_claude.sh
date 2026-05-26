#!/usr/bin/env bash
set -euo pipefail

python3 ryot_poll.py claude notes_for_claude.md .handoff_claude_state "${RYOT_POLL_INTERVAL:-2}"
