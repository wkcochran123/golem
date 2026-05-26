from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from ..actions import ActionRequest
from ..graph import KnowledgeGraph
from ..policies.regime_manager import RegimeManager
from ..policies.regimes import find_cat_regime
from ..store import EventLog
from ..vision.latches import ProjectionLatch, min_law
from ..vision.projection_transforms import RiskPanoramaTransform


def main() -> None:
    run_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "regime_threshold_loop"
        / uuid4().hex
    )
    run_root.mkdir(parents=True, exist_ok=True)
    graph = KnowledgeGraph(run_root / "graph.sqlite")
    event_log = EventLog(run_root / "events.jsonl")
    regime = find_cat_regime()
    latch = ProjectionLatch(
        "motion_salience_gate",
        "distance",
        parent_thresholds=[0.0],
        threshold_law=min_law,
        ema_alpha=0.5,
    )
    manager = RegimeManager([regime], graph=graph, event_log=event_log)
    manager.bind_latch("find_cat", "motion_salience", latch)
    result = manager.execute(
        "find_cat",
        ActionRequest(
            action_type="adjust_threshold",
            threshold_name="motion_salience",
            threshold_delta=-0.1,
            urgency_delta=0.05,
            rationale="Motion near the couch is salient but still below category confidence.",
        ),
    )
    projection = RiskPanoramaTransform(danger_distance=0.45).apply([0.3])
    latch_state = latch.update(projection)
    print(
        json.dumps(
            {
                "before": regime.to_payload(),
                "result": result.to_payload(),
                "after": manager.regimes["find_cat"].to_payload(),
                "bound_latch": latch_state.to_payload(),
                "events": list(event_log.read()),
                "graph": graph.summary(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
