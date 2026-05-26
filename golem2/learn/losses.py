"""Navigation-aware losses for the heatmap reader.

The naive MSE over the full 441-cell grid converges to tiny global error
(test loss 0.002) but leaves the 8-neighbor argmax noisy — the action
selector then picks the wrong neighbor and navigation success collapses
(0/10 in claude's run, 1/10 in codex's audit run).

These losses combat that with three terms, all defined over the r and g
channels only (the b channel is the noise floor):

  1. ``value_mse`` — plain MSE on r,g. Keeps global shape close to truth.

  2. ``local_weighted_mse`` — Gaussian-weighted MSE centered on each
     example's robot cell. Multiplies per-cell error by an N(robot,
     sigma_cells) bump so the cells the action selector actually reads
     dominate the gradient signal.

  3. ``neighbor_argmax_ce`` — cross-entropy over the 8-neighbor ring of
     scores (``g - |r|``). The target is the argmax of the *ground-truth*
     score field over the same 8 cells. This directly trains "rank the
     8 neighbors correctly", which is what the hand-coded action selector
     reads. Out-of-bounds neighbors (robot on grid border) are masked
     with ``-inf`` in both pred and target so softmax assigns them zero
     probability.

Use ``combined_navigation_loss`` for the full sum with tunable lambdas.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F


# Neighbor offsets in (dx, dy) order: N, NE, E, SE, S, SW, W, NW.
# Matches the convention in golem2.policies.distance_panorama.
_NEIGHBOR_OFFSETS = ((0, -1), (1, -1), (1, 0), (1, 1),
                     (0, 1), (-1, 1), (-1, 0), (-1, -1))


def value_mse(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Plain MSE over the r and g channels only."""
    return ((pred[:, :2] - target[:, :2]) ** 2).mean()


def robot_local_mask(
    robot_cell_x: torch.Tensor,
    robot_cell_y: torch.Tensor,
    grid_size: int,
    sigma_cells: float = 2.0,
) -> torch.Tensor:
    """Build a (B, 1, H, W) Gaussian mask centered on each example's robot cell.

    Value 1.0 at the robot cell, falls off as exp(-d^2 / (2 sigma^2)).
    """
    device = robot_cell_x.device
    batch = robot_cell_x.shape[0]
    yy, xx = torch.meshgrid(
        torch.arange(grid_size, device=device),
        torch.arange(grid_size, device=device),
        indexing="ij",
    )
    # broadcast to (B, H, W)
    yy = yy.unsqueeze(0).expand(batch, -1, -1)
    xx = xx.unsqueeze(0).expand(batch, -1, -1)
    rx = robot_cell_x.view(batch, 1, 1)
    ry = robot_cell_y.view(batch, 1, 1)
    d2 = (xx - rx).float() ** 2 + (yy - ry).float() ** 2
    mask = torch.exp(-d2 / (2.0 * sigma_cells * sigma_cells))
    return mask.unsqueeze(1)  # (B, 1, H, W)


def local_weighted_mse(
    pred: torch.Tensor,
    target: torch.Tensor,
    robot_cell_x: torch.Tensor,
    robot_cell_y: torch.Tensor,
    grid_size: int,
    sigma_cells: float = 2.0,
) -> torch.Tensor:
    """Gaussian-weighted MSE on r,g, peaking at each example's robot cell."""
    err = (pred[:, :2] - target[:, :2]) ** 2  # (B, 2, H, W)
    mask = robot_local_mask(robot_cell_x, robot_cell_y, grid_size, sigma_cells)
    # Normalize by mask sum so the magnitude is comparable to a plain mean
    # rather than scaling with sigma. Each example normalized independently.
    mask_sum = mask.sum(dim=(2, 3), keepdim=True).clamp_min(1e-6)
    weighted = (err * mask) / mask_sum
    # Sum spatially (already normalized), then mean over batch and channels
    return weighted.sum(dim=(2, 3)).mean()


def _neighbor_scores(
    field: torch.Tensor,
    robot_cell_x: torch.Tensor,
    robot_cell_y: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Extract the 8-neighbor ring of values around each example's robot cell.

    field: (B, H, W). Returns (values, in_bounds) each of shape (B, 8).
    Out-of-bounds neighbors are clamped to the nearest valid cell for gather
    safety; the ``in_bounds`` mask records which were valid.
    """
    batch, height, width = field.shape
    offsets = torch.tensor(_NEIGHBOR_OFFSETS, dtype=torch.long, device=field.device)
    # (B, 8) per axis
    rx_8 = robot_cell_x.view(batch, 1) + offsets[:, 0].view(1, 8)
    ry_8 = robot_cell_y.view(batch, 1) + offsets[:, 1].view(1, 8)
    in_bounds = (rx_8 >= 0) & (rx_8 < width) & (ry_8 >= 0) & (ry_8 < height)
    rx_clamped = rx_8.clamp(0, width - 1)
    ry_clamped = ry_8.clamp(0, height - 1)
    flat_idx = ry_clamped * width + rx_clamped  # (B, 8)
    values = torch.gather(field.view(batch, height * width), 1, flat_idx)
    return values, in_bounds


def neighbor_argmax_ce(
    pred: torch.Tensor,
    target: torch.Tensor,
    robot_cell_x: torch.Tensor,
    robot_cell_y: torch.Tensor,
) -> torch.Tensor:
    """Cross-entropy on the 8-neighbor ring of ``g - |r|`` scores.

    Target is the argmax of the ground-truth score over those 8 cells.
    Out-of-bounds neighbors get ``-inf`` logits in both pred and target so
    softmax masks them out and they're never the argmax.
    """
    pred_score = pred[:, 1] - pred[:, 0].abs()      # (B, H, W)
    target_score = target[:, 1] - target[:, 0].abs()
    pred_8, in_bounds = _neighbor_scores(pred_score, robot_cell_x, robot_cell_y)
    target_8, _ = _neighbor_scores(target_score, robot_cell_x, robot_cell_y)
    # Replace out-of-bounds entries with -inf so they're never picked
    neg_inf = torch.tensor(float("-inf"), device=pred.device)
    pred_8 = torch.where(in_bounds, pred_8, neg_inf)
    target_8 = torch.where(in_bounds, target_8, neg_inf)
    target_idx = target_8.argmax(dim=1)  # (B,) long
    return F.cross_entropy(pred_8, target_idx)


def combined_navigation_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    robot_cell_x: torch.Tensor,
    robot_cell_y: torch.Tensor,
    grid_size: int,
    *,
    lambda_value: float = 1.0,
    lambda_local: float = 3.0,
    lambda_ce: float = 1.0,
    sigma_cells: float = 2.0,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Sum of value MSE + local-weighted MSE + 8-neighbor argmax CE.

    Returns the scalar loss and a dict of the three terms for logging.
    """
    v = value_mse(pred, target)
    local = local_weighted_mse(
        pred, target, robot_cell_x, robot_cell_y, grid_size, sigma_cells
    )
    ce = neighbor_argmax_ce(pred, target, robot_cell_x, robot_cell_y)
    total = lambda_value * v + lambda_local * local + lambda_ce * ce
    parts = {
        "value_mse": float(v.detach().item()),
        "local_weighted_mse": float(local.detach().item()),
        "neighbor_argmax_ce": float(ce.detach().item()),
        "total": float(total.detach().item()),
    }
    return total, parts
