from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from ..actions import ActionRequest
from ..graph import KnowledgeGraph
from ..policies.regime_manager import RegimeManager
from ..policies.types import PolicyRegime, RegimeThreshold
from ..store import EventLog


def main() -> None:
    run_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "urgency_budget_pressure_loop"
        / uuid4().hex
    )
    run_root.mkdir(parents=True, exist_ok=True)
    graph = KnowledgeGraph(run_root / "graph.sqlite")
    event_log = EventLog(run_root / "events.jsonl")

    regime = PolicyRegime(
        name="budget_pressure",
        objective="Demonstrate urgency budget rejection as useful residue.",
        thresholds=[
            RegimeThreshold(
                name="front_obstacle_risk",
                projection="distance_panorama",
                current_value=0.0,
                threshold=0.1,
                urgency=0.3,
            ),
            RegimeThreshold(
                name="clear_path_low",
                projection="occupancy_free",
                current_value=0.0,
                threshold=0.5,
                urgency=0.2,
            ),
        ],
        allowed_actions=["adjust_threshold", "noop"],
    )
    manager = RegimeManager([regime], graph=graph, event_log=event_log)
    before = manager.regimes["budget_pressure"].to_payload()
    result = manager.execute(
        "budget_pressure",
        ActionRequest(
            action_type="adjust_threshold",
            threshold_name="clear_path_low",
            threshold_delta=-0.05,
            urgency_delta=0.05,
            rationale="Intentionally exceed the shared urgency budget.",
        ),
    )
    after = manager.regimes["budget_pressure"].to_payload()
    print(
        json.dumps(
            {
                "before": before,
                "result": result.to_payload(),
                "after": after,
                "unchanged": before == after,
                "events": list(event_log.read()),
                "graph": graph.summary(),
                "affordances": graph.affordances(),
                "failures": graph.failures(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
