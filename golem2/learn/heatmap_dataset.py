"""BFS-based ground-truth heatmap generator for navigation training.

The training paradigm: given a known occupancy grid + robot position + goal
position, the model should learn to predict a 3-channel heatmap encoding
"where to go" using the operator's r/g/b semantics:

  r ≤ 0 : negative evidence (don't go here)
  g ≥ 0 : positive evidence (do go here)
  b ±1  : deterministic balanced reference (per `_balanced_blue` shape)

For each cell:
  - occupied / unreachable: r=-1, g=0  (hard avoid)
  - reachable free: g = 1 - dist_to_goal / max_dist  (closer = higher g)
                    r = -(1 - g)                     (matching negative slope)
  - all cells: b in {-1, +1} from hash(cell coordinates)

BFS is 4-connected over free cells. Distance is hop count.
"""
from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass

import numpy as np

from ..sim.ideal_basement import IdealBasementScene, Wall


GRID_SIZE = 21  # 21x21 cells. Cell ~0.05 normalized units, MacBook-friendly.


@dataclass(frozen=True)
class NavExample:
    """One training example: state inputs → target heatmap."""
    occupancy: np.ndarray  # (H, W) int8 in {-1=free, 0=unknown, +1=occupied}
    robot_xy: tuple[float, float]  # normalized [0,1]
    goal_xy: tuple[float, float]   # normalized [0,1]
    heatmap: np.ndarray    # (3, H, W) float32, channels r/g/b


def _balanced_blue(cx: int, cy: int) -> float:
    """Matches the convention in vision/quantized_heatmap.py."""
    digest = hashlib.sha256(f"{cx}:{cy}".encode("utf-8")).digest()
    return 1.0 if digest[0] < 128 else -1.0


def _point_to_segment_distance(x: float, y: float, wall: Wall) -> float:
    """Min distance from point (x, y) to wall segment."""
    dx, dy = wall.x2 - wall.x1, wall.y2 - wall.y1
    if dx == 0 and dy == 0:
        return float(np.hypot(x - wall.x1, y - wall.y1))
    t = max(0.0, min(1.0, ((x - wall.x1) * dx + (y - wall.y1) * dy) / (dx * dx + dy * dy)))
    px = wall.x1 + t * dx
    py = wall.y1 + t * dy
    return float(np.hypot(x - px, y - py))


def build_occupancy(
    scene: IdealBasementScene,
    world_extent: float,
    grid_size: int = GRID_SIZE,
) -> np.ndarray:
    """Render the scene as a known-truth occupancy grid.

    Cell is occupied if any wall segment passes within (cell_size/2) of its
    center. `world_extent` is half the side length in world units (scene is
    `[-world_extent, +world_extent]^2`).
    """
    occupancy = np.zeros((grid_size, grid_size), dtype=np.int8)
    cell_size = 2 * world_extent / grid_size
    for cy in range(grid_size):
        for cx in range(grid_size):
            wx = -world_extent + (cx + 0.5) * cell_size
            wy = -world_extent + (cy + 0.5) * cell_size
            blocked = any(
                _point_to_segment_distance(wx, wy, wall) < cell_size / 2
                for wall in scene.walls
            )
            occupancy[cy, cx] = 1 if blocked else -1
    return occupancy


def bfs_distances(occupancy: np.ndarray, goal_cell: tuple[int, int]) -> dict[tuple[int, int], int]:
    """4-connected BFS from goal over free cells (value=-1). Returns hop count per reachable cell."""
    h, w = occupancy.shape
    gx, gy = goal_cell
    if not (0 <= gx < w and 0 <= gy < h):
        return {}
    if occupancy[gy, gx] != -1:
        return {}
    distances = {goal_cell: 0}
    queue: deque[tuple[int, int]] = deque([goal_cell])
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and occupancy[ny, nx] == -1 and (nx, ny) not in distances:
                distances[(nx, ny)] = distances[(cx, cy)] + 1
                queue.append((nx, ny))
    return distances


def make_target_heatmap(occupancy: np.ndarray, goal_cell: tuple[int, int]) -> np.ndarray:
    """Build the (3, H, W) target heatmap per the r/g/b semantic above."""
    h, w = occupancy.shape
    heatmap = np.zeros((3, h, w), dtype=np.float32)
    distances = bfs_distances(occupancy, goal_cell)
    max_dist = max(distances.values()) if distances else 1
    for cy in range(h):
        for cx in range(w):
            cell = (cx, cy)
            if occupancy[cy, cx] == 1:
                heatmap[0, cy, cx] = -1.0
                heatmap[1, cy, cx] = 0.0
            elif cell in distances:
                g = 1.0 - distances[cell] / max(1, max_dist)
                heatmap[0, cy, cx] = -(1.0 - g)
                heatmap[1, cy, cx] = g
            else:
                heatmap[0, cy, cx] = -1.0
                heatmap[1, cy, cx] = 0.0
            heatmap[2, cy, cx] = _balanced_blue(cx, cy)
    return heatmap


def cell_to_normalized(cx: int, cy: int, grid_size: int = GRID_SIZE) -> tuple[float, float]:
    """Map cell index to [0,1]^2 normalized coordinates (cell center)."""
    return ((cx + 0.5) / grid_size, (cy + 0.5) / grid_size)


def normalized_to_cell(nx: float, ny: float, grid_size: int = GRID_SIZE) -> tuple[int, int]:
    """Map normalized [0,1]^2 coordinates back to cell index, clipped."""
    cx = int(np.clip(nx * grid_size, 0, grid_size - 1))
    cy = int(np.clip(ny * grid_size, 0, grid_size - 1))
    return cx, cy


def generate_examples(
    scene: IdealBasementScene,
    world_extent: float,
    n: int = 100,
    seed: int = 0,
    grid_size: int = GRID_SIZE,
) -> list[NavExample]:
    """Sample n (robot, goal) pairs uniformly over free cells, build examples."""
    rng = np.random.default_rng(seed)
    occupancy = build_occupancy(scene, world_extent, grid_size=grid_size)
    free_cells = [(int(cx), int(cy)) for cy, cx in zip(*np.where(occupancy == -1))]
    if len(free_cells) < 2:
        raise ValueError(f"Scene has only {len(free_cells)} free cells; need at least 2.")
    examples = []
    while len(examples) < n:
        robot = free_cells[rng.integers(len(free_cells))]
        goal = free_cells[rng.integers(len(free_cells))]
        if robot == goal:
            continue
        robot_xy = cell_to_normalized(robot[0], robot[1], grid_size)
        goal_xy = cell_to_normalized(goal[0], goal[1], grid_size)
        heatmap = make_target_heatmap(occupancy, goal)
        examples.append(NavExample(
            occupancy=occupancy.copy(),
            robot_xy=robot_xy,
            goal_xy=goal_xy,
            heatmap=heatmap,
        ))
    return examples


def example_to_input_tensor(example: NavExample) -> np.ndarray:
    """Pack the (state) into a (5, H, W) tensor: occupancy + 4 broadcast scalars."""
    h, w = example.occupancy.shape
    tensor = np.zeros((5, h, w), dtype=np.float32)
    tensor[0] = example.occupancy.astype(np.float32)
    tensor[1] = example.robot_xy[0]
    tensor[2] = example.robot_xy[1]
    tensor[3] = example.goal_xy[0]
    tensor[4] = example.goal_xy[1]
    return tensor
