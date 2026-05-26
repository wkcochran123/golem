from __future__ import annotations

import json
import math

from ..mapping.occupancy import OccupancyGrid, Pose2D
from ..vision.quantized_heatmap import HeatMap


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
    heatmap = HeatMap.from_sensor_grid(
        grid.to_rows(),
        threshold=0.0,
        calibration="occupancy:occupied=+1,free=-1,unknown=0",
        neutral_zero=True,
    )
    occupancy_projection = grid.to_projection_map(mode="occupied")
    map_score = heatmap.total_score()
    projection_score = sum(occupancy_projection.values)
    if map_score != projection_score:
        raise AssertionError("HeatMap and ProjectionMap scores diverged.")
    print(
        json.dumps(
            {
                "pose": {"x": pose.x, "y": pose.y, "theta": pose.theta},
                "updates": [update.to_payload() for update in updates],
                "occupied_count": sum(
                    1 for row in grid.to_rows() for value in row if value == 1
                ),
                "free_count": sum(
                    1 for row in grid.to_rows() for value in row if value == -1
                ),
                "map_score": map_score,
                "projection": {
                    "kind": occupancy_projection.kind,
                    "calibration": occupancy_projection.calibration,
                    "score": projection_score,
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
