"""Heatmap reader training with v2 one-hot input + local-aware loss.

Sibling lane to ``heatmap_train_navigate_demo`` (the supervised bootstrap):

  - swaps the v1 broadcast-scalar 5-channel input for the v2 one-hot
    3-channel encoding (occupancy + robot one-hot + goal one-hot) — see
    ``golem2.learn.heatmap_reader_v2``;
  - swaps the naive MSE loss for the combined value + robot-local-
    weighted MSE + 8-neighbor argmax CE loss in ``golem2.learn.losses``.

The bootstrap lane converged to test_value_mse ≈ 0.002 with 0/10
navigation success because (a) the model couldn't get a sharp 8-neighbor
ranking from broadcast scalar encoding, and (b) the action selector
reads only those 8 cells. v2 + local-aware loss directly attacks both.

Run:
    /opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_local_loss_demo
"""
from __future__ import annotations

import json
import math

import numpy as np
import torch
from torch import optim
from torch.utils.data import DataLoader, TensorDataset

from ..learn.heatmap_dataset import (
    GRID_SIZE,
    NavExample,
    generate_examples,
    normalized_to_cell,
)
from ..learn.heatmap_reader import pick_action
from ..learn.heatmap_reader_v2 import (
    HeatmapReaderCNNv2,
    example_to_onehot_input,
    state_to_onehot_input,
)
from ..learn.losses import combined_navigation_loss, value_mse
from ..mapping.occupancy import Pose2D
from ..sim.ideal_basement import IdealBasementScene
from .heatmap_train_navigate_demo import WORLD_EXTENT, _device, _maze_scene


