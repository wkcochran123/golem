"""Heatmap reader training across a maze family (multi-scene).

Sibling lane to ``heatmap_train_local_loss_demo``. Same v2 one-hot encoding
and combined value+local+CE loss, but the dataset is sampled across many
distinct maze layouts instead of just one. Hypothesis: single-scene
training plateaus at 5/10 because the model has memorised the specific
wall layout; multi-scene training forces it to read the occupancy channel
and *plan*, generalising both in-distribution (new robot/goal in trained
mazes) and out-of-distribution (entirely unseen mazes).

Run:
    /opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_multi_scene_demo
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
from ..learn.maze_family import maze_family
from ..mapping.occupancy import Pose2D
from ..sim.ideal_basement import IdealBasementScene


WORLD_EXTENT = 2.0


def _device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


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


def _pack(examples: list[NavExample]):
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
    robot_world = Pose2D(*_norm_to_world(*start_xy_norm), 0.0)
    interventions = 0
    steps_taken = 0
    reached = False

    for _ in range(max_steps):
        rx_norm, ry_norm = _world_to_norm(robot_world.x, robot_world.y)
        if math.hypot(rx_norm - goal_xy_norm[0], ry_norm - goal_xy_norm[1]) <= goal_radius_norm:
            reached = True
            break
        state = state_to_onehot_input(occupancy, (rx_norm, ry_norm), goal_xy_norm, GRID_SIZE)
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
        "reached": reached,
        "steps": steps_taken,
        "interventions": interventions,
        "final_distance_to_goal_norm": float(math.hypot(
            _world_to_norm(robot_world.x, robot_world.y)[0] - goal_xy_norm[0],
            _world_to_norm(robot_world.x, robot_world.y)[1] - goal_xy_norm[1],
        )),
    }


def _gather_examples_per_scene(
    scenes: list[IdealBasementScene],
    examples_per_scene: int,
    seed_base: int,
) -> list[NavExample]:
    """Loop over scenes, generating ``examples_per_scene`` (robot, goal) pairs each."""
    all_examples: list[NavExample] = []
    for i, scene in enumerate(scenes):
        # Different per-scene seed so the same (scene, i) is reproducible
        examples = generate_examples(scene, WORLD_EXTENT, n=examples_per_scene, seed=seed_base + i)
        all_examples.extend(examples)
    return all_examples


def main() -> None:
    device = _device()
    # Fixed seed for reproducibility — the OOD/IID success rates jitter
    # 25-35% across random inits otherwise. With a fixed seed both this
    # script and codex's audit run can land on the same number.
    torch.manual_seed(0)

    # Multi-scene split: 50 train mazes × 40 pairs = 2000 train examples;
    # 10 held-out mazes × 4 pairs = 40 held-out (scene, pair) examples for
    # OOD navigation. Plus 10 IID rollouts on a re-sampled (scene, pair)
    # from the train scene family.
    n_train_scenes = 100
    n_test_scenes = 10
    examples_per_train_scene = 60
    examples_per_test_scene = 4

    train_scenes = maze_family(n_train_scenes, seed_offset=0)
    test_scenes = maze_family(n_test_scenes, seed_offset=10_000)  # disjoint seeds

    train_examples = _gather_examples_per_scene(train_scenes, examples_per_train_scene, seed_base=1000)
    test_examples = _gather_examples_per_scene(test_scenes, examples_per_test_scene, seed_base=2000)
    # Also generate IID held-out pairs from the train scenes (different seed)
    iid_eval_examples = _gather_examples_per_scene(
        train_scenes[:10], 2, seed_base=3000
    )

    train_x, train_y, train_rx, train_ry = _pack(train_examples)
    test_x, test_y, test_rx, test_ry = _pack(test_examples)

    model = HeatmapReaderCNNv2(grid_size=GRID_SIZE).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    lambdas = {"value": 1.0, "local": 3.0, "ce": 1.0, "sigma_cells": 2.0}

    loader = DataLoader(
        TensorDataset(train_x, train_y, train_rx, train_ry),
        batch_size=64,
        shuffle=True,
    )
    epochs = 100
    last_parts: dict[str, float] = {}
    epoch_log: list[dict[str, float]] = []
    for epoch in range(epochs):
        model.train()
        ep_total = ep_value = ep_local = ep_ce = 0.0
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
            ep_total += parts["total"]
            ep_value += parts["value_mse"]
            ep_local += parts["local_weighted_mse"]
            ep_ce += parts["neighbor_argmax_ce"]
            n_batches += 1
        denom = max(1, n_batches)
        last_parts = {
            "total": ep_total / denom,
            "value_mse": ep_value / denom,
            "local_weighted_mse": ep_local / denom,
            "neighbor_argmax_ce": ep_ce / denom,
        }
        epoch_log.append(last_parts)

    # Held-out scene eval (OOD)
    model.eval()
    with torch.no_grad():
        test_pred = model(test_x.to(device))
        test_value = float(value_mse(test_pred, test_y.to(device)).item())
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

    # Navigation rollouts: OOD (held-out scenes)
    ood_results = []
    for ex, scene in [
        (ex, test_scenes[i // examples_per_test_scene])
        for i, ex in enumerate(test_examples)
    ]:
        result = navigate_v2(
            scene=scene,
            model=model,
            occupancy=ex.occupancy,
            start_xy_norm=ex.robot_xy,
            goal_xy_norm=ex.goal_xy,
            device=device,
        )
        ood_results.append(result)

    # Navigation rollouts: IID (train scenes, fresh pairs)
    iid_results = []
    for ex, scene in [
        (ex, train_scenes[i // 2]) for i, ex in enumerate(iid_eval_examples)
    ]:
        result = navigate_v2(
            scene=scene,
            model=model,
            occupancy=ex.occupancy,
            start_xy_norm=ex.robot_xy,
            goal_xy_norm=ex.goal_xy,
            device=device,
        )
        iid_results.append(result)

    ood_success = sum(1 for r in ood_results if r["reached"]) / max(1, len(ood_results))
    iid_success = sum(1 for r in iid_results if r["reached"]) / max(1, len(iid_results))

    summary = {
        "model": "HeatmapReaderCNNv2",
        "loss_kind": "value+local_weighted+neighbor_argmax_ce",
        "lambdas": lambdas,
        "device": device,
        "grid_size": GRID_SIZE,
        "model_params": sum(p.numel() for p in model.parameters()),
        "n_train_scenes": n_train_scenes,
        "n_test_scenes": n_test_scenes,
        "train_examples": len(train_examples),
        "test_examples": len(test_examples),
        "iid_eval_examples": len(iid_eval_examples),
        "epochs": epochs,
        "train_loss_first": epoch_log[0]["total"],
        "train_loss_last": epoch_log[-1]["total"],
        "train_loss_last_parts": last_parts,
        "test_value_mse_rg": test_value,
        "test_combined_parts": test_parts,
        "navigation_ood": {
            "rollouts": len(ood_results),
            "success_rate": ood_success,
            "per_rollout_reached_steps": [(r["reached"], r["steps"]) for r in ood_results],
        },
        "navigation_iid": {
            "rollouts": len(iid_results),
            "success_rate": iid_success,
            "per_rollout_reached_steps": [(r["reached"], r["steps"]) for r in iid_results],
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
