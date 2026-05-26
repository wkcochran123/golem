from __future__ import annotations

import math
from dataclasses import dataclass

from ..mapping.occupancy import Pose2D


@dataclass(frozen=True)
class Wall:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class SafeMoveResult:
    """Record of what the collision-avoiding mover decided to do.

    `intervened` is True when the requested forward motion would have crossed
    a wall and the move was truncated. `allowed_forward` reports the actual
    forward distance applied (always <= requested_forward). `wall_distance`
    is the distance to the nearest wall along the forward ray, or None if no
    wall lay in front.
    """
    intervened: bool
    requested_forward: float
    allowed_forward: float
    wall_distance: float | None = None
    clearance: float = 0.0

    def to_payload(self) -> dict:
        return {
            "intervened": self.intervened,
            "requested_forward": self.requested_forward,
            "allowed_forward": self.allowed_forward,
            "wall_distance": self.wall_distance,
            "clearance": self.clearance,
        }


@dataclass(frozen=True)
class IdealBasementScene:
    walls: tuple[Wall, ...]
    max_range: float = 2.0

    @staticmethod
    def box(width: float = 4.0, height: float = 3.0, max_range: float = 2.0) -> "IdealBasementScene":
        half_w = width / 2
        half_h = height / 2
        return IdealBasementScene(
            walls=(
                Wall(-half_w, -half_h, half_w, -half_h),
                Wall(half_w, -half_h, half_w, half_h),
                Wall(half_w, half_h, -half_w, half_h),
                Wall(-half_w, half_h, -half_w, -half_h),
            ),
            max_range=max_range,
        )

    def proximity_scan(self, pose: Pose2D, directions: list[float]) -> list[float]:
        return [
            min(
                (
                    distance
                    for wall in self.walls
                    for distance in [_ray_segment_distance(pose, pose.theta + direction, wall)]
                    if distance is not None
                ),
                default=self.max_range,
            )
            for direction in directions
        ]

    def move(self, pose: Pose2D, *, forward: float = 0.0, turn: float = 0.0) -> Pose2D:
        next_theta = pose.theta + turn
        return Pose2D(
            x=pose.x + math.cos(next_theta) * forward,
            y=pose.y + math.sin(next_theta) * forward,
            theta=next_theta,
        )

    def safe_move(
        self,
        pose: Pose2D,
        *,
        forward: float = 0.0,
        turn: float = 0.0,
        clearance: float = 0.05,
    ) -> tuple[Pose2D, SafeMoveResult]:
        """Move with collision avoidance.

        Applies turn first (rotation is always free in this 2D sim), then
        evaluates the forward leg. If the forward motion would cross any
        wall, truncates the motion to stop `clearance` short of the wall
        and reports the intervention. Reverse motion (forward < 0) and zero
        forward are passed through unchecked — only forward collisions are
        evaluated.

        Returns (final_pose, SafeMoveResult). The pose always reflects the
        applied motion; the result reports requested vs allowed and the
        nearest wall distance when intervention happened.
        """
        if clearance < 0:
            raise ValueError("clearance must be non-negative.")
        next_theta = pose.theta + turn

        if forward <= 0 or not self.walls:
            applied = self.move(pose, forward=forward, turn=turn)
            return applied, SafeMoveResult(
                intervened=False,
                requested_forward=forward,
                allowed_forward=forward,
                clearance=clearance,
            )

        rotated_pose = Pose2D(pose.x, pose.y, next_theta)
        wall_distances = [
            _ray_segment_distance(rotated_pose, next_theta, wall)
            for wall in self.walls
        ]
        valid = [d for d in wall_distances if d is not None and d >= 0]
        nearest_wall = min(valid) if valid else None

        if nearest_wall is None or nearest_wall >= forward + clearance:
            applied = self.move(pose, forward=forward, turn=turn)
            return applied, SafeMoveResult(
                intervened=False,
                requested_forward=forward,
                allowed_forward=forward,
                wall_distance=nearest_wall,
                clearance=clearance,
            )

        allowed = max(0.0, nearest_wall - clearance)
        applied = self.move(pose, forward=allowed, turn=turn)
        return applied, SafeMoveResult(
            intervened=True,
            requested_forward=forward,
            allowed_forward=allowed,
            wall_distance=nearest_wall,
            clearance=clearance,
        )


def _ray_segment_distance(pose: Pose2D, angle: float, wall: Wall) -> float | None:
    ray_dx = math.cos(angle)
    ray_dy = math.sin(angle)
    seg_dx = wall.x2 - wall.x1
    seg_dy = wall.y2 - wall.y1
    denom = ray_dx * seg_dy - ray_dy * seg_dx
    if abs(denom) < 1e-9:
        return None
    rel_x = wall.x1 - pose.x
    rel_y = wall.y1 - pose.y
    t = (rel_x * seg_dy - rel_y * seg_dx) / denom
    u = (rel_x * ray_dy - rel_y * ray_dx) / denom
    if t < 0 or not (0 <= u <= 1):
        return None
    return t

