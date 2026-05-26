from __future__ import annotations

import heapq
import json
import math
from dataclasses import asdict, dataclass

from ..mapping.occupancy import OccupancyGrid, Pose2D
from ..sim.ideal_basement import IdealBasementScene, Wall
from ..telemetry.sensor_stack import (
    SensorCommand,
    SensorKnobs,
    StackedSensor,
    scalar_snapshot,
)


DIRECTIONS = [
    0.0,
    math.pi / 4,
    math.pi / 2,
    3 * math.pi / 4,
    math.pi,
    -3 * math.pi / 4,
    -math.pi / 2,
    -math.pi / 4,
]


@dataclass(frozen=True)
class MazeWorld:
    scene: IdealBasementScene
    start: Pose2D
    goal: Pose2D
    route: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class MotionStep:
    before: Pose2D
    requested: float
    applied: float
    after: Pose2D
    event: str
    nearest_front: float

    def to_payload(self) -> dict:
        return asdict(self)


def make_maze_world() -> MazeWorld:
    walls = (
        Wall(-2.0, -2.0, 2.0, -2.0),
        Wall(2.0, -2.0, 2.0, 2.0),
        Wall(2.0, 2.0, -2.0, 2.0),
        Wall(-2.0, 2.0, -2.0, -2.0),
        Wall(-1.15, -2.0, -1.15, 0.95),
        Wall(-0.25, -0.95, -0.25, 2.0),
        Wall(0.75, -2.0, 0.75, 0.9),
        Wall(1.35, -0.25, 2.0, -0.25),
    )
    return MazeWorld(
        scene=IdealBasementScene(walls=walls, max_range=1.35),
        start=Pose2D(-1.65, -1.55, 0.0),
        goal=Pose2D(1.55, 1.55, 0.0),
        route=(
            (-1.65, -1.55),
            (-1.65, 1.45),
            (-0.7, 1.45),
            (-0.7, -1.45),
            (0.25, -1.45),
            (0.25, 1.45),
            (1.55, 1.45),
            (1.55, 1.55),
        ),
    )


def safe_forward(
    scene: IdealBasementScene,
    pose: Pose2D,
    requested: float,
    *,
    robot_radius: float = 0.18,
) -> MotionStep:
    after, safety = scene.safe_move(pose, forward=requested, clearance=robot_radius)
    applied = safety.allowed_forward
    if safety.intervened and applied <= 1e-9 and requested > 0:
        event = "blocked_before_wall_contact"
    elif safety.intervened:
        event = "truncated_before_wall_contact"
    else:
        event = "accepted"
    return MotionStep(
        before=pose,
        requested=requested,
        applied=applied,
        after=after,
        event=event,
        nearest_front=safety.wall_distance or scene.max_range,
    )


def face_point(pose: Pose2D, target: tuple[float, float]) -> Pose2D:
    return Pose2D(pose.x, pose.y, math.atan2(target[1] - pose.y, target[0] - pose.x))


def drive_route(world: MazeWorld, *, step_size: float = 0.2) -> list[MotionStep]:
    pose = world.start
    steps: list[MotionStep] = []
    for target in world.route[1:]:
        while math.hypot(target[0] - pose.x, target[1] - pose.y) > step_size / 2:
            pose = face_point(pose, target)
            requested = min(step_size, math.hypot(target[0] - pose.x, target[1] - pose.y))
            step = safe_forward(world.scene, pose, requested)
            steps.append(step)
            pose = step.after
            if step.applied <= 1e-9:
                break
    return steps


def build_map(world: MazeWorld, steps: list[MotionStep]) -> OccupancyGrid:
    grid = OccupancyGrid(width=45, height=45, resolution=0.1)
    poses = [world.start] + [step.after for step in steps]
    for pose in poses:
        distances = world.scene.proximity_scan(pose, DIRECTIONS)
        grid.apply_proximity_scan(pose, distances, DIRECTIONS, max_range=world.scene.max_range)
        grid.mark_world_cell(pose.x, pose.y, -1, "robot_pose_is_free")
    return grid


def world_to_cell(grid: OccupancyGrid, x: float, y: float) -> tuple[int, int]:
    return (
        int(round(x / grid.resolution + grid.width / 2)),
        int(round(y / grid.resolution + grid.height / 2)),
    )


def cell_to_world(grid: OccupancyGrid, cell: tuple[int, int]) -> tuple[float, float]:
    return (
        (cell[0] - grid.width / 2) * grid.resolution,
        (cell[1] - grid.height / 2) * grid.resolution,
    )


