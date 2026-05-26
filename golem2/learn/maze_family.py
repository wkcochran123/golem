"""Random maze family generator for multi-scene heatmap training.

The single-scene v1/v2 heatmap reader plateaus at ~5/10 navigation success
because 500-2000 examples on one maze layout teach the model the *specific*
wall positions, not the underlying path-planning rule. Multi-scene training
forces the conv stack to generalise: occupancy is a per-cell input channel,
so the model has to read the maze and plan.

This module exposes ``random_maze_scene(seed)`` that builds a
``IdealBasementScene`` with:

- a fixed 4x4 outer box at ``±world_extent`` (same room footprint);
- 2-4 axis-aligned interior wall segments at random positions, each
  spanning a random fraction of the room and offset to one side.

Each ``seed`` yields a deterministic, distinct maze. Two scenes from
different seeds will typically have different interior wall counts,
orientations, and positions.
"""
from __future__ import annotations

import random

from ..sim.ideal_basement import IdealBasementScene, Wall


def _outer_box(world_extent: float) -> tuple[Wall, ...]:
    return (
        Wall(-world_extent, -world_extent, world_extent, -world_extent),  # bottom
        Wall(world_extent, -world_extent, world_extent, world_extent),    # right
        Wall(world_extent, world_extent, -world_extent, world_extent),    # top
        Wall(-world_extent, world_extent, -world_extent, -world_extent),  # left
    )


def random_maze_scene(
    seed: int,
    *,
    world_extent: float = 2.0,
    min_interior_walls: int = 2,
    max_interior_walls: int = 4,
    max_range: float = 1.5,
) -> IdealBasementScene:
    """Build a deterministic random maze scene from a seed.

    Outer box is fixed. Interior walls are axis-aligned, each a single
    straight segment. Wall placement is biased so segments touch one edge
    of the room (so a single wall actually blocks part of the room rather
    than floating in the middle).
    """
    rng = random.Random(seed)
    walls: list[Wall] = list(_outer_box(world_extent))
    n_interior = rng.randint(min_interior_walls, max_interior_walls)
    for _ in range(n_interior):
        # Vertical (constant x) or horizontal (constant y)
        vertical = rng.random() < 0.5
        # Position along the axis it spans (avoid being right on the boundary)
        margin = 0.4
        position = rng.uniform(-world_extent + margin, world_extent - margin)
        # Length: 30%-80% of room side
        length = rng.uniform(0.3, 0.8) * (2 * world_extent)
        # Which edge the wall touches (so it's not free-floating)
        anchor_low = rng.random() < 0.5
        if vertical:
            x = position
            if anchor_low:
                y1 = -world_extent
                y2 = -world_extent + length
            else:
                y1 = world_extent
                y2 = world_extent - length
            walls.append(Wall(x, y1, x, y2))
        else:
            y = position
            if anchor_low:
                x1 = -world_extent
                x2 = -world_extent + length
            else:
                x1 = world_extent
                x2 = world_extent - length
            walls.append(Wall(x1, y, x2, y))
    return IdealBasementScene(walls=tuple(walls), max_range=max_range)


def maze_family(
    n: int,
    *,
    seed_offset: int = 0,
    world_extent: float = 2.0,
) -> list[IdealBasementScene]:
    """Build a list of ``n`` distinct maze scenes seeded ``seed_offset + i``."""
    return [
        random_maze_scene(seed_offset + i, world_extent=world_extent)
        for i in range(n)
    ]
