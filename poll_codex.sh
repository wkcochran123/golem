#!/usr/bin/env bash
set -euo pipefail

RYOT_AGENT_INSTANCE="${RYOT_AGENT_INSTANCE:-primary}" \
  python3 ryot_poll.py codex notes_for_codex.md .handoff_codex_state "${RYOT_POLL_INTERVAL:-2}"
