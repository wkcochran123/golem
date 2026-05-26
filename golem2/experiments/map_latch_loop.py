from __future__ import annotations

import json
import math

from ..mapping.occupancy import OccupancyGrid, Pose2D
from ..vision.latches import ProjectionLatch, min_law


def main() -> None:
    directions = [
        0.0,
        math.pi / 4,
        math.pi / 2,
        3 * math.pi / 4,
        math.pi,
        -3 * math.pi / 4,
        -math.pi / 2,
        -math.pi / 4,
    ]
    grid = OccupancyGrid(width=21, height=21, resolution=0.25)
    pose = Pose2D(x=0.0, y=0.0, theta=0.0)
    distances = [0.75, 1.2, 1.4, 1.2, 1.8, 1.5, 1.4, 0.9]
    updates = grid.apply_proximity_scan(
        pose,
        distances,
        directions,
        max_range=2.0,
    )
    free_projection = grid.to_projection_map(mode="free")
    required_free_cells = 12
    free_latch = ProjectionLatch(
        "map_free_space_gate",
        "occupancy",
        parent_thresholds=[0.5],
        threshold_law=min_law,
        ema_alpha=0.5,
        latch_min_active=required_free_cells,
    )
    free_state = free_latch.update(free_projection)
    occupied_projection = grid.to_projection_map(mode="occupied")
    obstacle_latch = ProjectionLatch(
        "map_obstacle_gate",
        "occupancy",
        parent_thresholds=[0.5],
        threshold_law=min_law,
        ema_alpha=0.5,
        latch_min_active=1,
    )
    obstacle_state = obstacle_latch.update(occupied_projection)
    print(
        json.dumps(
            {
                "pose": {"x": pose.x, "y": pose.y, "theta": pose.theta},
                "updates": [update.to_payload() for update in updates],
                "free_projection": {
                    "kind": free_projection.kind,
                    "calibration": free_projection.calibration,
                    "score": sum(free_projection.values),
                },
                "free_latch": free_state.to_payload(),
                "required_free_cells": required_free_cells,
                "occupied_projection": {
                    "kind": occupied_projection.kind,
                    "calibration": occupied_projection.calibration,
                    "score": sum(occupied_projection.values),
                },
                "obstacle_latch": obstacle_state.to_payload(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
