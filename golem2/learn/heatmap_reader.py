"""Tiny CNN heatmap reader + hand-coded action selector.

The model takes a (5, H, W) state tensor (occupancy + broadcast robot_xy and
goal_xy) and predicts a (3, H, W) r/g/b heatmap.

The action selector is NOT learned. Given a predicted heatmap and the robot's
current normalized position, it picks the next world-coordinate target by
reading the heatmap gradient — pick the neighbor cell with the best score
(g - |r|, with the b channel weighted to zero).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn

from .heatmap_dataset import GRID_SIZE, normalized_to_cell


class HeatmapReaderCNN(nn.Module):
    """Small CNN: 5 input channels → 3 output channels, same spatial dims.

    Three conv layers (16, 32, 32 filters) + 1x1 conv head. Total params ~15k.
    Designed to fit in MacBook memory and train in seconds per epoch.
    """

    def __init__(self, grid_size: int = GRID_SIZE):
        super().__init__()
        self.grid_size = grid_size
        # 5 conv layers with growing receptive field — distance-to-goal is a
        # long-range signal, needs multi-cell context.
        self.conv1 = nn.Conv2d(5, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv5 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
        self.head = nn.Conv2d(32, 3, kernel_size=1)
        self.act = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.act(self.conv1(x))
        x = self.act(self.conv2(x))
        x = self.act(self.conv3(x))
        x = self.act(self.conv4(x))
        x = self.act(self.conv5(x))
        x = self.head(x)
        # r and g have specific signs; clamp via tanh-like rescaling.
        # Channel 0 (r) ≤ 0; channel 1 (g) ≥ 0; channel 2 (b) ∈ [-1, +1].
        r = -torch.relu(-x[:, 0:1])  # negative side only
        g = torch.relu(x[:, 1:2])    # positive side only
        b = torch.tanh(x[:, 2:3])    # bounded
        return torch.cat([r, g, b], dim=1)

    def predict(self, state: np.ndarray, device: str = "cpu") -> np.ndarray:
        """Single-example inference. state: (5, H, W) numpy → (3, H, W) numpy."""
        self.eval()
        with torch.no_grad():
            x = torch.from_numpy(state).unsqueeze(0).to(device)
            y = self.forward(x)
            return y.squeeze(0).cpu().numpy()


@dataclass(frozen=True)
class ActionPick:
    """One action choice from reading the heatmap."""
    target_cell: tuple[int, int]
    target_xy_norm: tuple[float, float]
    score: float
    robot_cell: tuple[int, int]


def pick_action(
    heatmap: np.ndarray,
    robot_xy_norm: tuple[float, float],
    *,
    grid_size: int = GRID_SIZE,
) -> ActionPick:
    """Read the heatmap and pick the best 8-neighbor cell from the robot's position.

    Score = g - |r| (b channel ignored — it's the noise floor, not signal).
    Returns the chosen cell + its normalized coords + the score.
    """
    robot_cell = normalized_to_cell(robot_xy_norm[0], robot_xy_norm[1], grid_size)
    rx, ry = robot_cell

    best_cell = robot_cell
    best_score = float("-inf")
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = rx + dx, ry + dy
            if not (0 <= nx < grid_size and 0 <= ny < grid_size):
                continue
            r = float(heatmap[0, ny, nx])
            g = float(heatmap[1, ny, nx])
            score = g - abs(r)
            if score > best_score:
                best_score = score
                best_cell = (nx, ny)

    nx_norm, ny_norm = (
        (best_cell[0] + 0.5) / grid_size,
        (best_cell[1] + 0.5) / grid_size,
    )
    return ActionPick(
        target_cell=best_cell,
        target_xy_norm=(nx_norm, ny_norm),
        score=best_score,
        robot_cell=robot_cell,
    )
