from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from ..vision.latches import ProjectionMap


OccupancyProjectionMode = Literal["occupied", "free"]
FREE_SPACE_INVERSION = {-1: 1, 0: 0, 1: -1}


@dataclass(frozen=True)
class Pose2D:
    x: float
    y: float
    theta: float


@dataclass(frozen=True)
class OccupancyUpdate:
    x: int
    y: int
    value: int
    evidence: str

    def to_payload(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "value": self.value,
            "evidence": self.evidence,
        }


class OccupancyGrid:
    def __init__(self, width: int, height: int, resolution: float):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.values = [[0 for _ in range(width)] for _ in range(height)]

    def apply_proximity_scan(
        self,
        pose: Pose2D,
        distances: list[float],
        directions: list[float],
        *,
        max_range: float,
    ) -> list[OccupancyUpdate]:
        updates: list[OccupancyUpdate] = []
        for distance, direction in zip(distances, directions, strict=True):
            angle = pose.theta + direction
            ray_distance = min(distance, max_range)
            free_steps = int(ray_distance / self.resolution)
            for step in range(1, free_steps):
                updates.append(
                    self._mark_world(
                        pose.x + math.cos(angle) * step * self.resolution,
                        pose.y + math.sin(angle) * step * self.resolution,
                        -1,
                        "free_space_along_sensor_ray",
                    )
                )
            if distance < max_range:
                updates.append(
                    self._mark_world(
                        pose.x + math.cos(angle) * distance,
                        pose.y + math.sin(angle) * distance,
                        1,
                        "occupied_endpoint_from_proximity",
                    )
                )
        return [update for update in updates if update is not None]

    def to_rows(self) -> list[list[int]]:
        return [row[:] for row in self.values]

    def mark_world_cell(
        self, world_x: float, world_y: float, value: int, evidence: str
    ) -> OccupancyUpdate | None:
        return self._mark_world(world_x, world_y, value, evidence)

    def to_projection_map(
        self,
        *,
        mode: OccupancyProjectionMode = "occupied",
    ) -> ProjectionMap:
        if mode == "occupied":
            rows = self.to_rows()
            calibration = "occupancy:occupied=+1,free=-1,unknown=0"
        elif mode == "free":
            rows = [[FREE_SPACE_INVERSION[value] for value in row] for row in self.values]
            calibration = "occupancy:free=+1,occupied=-1,unknown=0"
        else:
            raise ValueError(f"Unknown occupancy projection mode: {mode}")
        return ProjectionMap.from_rows(
            "occupancy",
            rows,
            threshold=0.0,
            calibration=calibration,
        )

    def _mark_world(
        self, world_x: float, world_y: float, value: int, evidence: str
    ) -> OccupancyUpdate | None:
        grid_x = int(round(world_x / self.resolution + self.width / 2))
        grid_y = int(round(world_y / self.resolution + self.height / 2))
        if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
            return None
        if value == 1:
            self.values[grid_y][grid_x] = 1
        elif self.values[grid_y][grid_x] == 0:
            self.values[grid_y][grid_x] = -1
        return OccupancyUpdate(grid_x, grid_y, self.values[grid_y][grid_x], evidence)