def _pack_dataset(
    examples: list[NavExample],
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    inputs = np.stack([example_to_onehot_input(ex) for ex in examples])
    targets = np.stack([ex.heatmap for ex in examples])
    robot_cells = [
        normalized_to_cell(ex.robot_xy[0], ex.robot_xy[1], GRID_SIZE) for ex in examples
    ]
    rx = torch.tensor([c[0] for c in robot_cells], dtype=torch.long)
    ry = torch.tensor([c[1] for c in robot_cells], dtype=torch.long)
    return (
        torch.from_numpy(inputs).float(),
        torch.from_numpy(targets).float(),
        rx,
        ry,
    )


def _norm_to_world(nx: float, ny: float) -> tuple[float, float]:
    return (
        -WORLD_EXTENT + nx * 2 * WORLD_EXTENT,
        -WORLD_EXTENT + ny * 2 * WORLD_EXTENT,
    )


def _world_to_norm(wx: float, wy: float) -> tuple[float, float]:
    return (
        (wx + WORLD_EXTENT) / (2 * WORLD_EXTENT),
        (wy + WORLD_EXTENT) / (2 * WORLD_EXTENT),
    )


def navigate_v2(
    scene: IdealBasementScene,
    model: HeatmapReaderCNNv2,
    occupancy: np.ndarray,
    start_xy_norm: tuple[float, float],
    goal_xy_norm: tuple[float, float],
    *,
    max_steps: int = 80,
    goal_radius_norm: float = 0.05,
    device: str = "cpu",
) -> dict:
    """Navigate using the v2 one-hot encoding."""
    robot_world = Pose2D(*_norm_to_world(*start_xy_norm), 0.0)
    interventions = 0
    steps_taken = 0
    reached = False

    for _ in range(max_steps):
        rx_norm, ry_norm = _world_to_norm(robot_world.x, robot_world.y)
        if math.hypot(rx_norm - goal_xy_norm[0], ry_norm - goal_xy_norm[1]) <= goal_radius_norm:
            reached = True
            break

        state = state_to_onehot_input(
            occupancy, (rx_norm, ry_norm), goal_xy_norm, GRID_SIZE
        )
        heatmap = model.predict(state, device=device)

        action = pick_action(heatmap, (rx_norm, ry_norm), grid_size=GRID_SIZE)
        target_wx, target_wy = _norm_to_world(*action.target_xy_norm)
        dx = target_wx - robot_world.x
        dy = target_wy - robot_world.y
        forward = math.hypot(dx, dy)
        if forward < 1e-6:
            break
        turn = math.atan2(dy, dx) - robot_world.theta
        new_pose, safety = scene.safe_move(robot_world, forward=forward, turn=turn, clearance=0.05)
        robot_world = new_pose
        steps_taken += 1
        if safety.intervened:
            interventions += 1

    return {
        "start_norm": list(start_xy_norm),
        "goal_norm": list(goal_xy_norm),
        "reached": reached,
        "steps": steps_taken,
        "interventions": interventions,
        "final_distance_to_goal_norm": float(math.hypot(
            _world_to_norm(robot_world.x, robot_world.y)[0] - goal_xy_norm[0],
            _world_to_norm(robot_world.x, robot_world.y)[1] - goal_xy_norm[1],
        )),
    }


def main() -> None:
    torch.manual_seed(0)
    np.random.seed(0)
    device = _device()
    scene = _maze_scene()

    train_examples = generate_examples(scene, WORLD_EXTENT, n=2000, seed=0)
    test_examples = generate_examples(scene, WORLD_EXTENT, n=30, seed=42)

    train_x, train_y, train_rx, train_ry = _pack_dataset(train_examples)
    test_x, test_y, test_rx, test_ry = _pack_dataset(test_examples)

    model = HeatmapReaderCNNv2(grid_size=GRID_SIZE).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    lambdas = {"value": 1.0, "local": 3.0, "ce": 1.0, "sigma_cells": 2.0}

    loader = DataLoader(
        TensorDataset(train_x, train_y, train_rx, train_ry),
        batch_size=32,
        shuffle=True,
    )
    epochs = 150
    epoch_summaries = []
    last_parts: dict[str, float] = {}
    for epoch in range(epochs):
        model.train()
        epoch_total = 0.0
        epoch_value = 0.0
        epoch_local = 0.0
        epoch_ce = 0.0
        n_batches = 0
        for batch_x, batch_y, batch_rx, batch_ry in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            batch_rx = batch_rx.to(device)
            batch_ry = batch_ry.to(device)
            optimizer.zero_grad()
            pred = model(batch_x)
            loss, parts = combined_navigation_loss(
                pred,
                batch_y,
                batch_rx,
                batch_ry,
                GRID_SIZE,
                lambda_value=lambdas["value"],
                lambda_local=lambdas["local"],
                lambda_ce=lambdas["ce"],
                sigma_cells=lambdas["sigma_cells"],
            )
            loss.backward()
            optimizer.step()
            epoch_total += parts["total"]
            epoch_value += parts["value_mse"]
            epoch_local += parts["local_weighted_mse"]
            epoch_ce += parts["neighbor_argmax_ce"]
            n_batches += 1
        denom = max(1, n_batches)
        last_parts = {
            "total": epoch_total / denom,
            "value_mse": epoch_value / denom,
            "local_weighted_mse": epoch_local / denom,
            "neighbor_argmax_ce": epoch_ce / denom,
        }
        epoch_summaries.append(last_parts)

    model.eval()
    with torch.no_grad():
        test_pred = model(test_x.to(device))
        test_value_mse = float(value_mse(test_pred, test_y.to(device)).item())
        _, test_parts = combined_navigation_loss(
            test_pred,
            test_y.to(device),
            test_rx.to(device),
            test_ry.to(device),
            GRID_SIZE,
            lambda_value=lambdas["value"],
            lambda_local=lambdas["local"],
            lambda_ce=lambdas["ce"],
            sigma_cells=lambdas["sigma_cells"],
        )

    occupancy = train_examples[0].occupancy
    nav_results = []
    for ex in test_examples[:10]:
        result = navigate_v2(
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
        "model": "HeatmapReaderCNNv2 (one-hot robot+goal channels)",
        "loss_kind": "value+local_weighted+neighbor_argmax_ce",
        "lambdas": lambdas,
        "device": device,
        "grid_size": GRID_SIZE,
        "model_params": sum(p.numel() for p in model.parameters()),
        "train_examples": len(train_examples),
        "test_examples": len(test_examples),
        "epochs": epochs,
        "train_loss_first_total": epoch_summaries[0]["total"],
        "train_loss_last_total": epoch_summaries[-1]["total"],
        "train_loss_last_parts": last_parts,
        "test_value_mse_rg": test_value_mse,
        "test_combined_parts": test_parts,
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
