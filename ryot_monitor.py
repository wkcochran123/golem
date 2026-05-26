#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import time
from dataclasses import dataclass
from pathlib import Path

from ryot_poll import handoff_blocks


REPLY_REQUIRED = {"NEEDS_RESPONSE", "CHANGES_REQUESTED", "CHANGES_APPLIED", "CONVERGED"}
LANE_CLOSED = {"HANDOFF_CONVERGED"}
PHASE_ORDER = ("stuck", "design", "implement", "converged", "unknown")
SIDE_TRACK_STATUSES = {"WITHDRAWN", "INFO_ONLY"}


@dataclass(frozen=True)
class HandoffSummary:
    inbox: str
    sender: str
    receiver: str
    turn: int
    status: str
    thread: str
    lane: str
    claim: str
    closure_owner: str
    checklist: str
    scope: str
    depends_on: str

    @property
    def lane_key(self) -> tuple[str, str]:
        # Key by (thread, lane) only. The two-phase stop and the back-and-forth
        # within a single lane span both inboxes, so the "latest turn" should be
        # the highest turn across BOTH directions, not per-receiver. The receiver
        # field still tells you who owes the next reply (it's the recipient of
        # the latest message); this just stops the monitor from showing a stale
        # codex→claude turn as still-unanswered when claude has already replied
        # back in the opposite direction.
        return (self.thread, self.lane)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize active RYOT lanes and checklists.")
    parser.add_argument("--codex-inbox", default="notes_for_codex.md")
    parser.add_argument("--claude-inbox", default="notes_for_claude.md")
    parser.add_argument("--codex-state", default=".handoff_codex_state")
    parser.add_argument("--claude-state", default=".handoff_claude_state")
    parser.add_argument("--checklist", default="RYOT_CHECKLIST.md")
    parser.add_argument("--include-converged", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=float, default=10.0)
    args = parser.parse_args()

    while True:
        print(render_dashboard(args), flush=True)
        if not args.watch:
            return 0
        time.sleep(args.interval)


def render_dashboard(args: argparse.Namespace) -> str:
    inboxes = [Path(args.codex_inbox), Path(args.claude_inbox)]
    handoffs = collect_handoffs(inboxes)
    latest = latest_by_lane(handoffs)
    consumed = max_consumed_turns(
        [Path(args.codex_state), Path(args.claude_state)],
    )
    checklist_path = Path(args.checklist)
    closed_checklist_sections = (
        checklist_closed_sections(checklist_path) if checklist_path.exists() else set()
    )
    lines = ["# RYOT Monitor", ""]
    lines.append("## Active Lanes")
    if not latest:
        lines.append("- No handoffs found.")
    for summary in sorted(latest.values(), key=lambda item: item.lane_key):
        checklist_section = _checklist_section(summary.checklist)
        checklist_closed = (
            checklist_section and checklist_section in closed_checklist_sections
        )
        needs_reply = summary.status in REPLY_REQUIRED
        closed = summary.status in LANE_CLOSED or checklist_closed
        marker = "!" if needs_reply else "x" if closed else "-"
        if checklist_closed:
            marker = "x"
        lines.append(
            (
                f"- [{marker}] to={summary.receiver} thread={summary.thread} "
                f"lane={summary.lane} turn={summary.turn} status={summary.status} "
                f"from={summary.sender} claim={summary.claim or 'unclaimed'}"
            )
        )
        if summary.closure_owner or summary.checklist:
            lines.append(
                f"  owner={summary.closure_owner or 'unset'} checklist={summary.checklist or 'unset'}"
            )
        if summary.scope:
            lines.append(f"  scope={summary.scope}")

    lines.extend(["", "## Phases"])
    lines.extend(
        render_phase_summary(
            handoffs,
            include_converged=args.include_converged,
            checklist_path=checklist_path,
        )
    )

    lines.extend(["", "## Reply Required"])
    required_replies = reply_required(
        latest,
        handoffs,
        consumed=consumed,
        closed_checklist_sections=closed_checklist_sections,
    )
    if not required_replies:
        lines.append("- None.")
    for summary in sorted(required_replies, key=lambda item: item.lane_key):
        lines.append(
            f"- {summary.receiver} must answer {summary.thread}/{summary.lane} "
            f"turn {summary.turn} ({summary.status})."
        )

    lines.extend(["", "## Checklist"])
    if checklist_path.exists():
        lines.extend(render_checklist_summary(checklist_path))
    else:
        lines.append(f"- Missing checklist: {checklist_path}")
    return "\n".join(lines)


