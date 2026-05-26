"""End-to-end demo: train the heatmap reader, then use it to navigate the maze.

Run with anaconda Python (the env that has torch):

    /opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_navigate_demo

What it does:
  1. Generate a maze scene (reused from maze_navigation_demo).
  2. Build a dataset of (state, target_heatmap) pairs via BFS ground truth.
  3. Train the tiny CNN for a handful of epochs.
  4. Pick a fresh (robot, goal) pair, navigate using the trained model.
  5. Report training loss curve + navigation success per held-out test pair.

The model uses no real LLM call; this is the supervised-pretrain step from
the design doc's training schedule. Online correction / sleep replay land in
later lanes.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset

from ..learn.heatmap_dataset import (
    GRID_SIZE,
    NavExample,
    cell_to_normalized,
    example_to_input_tensor,
    generate_examples,
    normalized_to_cell,
)
from ..learn.heatmap_reader import HeatmapReaderCNN, pick_action
from ..mapping.occupancy import Pose2D
from ..sim.ideal_basement import IdealBasementScene, Wall


WORLD_EXTENT = 2.0  # scene is [-2, +2]^2 = 4x4 m


def _maze_scene() -> IdealBasementScene:
    """Maze geometry similar to maze_navigation_demo.make_maze_world but
    smaller-wall-count for faster ground-truth generation."""
    walls = (
        Wall(-2.0, -2.0, 2.0, -2.0),
        Wall(2.0, -2.0, 2.0, 2.0),
        Wall(2.0, 2.0, -2.0, 2.0),
        Wall(-2.0, 2.0, -2.0, -2.0),
        Wall(-1.0, -2.0, -1.0, 0.8),     # vertical interior wall 1
        Wall(0.0, -0.8, 0.0, 2.0),       # vertical interior wall 2
        Wall(1.0, -2.0, 1.0, 0.4),       # vertical interior wall 3
    )
    return IdealBasementScene(walls=walls, max_range=1.5)


def _pack_dataset(examples: list[NavExample]) -> tuple[torch.Tensor, torch.Tensor]:
    inputs = np.stack([example_to_input_tensor(ex) for ex in examples])
    targets = np.stack([ex.heatmap for ex in examples])
    return (
        torch.from_numpy(inputs).float(),
        torch.from_numpy(targets).float(),
    )


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _norm_to_world(nx: float, ny: float) -> tuple[float, float]:
    """Map normalized [0,1]^2 back to world [-WORLD_EXTENT, +WORLD_EXTENT]^2."""
    return (
        -WORLD_EXTENT + nx * 2 * WORLD_EXTENT,
        -WORLD_EXTENT + ny * 2 * WORLD_EXTENT,
    )


def _world_to_norm(wx: float, wy: float) -> tuple[float, float]:
    return (
        (wx + WORLD_EXTENT) / (2 * WORLD_EXTENT),
        (wy + WORLD_EXTENT) / (2 * WORLD_EXTENT),
    )


def navigate(
    scene: IdealBasementScene,
    model: HeatmapReaderCNN,
    occupancy: np.ndarray,
    start_xy_norm: tuple[float, float],
    goal_xy_norm: tuple[float, float],
    *,
    max_steps: int = 80,
    goal_radius_norm: float = 0.05,
    step_norm: float = 1.0 / GRID_SIZE,
    device: str = "cpu",
) -> dict:
    """Walk the trained model around the scene from start to goal."""
    robot_world = Pose2D(*_norm_to_world(*start_xy_norm), 0.0)
    goal_world = _norm_to_world(*goal_xy_norm)
    trajectory = [{"x": robot_world.x, "y": robot_world.y, "theta": robot_world.theta}]
    interventions = 0
    steps_taken = 0
    reached = False

    for _ in range(max_steps):
        rx_norm, ry_norm = _world_to_norm(robot_world.x, robot_world.y)
        if math.hypot(rx_norm - goal_xy_norm[0], ry_norm - goal_xy_norm[1]) <= goal_radius_norm:
            reached = True
            break

        state = np.zeros((5, *occupancy.shape), dtype=np.float32)
        state[0] = occupancy.astype(np.float32)
        state[1] = rx_norm
        state[2] = ry_norm
        state[3] = goal_xy_norm[0]
        state[4] = goal_xy_norm[1]
        heatmap = model.predict(state, device=device)

        action = pick_action(heatmap, (rx_norm, ry_norm), grid_size=GRID_SIZE)
        target_wx, target_wy = _norm_to_world(*action.target_xy_norm)
        dx = target_wx - robot_world.x
        dy = target_wy - robot_world.y
        forward = math.hypot(dx, dy)
        if forward < 1e-6:
            # Stuck (no better neighbor). Break to avoid loop.
            break
        turn = math.atan2(dy, dx) - robot_world.theta
        new_pose, safety = scene.safe_move(robot_world, forward=forward, turn=turn, clearance=0.05)
        robot_world = new_pose
        steps_taken += 1
        if safety.intervened:
            interventions += 1
        trajectory.append({"x": robot_world.x, "y": robot_world.y, "theta": robot_world.theta})

    return {
        "start_norm": list(start_xy_norm),
        "goal_norm": list(goal_xy_norm),
        "reached": reached,
        "steps": steps_taken,
        "interventions": interventions,
        "final_pose": trajectory[-1],
        "final_distance_to_goal_norm": float(math.hypot(
            _world_to_norm(robot_world.x, robot_world.y)[0] - goal_xy_norm[0],
            _world_to_norm(robot_world.x, robot_world.y)[1] - goal_xy_norm[1],
        )),
    }


def main() -> None:
    device = _device()
    scene = _maze_scene()

    train_examples = generate_examples(scene, WORLD_EXTENT, n=500, seed=0)
    test_examples = generate_examples(scene, WORLD_EXTENT, n=30, seed=42)

    train_x, train_y = _pack_dataset(train_examples)
    test_x, test_y = _pack_dataset(test_examples)

    model = HeatmapReaderCNN(grid_size=GRID_SIZE).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    def navigation_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        # Weight r and g (the navigation signal), skip b (noise reference).
        return ((pred[:, :2] - target[:, :2]) ** 2).mean()

    loader = DataLoader(TensorDataset(train_x, train_y), batch_size=32, shuffle=True)
    losses_per_epoch = []
    epochs = 60
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad()
            pred = model(batch_x)
            loss = navigation_loss(pred, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            n_batches += 1
        losses_per_epoch.append(epoch_loss / max(1, n_batches))

    # Test set MSE on held-out examples
    model.eval()
    with torch.no_grad():
        test_pred = model(test_x.to(device))
        test_loss = float(navigation_loss(test_pred, test_y.to(device)).item())

    # Navigation rollouts on the test set
    occupancy = train_examples[0].occupancy  # all examples share the same scene
    nav_results = []
    for ex in test_examples[:10]:
        result = navigate(
            scene=scene,
            model=model,
            occupancy=occupancy,
            start_xy_norm=ex.robot_xy,
            goal_xy_norm=ex.goal_xy,
            device=device,
        )
        nav_results.append(result)

    success_rate = sum(1 for r in nav_results if r["reached"]) / len(nav_results)
    avg_steps = sum(r["steps"] for r in nav_results) / len(nav_results)
    avg_interventions = sum(r["interventions"] for r in nav_results) / len(nav_results)

    summary = {
        "device": device,
        "grid_size": GRID_SIZE,
        "model_params": sum(p.numel() for p in model.parameters()),
        "train_examples": len(train_examples),
        "test_examples": len(test_examples),
        "epochs": epochs,
        "train_loss_first": losses_per_epoch[0],
        "train_loss_last": losses_per_epoch[-1],
        "train_loss_curve": losses_per_epoch,
        "test_loss": test_loss,
        "navigation": {
            "rollouts": len(nav_results),
            "success_rate": success_rate,
            "avg_steps": avg_steps,
            "avg_interventions": avg_interventions,
            "per_rollout": nav_results,
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
