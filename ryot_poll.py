#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import time
import os
from pathlib import Path


HEADER_RE = re.compile(r"<!-- (?:HANDOFF|BROADCAST)(?P<header>.*?)-->", re.DOTALL)


def main() -> int:
    if len(sys.argv) not in {4, 5}:
        print(
            "usage: ryot_poll.py <agent_id> <inbox_file> <state_file> [interval]",
            file=sys.stderr,
        )
        return 2
    agent = sys.argv[1]
    instance = os.environ.get("RYOT_AGENT_INSTANCE", "")
    inbox = Path(sys.argv[2])
    state_file = Path(sys.argv[3])
    interval = float(sys.argv[4]) if len(sys.argv) == 5 else 3.0

    inbox.touch()
    if not state_file.exists():
        state_file.write_text("last_turn=0\n", encoding="utf-8")

    broadcast_file = inbox.parent / "notes_broadcast.md"
    broadcast_file.touch()

    while True:
        state = read_state(state_file)
        changed = False
        for source_label, source_path in (("inbox", inbox), ("broadcast", broadcast_file)):
            text = source_path.read_text(encoding="utf-8")
            for block, fields in handoff_blocks(text):
                sender = fields.get("from", "")
                receiver = fields.get("to", "")
                sender_instance = fields.get("from_instance", "")
                receiver_instance = fields.get("to_instance", "")
                if receiver != agent and receiver != "*":
                    continue
                if instance and receiver_instance and receiver_instance != instance:
                    continue
                if is_self_authored(agent, instance, sender, sender_instance):
                    continue
                thread = fields.get("thread", "main")
                lane = fields.get("lane", "default")
                try:
                    turn = int(fields.get("turn", "0"))
                except ValueError:
                    continue
                key = state_key(thread, lane)
                last_turn = int(state.get(key, fallback_last_turn(state, key)))
                if turn <= last_turn:
                    continue
                claim = fields.get("claim", "unclaimed")
                tag = "BROADCAST" if receiver == "*" else "HANDOFF"
                print(
                    f"\n===== RYOT {tag} for {agent} "
                    f"instance={instance or '*'} thread={thread} "
                    f"lane={lane} turn={turn} claim={claim} "
                    f"source={source_label} =====",
                    flush=True,
                )
                print(block, flush=True)
                state[key] = str(turn)
                changed = True
        if changed:
            write_state(state_file, state)
        time.sleep(interval)


def handoff_blocks(text: str) -> list[tuple[str, dict[str, str]]]:
    matches = list(HEADER_RE.finditer(text))
    blocks: list[tuple[str, dict[str, str]]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        fields = parse_header(match.group("header"))
        blocks.append((block, fields))
    return blocks


def parse_header(header: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in header.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def read_state(path: Path) -> dict[str, str]:
    state: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        state[key.strip()] = value.strip()
    return state


def write_state(path: Path, state: dict[str, str]) -> None:
    lines = [f"{key}={state[key]}" for key in sorted(state)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fallback_last_turn(state: dict[str, str], key: str) -> str:
    if key == state_key("main", "default"):
        return state.get("last_turn", "0")
    return "0"


def state_key(thread: str, lane: str) -> str:
    return f"last_turn__{sanitize(thread)}__{sanitize(lane)}"


def sanitize(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned or "default"


def is_self_authored(
    agent: str,
    instance: str,
    sender: str,
    sender_instance: str,
) -> bool:
    if sender != agent:
        return False
    if instance:
        return sender_instance == instance
    return not sender_instance


if __name__ == "__main__":
    raise SystemExit(main())
