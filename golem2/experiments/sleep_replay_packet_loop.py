from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from ..actions import ActionRequest
from ..events import event
from ..host.sleep_replay import build_sleep_replay_packet
from ..policies.regime_manager import RegimeManager
from ..policies.types import PolicyRegime, RegimeThreshold
from ..store import EventLog


def main() -> None:
    run_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "sleep_replay_packet_loop"
        / uuid4().hex
    )
    event_log = EventLog(run_root / "events.jsonl")
    event_log.append(
        event(
            "heatmap_comparison",
            {
                "name": "synthetic_near_threshold",
                "delta": 0.8,
                "threshold": 1.0,
                "threshold_crossed": False,
            },
        )
    )

    regime = PolicyRegime(
        name="sleep_replay_budget_pressure",
        objective="Generate success and failure residue for sleep replay.",
        thresholds=[
            RegimeThreshold("front_obstacle_risk", "distance_panorama", 0.0, 0.1, 0.3),
            RegimeThreshold("clear_path_low", "occupancy_free", 0.0, 0.5, 0.2),
        ],
    )
    manager = RegimeManager([regime], event_log=event_log)
    manager.execute(
        "sleep_replay_budget_pressure",
        ActionRequest(
            action_type="adjust_threshold",
            threshold_name="front_obstacle_risk",
            threshold_delta=0.05,
            urgency_delta=-0.05,
            rationale="Successful adjustment for replay contrast.",
        ),
    )
    manager.execute(
        "sleep_replay_budget_pressure",
        ActionRequest(
            action_type="adjust_threshold",
            threshold_name="clear_path_low",
            threshold_delta=-0.05,
            urgency_delta=0.2,
            rationale="Intentional urgency budget failure for replay focus.",
        ),
    )

    packet = build_sleep_replay_packet(event_log.path, event_log.read())
    print(json.dumps(packet, indent=2))


if __name__ == "__main__":
    main()