def collect_handoffs(inboxes: list[Path]) -> list[HandoffSummary]:
    summaries: list[HandoffSummary] = []
    for inbox in inboxes:
        if not inbox.exists():
            continue
        for _block, fields in handoff_blocks(inbox.read_text(encoding="utf-8")):
            if not _valid_handoff_header(fields):
                continue
            try:
                turn = int(fields.get("turn", "0"))
            except ValueError:
                continue
            summaries.append(
                HandoffSummary(
                    inbox=str(inbox),
                    sender=_agent_name(fields.get("from", ""), fields.get("from_instance", "")),
                    receiver=_agent_name(fields.get("to", ""), fields.get("to_instance", "")),
                    turn=turn,
                    status=fields.get("status", ""),
                    thread=fields.get("thread", "main"),
                    lane=fields.get("lane", "default"),
                    claim=fields.get("claim", ""),
                    closure_owner=fields.get("closure_owner", ""),
                    checklist=fields.get("checklist", ""),
                    scope=fields.get("scope", ""),
                    depends_on=fields.get("depends_on", ""),
                )
            )
    return summaries


def latest_by_lane(handoffs: list[HandoffSummary]) -> dict[tuple[str, str], HandoffSummary]:
    """Latest handoff per (thread, lane), across both inboxes.

    Two-phase stop and back-and-forth audits span both inboxes. The latest
    turn in a lane is the highest turn across both directions; whoever sent
    that latest message is the one who just acted, and the receiver field on
    that message tells you who owes the next reply (or whether the lane is
    closed if status is HANDOFF_CONVERGED).
    """
    latest: dict[tuple[str, str], HandoffSummary] = {}
    for summary in handoffs:
        prior = latest.get(summary.lane_key)
        if prior is None or summary.turn > prior.turn:
            latest[summary.lane_key] = summary
    return latest


def latest_qualifying_by_lane(
    handoffs: list[HandoffSummary],
) -> dict[tuple[str, str], HandoffSummary]:
    latest: dict[tuple[str, str], HandoffSummary] = {}
    for summary in handoffs:
        if summary.status in SIDE_TRACK_STATUSES:
            continue
        prior = latest.get(summary.lane_key)
        if prior is None or summary.turn > prior.turn:
            latest[summary.lane_key] = summary
    return latest


def render_phase_summary(
    handoffs: list[HandoffSummary],
    *,
    include_converged: bool,
    checklist_path: Path,
) -> list[str]:
    visible_keys = {handoff.lane_key for handoff in handoffs}
    qualifying = latest_qualifying_by_lane(handoffs)
    operator_hints = (
        operator_block_hints(checklist_path) if checklist_path.exists() else {}
    )
    grouped: dict[str, list[HandoffSummary | tuple[tuple[str, str], str]]] = {
        phase: [] for phase in PHASE_ORDER
    }
    for lane_key in sorted(visible_keys):
        summary = qualifying.get(lane_key)
        if summary is None:
            grouped["unknown"].append((lane_key, "no qualifying status"))
            continue
        phase = phase_for(summary)
        if phase == "converged" and not include_converged:
            continue
        grouped[phase].append(summary)

    lines: list[str] = []
    for phase in PHASE_ORDER:
        items = grouped[phase]
        if not items:
            continue
        lines.append(f"### {phase}")
        for item in items:
            if isinstance(item, tuple):
                lane_key, reason = item
                lines.append(f"- {lane_key[0]}/{lane_key[1]} ({reason})")
                continue
            hint = ""
            if phase == "stuck":
                hint_text = operator_hints.get(item.lane)
                if hint_text:
                    hint = f" operator_hint={hint_text}"
            lines.append(
                (
                    f"- {item.thread}/{item.lane} turn {item.turn} "
                    f"status={item.status} to={item.receiver}{hint}"
                )
            )
    if not lines:
        lines.append("- No visible lanes in non-excluded phases.")
    return lines


def phase_for(summary: HandoffSummary) -> str:
    if summary.status == "BLOCKED":
        return "stuck"
    if summary.status == "NEEDS_RESPONSE":
        return "design"
    if summary.status == "WORKING":
        return "implement" if summary.thread == "implementation" else "design"
    if summary.status in {"CHANGES_APPLIED", "CHANGES_REQUESTED"}:
        return "implement"
    if summary.status in {"CONVERGED", "HANDOFF_CONVERGED"}:
        return "converged"
    return "unknown"


def operator_block_hints(path: Path) -> dict[str, str]:
    hints: dict[str, str] = {}
    in_queue = False
    item_re = re.compile(r"^-\s+\[[ xX]\]\s+\*\*(?P<lane>[^*]+)\*\*\s+—\s+(?P<body>.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Operator Blocked Queue"):
            in_queue = True
            continue
        if in_queue and line.startswith("## "):
            break
        if not in_queue:
            continue
        match = item_re.match(line)
        if match:
            hints[match.group("lane")] = "Operator Blocked Queue"
    return hints