def solve_known_free_path(
    grid: OccupancyGrid,
    start: tuple[int, int],
    goal: tuple[int, int],
) -> list[tuple[int, int]]:
    open_heap: list[tuple[float, tuple[int, int]]] = [(0.0, start)]
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    cost_so_far = {start: 0.0}
    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            break
        for neighbor in _neighbors(current):
            x, y = neighbor
            if not (0 <= x < grid.width and 0 <= y < grid.height):
                continue
            if grid.values[y][x] == 1:
                continue
            if grid.values[y][x] == 0 and neighbor not in (start, goal):
                continue
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + abs(goal[0] - x) + abs(goal[1] - y)
                heapq.heappush(open_heap, (priority, neighbor))
                came_from[neighbor] = current
    if goal not in came_from:
        return []
    path = []
    current: tuple[int, int] | None = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def run_demo() -> dict:
    world = make_maze_world()
    unsafe_probe = safe_forward(
        world.scene,
        Pose2D(-1.55, 1.62, math.pi / 2),
        requested=0.6,
    )
    steps = drive_route(world)
    grid = build_map(world, steps)
    start_cell = world_to_cell(grid, world.start.x, world.start.y)
    goal_cell = world_to_cell(grid, world.goal.x, world.goal.y)
    grid.mark_world_cell(world.goal.x, world.goal.y, -1, "goal_pose_is_free")
    path = solve_known_free_path(grid, start_cell, goal_cell)
    counts = {
        "free": sum(1 for row in grid.values for value in row if value == -1),
        "occupied": sum(1 for row in grid.values for value in row if value == 1),
        "unknown": sum(1 for row in grid.values for value in row if value == 0),
    }
    telemetry_stack = build_telemetry_stack(unsafe_probe, counts, path)
    return {
        "world": {
            "start": asdict(world.start),
            "goal": asdict(world.goal),
            "walls": [asdict(wall) for wall in world.scene.walls],
        },
        "unsafe_probe": unsafe_probe.to_payload(),
        "steps": [step.to_payload() for step in steps],
        "grid": grid.to_rows(),
        "counts": counts,
        "start_cell": start_cell,
        "goal_cell": goal_cell,
        "path": path,
        "path_world": [cell_to_world(grid, cell) for cell in path],
        "path_crosses_occupied": any(grid.values[y][x] == 1 for x, y in path),
        "events": {
            "accepted": sum(1 for step in steps if step.event == "accepted"),
            "truncated": sum(1 for step in steps if step.event == "truncated_before_wall_contact"),
            "blocked": sum(1 for step in steps if step.event == "blocked_before_wall_contact"),
            "unsafe_probe": unsafe_probe.event,
        },
        "event_log": [
            _motion_event("unsafe_probe", unsafe_probe),
            *[_motion_event(f"route_step_{index}", step) for index, step in enumerate(steps)],
        ],
        "telemetry_stack": telemetry_stack,
    }


def _neighbors(cell: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    x, y = cell
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def build_telemetry_stack(
    unsafe_probe: MotionStep,
    counts: dict[str, int],
    path: list[tuple[int, int]],
) -> list[dict]:
    total_cells = sum(counts.values())
    coverage = counts["free"] / total_cells
    path_signal = min(1.0, len(path) / 120)
    clearance_signal = min(1.0, unsafe_probe.applied / max(unsafe_probe.requested, 1e-9))

    clearance_snapshot = scalar_snapshot(
        "front_clearance_sensor",
        "proximity_margin",
        clearance_signal,
        applied=unsafe_probe.applied,
        requested=unsafe_probe.requested,
    )
    map_snapshot = scalar_snapshot(
        "occupancy_coverage_sensor",
        "map_coverage",
        coverage,
        counts=counts,
    )
    path_snapshot = scalar_snapshot(
        "known_free_path_sensor",
        "path_confidence",
        path_signal,
        path_length=len(path),
    )

    navigability = StackedSensor(
        "maze_navigability_sensor",
        kind="stacked_sensor",
        knobs=SensorKnobs(alpha=0.35, lower_bound=0.0, upper_bound=1.0),
    )
    records = [
        clearance_snapshot.to_payload(),
        map_snapshot.to_payload(),
        path_snapshot.to_payload(),
        navigability.apply([clearance_snapshot, map_snapshot, path_snapshot]).to_payload(),
    ]
    for command in (
        SensorCommand("set_alpha", 0.65, "React faster while near maze walls."),
        SensorCommand("nudge_down", 0.08, "Tighten the acceptance band after a clipped motion."),
        SensorCommand("shrink_spread", 0.05, "Pay attention to a narrower navigability window."),
        SensorCommand("grow_spread", 0.1, "Relax after finding a known-free path."),
    ):
        records.append(navigability.execute(command).to_payload())
        records.append(navigability.apply([clearance_snapshot, map_snapshot, path_snapshot]).to_payload())
    return records


def _motion_event(name: str, step: MotionStep) -> dict:
    return {
        "kind": "simulated_motion",
        "name": name,
        "event": step.event,
        "requested": step.requested,
        "applied": step.applied,
        "nearest_front": step.nearest_front,
    }


def main() -> None:
    result = run_demo()
    print(
        json.dumps(
            {
                "unsafe_probe": result["unsafe_probe"],
                "counts": result["counts"],
                "events": result["events"],
                "path_length": len(result["path"]),
                "path_crosses_occupied": result["path_crosses_occupied"],
                "telemetry_stack_tail": result["telemetry_stack"][-4:],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
