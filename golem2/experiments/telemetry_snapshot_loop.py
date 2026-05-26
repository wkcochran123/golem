from __future__ import annotations

import json

from ..telemetry.snapshot import TelemetrySnapshot
from ..vision.latches import ProjectionLatch, ProjectionMap, max_law, split_urgency


def main() -> None:
    latch = ProjectionLatch(
        "front_obstacle_gate",
        "distance",
        parent_thresholds=split_urgency(0.5, 8),
        threshold_law=max_law,
    )
    projection = ProjectionMap.from_rows(
        "distance",
        [[0.0, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5, 0.0]],
        threshold=0.0,
        calibration="demo",
    )
    state = latch.update(projection)
    snapshot = TelemetrySnapshot.capture(
        component=state.name,
        kind="projection_latch",
        payload=state.to_payload(),
    )
    print(json.dumps(snapshot.to_payload(), indent=2))


if __name__ == "__main__":
    main()