def reply_required(
    latest: dict[tuple[str, str], HandoffSummary],
    handoffs: list[HandoffSummary],
    *,
    consumed: dict[tuple[str, str], int] | None = None,
    closed_checklist_sections: set[str] | None = None,
) -> list[HandoffSummary]:
    audit_satisfied = _audit_satisfied_implementation_turns(handoffs)
    consumed = consumed or {}
    closed_checklist_sections = closed_checklist_sections or set()
    replies: list[HandoffSummary] = []
    for item in latest.values():
        if item.status not in REPLY_REQUIRED:
            continue
        checklist_section = _checklist_section(item.checklist)
        if checklist_section and checklist_section in closed_checklist_sections:
            continue
        if (
            item.thread == "implementation"
            and item.status == "CHANGES_APPLIED"
            and (
                (item.lane, item.turn) in audit_satisfied
                or (item.lane, -1) in audit_satisfied
            )
        ):
            continue
        # State-aware suppression: if a watcher's state file has consumed a
        # turn past the visible inbox turn for this lane, a later reply
        # existed but its handoff block was overwritten in the inbox before
        # we could see it. The apparent reply-required entry is stale.
        if consumed.get(item.lane_key, 0) > item.turn:
            continue
        replies.append(item)
    return replies


def max_consumed_turns(state_files: list[Path]) -> dict[tuple[str, str], int]:
    """Highest consumed turn per (thread, lane) across all watcher state files.

    Each state file has `last_turn__<thread>__<lane>=N` lines reflecting what
    that watcher has printed for its agent. If any watcher's state shows turn
    N for a (thread, lane), at least N turns were sent in that lane regardless
    of whether the original handoff blocks are still visible in the inbox.
    """
    consumed: dict[tuple[str, str], int] = {}
    key_re = re.compile(r"^last_turn__(?P<thread>.+?)__(?P<lane>.+)$")
    for path in state_files:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            try:
                turn = int(value.strip())
            except ValueError:
                continue
            match = key_re.match(key.strip())
            if match is None:
                continue
            lane_key = (match.group("thread"), match.group("lane"))
            if turn > consumed.get(lane_key, 0):
                consumed[lane_key] = turn
    return consumed


def _audit_satisfied_implementation_turns(handoffs: list[HandoffSummary]) -> set[tuple[str, int]]:
    satisfied: set[tuple[str, int]] = set()
    for item in handoffs:
        if item.thread != "audit":
            continue
        if item.status not in REPLY_REQUIRED | LANE_CLOSED:
            continue
        dependency = _implementation_dependency(item.depends_on)
        if dependency is not None:
            lane, turn = dependency
            satisfied.add((lane, turn))
            continue
        if item.status in LANE_CLOSED | {"CONVERGED", "CHANGES_REQUESTED"}:
            satisfied.add((item.lane, -1))
    return satisfied


def _implementation_dependency(depends_on: str) -> tuple[str, int] | None:
    match = re.fullmatch(r"implementation:(?P<lane>[^:]+):turn-(?P<turn>\d+)", depends_on)
    if match is None:
        return None
    return (match.group("lane"), int(match.group("turn")))


def render_checklist_summary(path: Path) -> list[str]:
    current_section = "root"
    open_items: list[tuple[str, str]] = []
    closed_count = 0
    open_count = 0
    section_re = re.compile(r"^##\s+(.+)$")
    item_re = re.compile(r"^-\s+\[(?P<mark>[ xX])\]\s+(?P<body>.+)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        section_match = section_re.match(line)
        if section_match:
            current_section = section_match.group(1)
            continue
        item_match = item_re.match(line)
        if not item_match:
            continue
        if item_match.group("mark").strip().lower() == "x":
            closed_count += 1
        else:
            open_count += 1
            open_items.append((current_section, item_match.group("body")))

    lines = [f"- Closed items: {closed_count}", f"- Open items: {open_count}"]
    for section, item in open_items:
        lines.append(f"- [ ] {section}: {item}")
    return lines


def checklist_closed_sections(path: Path) -> set[str]:
    current_section = "root"
    sections: dict[str, list[bool]] = {}
    section_re = re.compile(r"^##\s+(.+)$")
    item_re = re.compile(r"^-\s+\[(?P<mark>[ xX])\]\s+.+$")
    for line in path.read_text(encoding="utf-8").splitlines():
        section_match = section_re.match(line)
        if section_match:
            current_section = section_match.group(1)
            continue
        item_match = item_re.match(line)
        if not item_match:
            continue
        sections.setdefault(current_section, []).append(
            item_match.group("mark").strip().lower() == "x"
        )
    return {
        _section_anchor(section)
        for section, marks in sections.items()
        if marks and all(marks)
    }


def _checklist_section(checklist: str) -> str:
    if "#" not in checklist:
        return ""
    return checklist.rsplit("#", 1)[1].strip()


def _section_anchor(section: str) -> str:
    return section.strip().lower().replace(" ", "-")


def _agent_name(agent: str, instance: str) -> str:
    if instance:
        return f"{agent}:{instance}"
    return agent


def _valid_handoff_header(fields: dict[str, str]) -> bool:
    required = {"from", "to", "turn", "status"}
    return all(fields.get(field) for field in required)


if __name__ == "__main__":
    raise SystemExit(main())
