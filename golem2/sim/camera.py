from __future__ import annotations

import math

from ..mapping.occupancy import Pose2D
from .ideal_basement import IdealBasementScene


def render_top_down(
    scene: IdealBasementScene,
    pose: Pose2D,
    width: int = 64,
    height: int = 64,
) -> list[list[int]]:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive.")
    min_x, max_x, min_y, max_y = _bounds(scene)
    frame = [[0 for _ in range(width)] for _ in range(height)]
    for wall in scene.walls:
        length = math.hypot(wall.x2 - wall.x1, wall.y2 - wall.y1)
        samples = max(width, height, int(length / max((max_x - min_x) / width, 1e-6)) * 2)
        for index in range(samples + 1):
            t = index / max(samples, 1)
            x = wall.x1 + (wall.x2 - wall.x1) * t
            y = wall.y1 + (wall.y2 - wall.y1) * t
            px, py = _world_to_pixel(x, y, width, height, min_x, max_x, min_y, max_y)
            if 0 <= px < width and 0 <= py < height:
                frame[py][px] = 1
    robot_x, robot_y = _world_to_pixel(pose.x, pose.y, width, height, min_x, max_x, min_y, max_y)
    if 0 <= robot_x < width and 0 <= robot_y < height:
        frame[robot_y][robot_x] = 2
    return frame


def _bounds(scene: IdealBasementScene) -> tuple[float, float, float, float]:
    xs = [coord for wall in scene.walls for coord in (wall.x1, wall.x2)]
    ys = [coord for wall in scene.walls for coord in (wall.y1, wall.y2)]
    margin = 0.05
    return min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin


def _world_to_pixel(
    x: float,
    y: float,
    width: int,
    height: int,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
) -> tuple[int, int]:
    px = int(round((x - min_x) / (max_x - min_x) * (width - 1)))
    py = int(round((max_y - y) / (max_y - min_y) * (height - 1)))
    return px, py
