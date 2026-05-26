from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from ..actions import ActionRequest
from ..graph import KnowledgeGraph
from ..policies.regime_manager import RegimeManager
from ..policies.types import PolicyRegime, RegimeThreshold
from ..store import EventLog


def _adjust(threshold_name: str, threshold_delta: float) -> ActionRequest:
    return ActionRequest(
        action_type="adjust_threshold",
        threshold_name=threshold_name,
        threshold_delta=threshold_delta,
        rationale="Exercise opt-in regime adjustment cooldown.",
    )


def main() -> None:
    run_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "regime_rate_limit_loop"
        / uuid4().hex
    )
    run_root.mkdir(parents=True, exist_ok=True)
    graph = KnowledgeGraph(run_root / "graph.sqlite")
    event_log = EventLog(run_root / "events.jsonl")

    regime = PolicyRegime(
        name="basement_threshold_safety",
        objective="Keep threshold joystick moves smooth enough for local reflexes.",
        thresholds=[
            RegimeThreshold(
                name="front_obstacle_risk",
                projection="distance_panorama",
                current_value=0.0,
                threshold=0.0,
                urgency=0.25,
                min_threshold=0.0,
                max_threshold=0.5,
            ),
            RegimeThreshold(
                name="clear_path_low",
                projection="occupancy_free",
                current_value=0.0,
                threshold=0.5,
                urgency=0.2,
                min_threshold=0.1,
                max_threshold=0.9,
            ),
        ],
        allowed_actions=["adjust_threshold", "noop"],
    )
    manager = RegimeManager(
        [regime],
        graph=graph,
        event_log=event_log,
        adjustment_cooldown_steps=1,
    )

    requests = [
        _adjust("front_obstacle_risk", 0.1),
        _adjust("front_obstacle_risk", 0.1),
        _adjust("clear_path_low", -0.05),
        _adjust("front_obstacle_risk", 0.1),
    ]
    results = [
        manager.execute("basement_threshold_safety", request)
        for request in requests
    ]

    print(
        json.dumps(
            {
                "cooldown_steps": manager.adjustment_cooldown_steps,
                "requests": [request.to_payload() for request in requests],
                "results": [result.to_payload() for result in results],
                "final_regime": manager.regimes["basement_threshold_safety"].to_payload(),
                "events": list(event_log.read()),
                "graph": graph.summary(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
