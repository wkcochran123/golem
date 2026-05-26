from __future__ import annotations

import json

from ..vision.latches import ProjectionLatch, ProjectionMap, max_law, split_urgency


def main() -> None:
    latch = ProjectionLatch(
        "goal_distance_gate",
        "distance",
        parent_thresholds=split_urgency(0.5, 2),
        threshold_law=max_law,
        latch_min_active=2,
    )
    frames = [
        [[0.1, 0.2, 0.4], [0.1, 0.3, 0.5]],
        [[0.2, 0.5, 0.7], [0.1, 0.4, 0.8]],
        [[0.5, 0.7, 0.9], [0.3, 0.6, 1.0]],
    ]
    states = []
    for rows in frames:
        projection = ProjectionMap.from_rows(
            "distance",
            rows,
            threshold=0.0,
            calibration="parent-threshold:max(distance_parent,goal_parent)",
        )
        states.append(latch.update(projection).to_payload())
    print(json.dumps({"states": states}, indent=2))


if __name__ == "__main__":
    main()
