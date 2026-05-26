from __future__ import annotations

from pathlib import Path
from typing import Iterable


DEFAULT_SLEEP_MODELS = ["heatmap_reader", "urgency_policy"]


def build_sleep_replay_packet(
    ledger_path: Path,
    events: Iterable[dict],
    *,
    models: list[str] | None = None,
) -> dict:
    records = list(events)
    failures = [
        record
        for record in records
        if _event_result(record).get("ok") is False
    ]
    threshold_adjustments = [
        record for record in records if record.get("kind") == "threshold_adjustment"
    ]
    threshold_failures = [
        record
        for record in threshold_adjustments
        if _event_result(record).get("ok") is False
    ]
    return {
        "ledger_path": str(ledger_path),
        "models": models or DEFAULT_SLEEP_MODELS,
        "sampling": {
            "failures": True,
            "near_threshold": True,
            "successful_crossings": True,
            "rare_sensor_states": True,
        },
        "summary": {
            "event_count": len(records),
            "failure_count": len(failures),
            "threshold_adjustment_count": len(threshold_adjustments),
            "threshold_failure_count": len(threshold_failures),
            "failure_kinds": _failure_kind_counts(failures),
        },
        "replay_focus": _replay_focus(failures, threshold_adjustments),
    }


def _event_result(record: dict) -> dict:
    payload = record.get("payload", {})
    result = payload.get("result", {})
    return result if isinstance(result, dict) else {}


def _failure_kind_counts(records: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        failure_kind = _event_result(record).get("failure_kind")
        if not isinstance(failure_kind, str) or not failure_kind:
            continue
        counts[failure_kind] = counts.get(failure_kind, 0) + 1
    return counts


def _replay_focus(
    failures: list[dict],
    threshold_adjustments: list[dict],
) -> list[dict]:
    focus: list[dict] = []
    for record in failures:
        focus.append(
            {
                "event_id": record.get("id", ""),
                "kind": record.get("kind", ""),
                "reason": _event_result(record).get("failure_kind", "unknown_failure"),
                "priority": "high",
            }
        )
    for record in threshold_adjustments:
        result = _event_result(record)
        if result.get("ok") is False:
            continue
        focus.append(
            {
                "event_id": record.get("id", ""),
                "kind": record.get("kind", ""),
                "reason": "successful_threshold_adjustment",
                "priority": "medium",
            }
        )
    return focus
