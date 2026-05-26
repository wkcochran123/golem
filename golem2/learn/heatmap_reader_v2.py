"""Heatmap reader v2: one-hot robot/goal input channels.

The v1 reader (golem2.learn.heatmap_reader.HeatmapReaderCNN) encodes the
robot and goal positions as broadcast scalar channels — every cell sees
the same ``rx_norm`` value. That gives the conv stack no per-cell info
about where the robot actually is, so the model has to learn to decode
broadcast scalars through receptive-field arithmetic. On 500 training
examples (the bootstrap lane) this generalises poorly: the 8-neighbor
argmax CE goes to 0.33 on train but stays at 1.82 (≈ uniform log(8))
on the held-out test set.

v2 swaps the encoding for **3 channels**:

- channel 0: occupancy (same as v1 channel 0)
- channel 1: robot one-hot map (1.0 at robot cell, 0.0 elsewhere)
- channel 2: goal  one-hot map (1.0 at goal cell, 0.0 elsewhere)

Each cell now sees a direct signal about whether it's the robot, the
goal, or neither. The conv stack can build the distance field directly
from these locality markers without learning to decode broadcast values.

Output head is the same sign-constrained 3-channel r/g/b heatmap as v1.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from .heatmap_dataset import GRID_SIZE, NavExample, normalized_to_cell


class HeatmapReaderCNNv2(nn.Module):
    """Same CNN as v1 but with a 3-channel one-hot input instead of 5-channel broadcast.

    Five conv layers (32 → 64 → 64 → 64 → 32) + 1x1 head. ~112k params.
    """

    def __init__(self, grid_size: int = GRID_SIZE):
        super().__init__()
        self.grid_size = grid_size
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
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
        # Smooth sign constraints avoid the dead-head failure mode where a
        # hard ReLU output starts on the wrong side and receives no gradient.
        r = -F.softplus(x[:, 0:1])
        g = F.softplus(x[:, 1:2])
        b = torch.tanh(x[:, 2:3])
        return torch.cat([r, g, b], dim=1)

    def predict(self, state: np.ndarray, device: str = "cpu") -> np.ndarray:
        self.eval()
        with torch.no_grad():
            x = torch.from_numpy(state).unsqueeze(0).to(device)
            y = self.forward(x)
            return y.squeeze(0).cpu().numpy()


def example_to_onehot_input(example: NavExample, grid_size: int = GRID_SIZE) -> np.ndarray:
    """Pack an example into the v2 3-channel one-hot input tensor."""
    h, w = example.occupancy.shape
    tensor = np.zeros((3, h, w), dtype=np.float32)
    tensor[0] = example.occupancy.astype(np.float32)
    rx, ry = normalized_to_cell(example.robot_xy[0], example.robot_xy[1], grid_size)
    gx, gy = normalized_to_cell(example.goal_xy[0], example.goal_xy[1], grid_size)
    tensor[1, ry, rx] = 1.0
    tensor[2, gy, gx] = 1.0
    return tensor


def state_to_onehot_input(
    occupancy: np.ndarray,
    robot_xy_norm: tuple[float, float],
    goal_xy_norm: tuple[float, float],
    grid_size: int = GRID_SIZE,
) -> np.ndarray:
    """Build a v2 3-channel input from raw state (for navigation rollouts)."""
    h, w = occupancy.shape
    tensor = np.zeros((3, h, w), dtype=np.float32)
    tensor[0] = occupancy.astype(np.float32)
    rx, ry = normalized_to_cell(robot_xy_norm[0], robot_xy_norm[1], grid_size)
    gx, gy = normalized_to_cell(goal_xy_norm[0], goal_xy_norm[1], grid_size)
    tensor[1, ry, rx] = 1.0
    tensor[2, gy, gx] = 1.0
    return tensor
