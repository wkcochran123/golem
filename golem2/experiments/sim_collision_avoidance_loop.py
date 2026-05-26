from __future__ import annotations

import json
import math
from pathlib import Path

from ..mapping.occupancy import Pose2D
from ..sim.ideal_basement import IdealBasementScene


def _serialize_step(label: str, pose_before: Pose2D, result, pose_after: Pose2D) -> dict:
    return {
        "label": label,
        "pose_before": {"x": pose_before.x, "y": pose_before.y, "theta": pose_before.theta},
        "result": result.to_payload(),
        "pose_after": {"x": pose_after.x, "y": pose_after.y, "theta": pose_after.theta},
    }


def main() -> None:
    # 4x3 m box, walls at x=±2, y=±1.5. clearance=0.05 m.
    scene = IdealBasementScene.box(width=4.0, height=3.0, max_range=2.0)
    clearance = 0.05

    steps = []

    # Step 1: start in the middle facing east. Forward 1.0 m is safe (lands at 1.0).
    pose0 = Pose2D(x=0.0, y=0.0, theta=0.0)
    pose1, result1 = scene.safe_move(pose0, forward=1.0, clearance=clearance)
    steps.append(_serialize_step("middle_room_safe_forward", pose0, result1, pose1))

    # Step 2: now at x=1.0, facing east. Forward 1.5 m would land at x=2.5,
    # past the right wall at x=2.0. Should truncate to x=2.0-0.05=1.95.
    pose2, result2 = scene.safe_move(pose1, forward=1.5, clearance=clearance)
    steps.append(_serialize_step("forward_into_right_wall", pose1, result2, pose2))

    # Step 3: turn 180 degrees (free rotation), then forward 2.0 m would reach
    # x=-2.05 past the left wall. Should truncate to x=-2.0+0.05=-1.95.
    pose3, result3 = scene.safe_move(pose2, forward=2.0, turn=math.pi, clearance=clearance)
    steps.append(_serialize_step("turn_and_forward_into_left_wall", pose2, result3, pose3))

    # Step 4: from the truncated pose, request small forward 0.5 m heading west.
    # Already very close to left wall; should truncate to allowed_forward = 0
    # (or very small) and stop right where we are.
    pose4, result4 = scene.safe_move(pose3, forward=0.5, clearance=clearance)
    steps.append(_serialize_step("nudge_into_wall_at_close_range", pose3, result4, pose4))

    # Step 5: turn back to face east, then forward 5.0 m crosses entire room.
    # Should truncate at right wall.
    pose5, result5 = scene.safe_move(pose4, forward=5.0, turn=math.pi, clearance=clearance)
    steps.append(_serialize_step("turn_back_and_charge_across_room", pose4, result5, pose5))

    # Step 6: zero forward, just turn. Should never intervene.
    pose6, result6 = scene.safe_move(pose5, forward=0.0, turn=math.pi / 2, clearance=clearance)
    steps.append(_serialize_step("rotate_in_place", pose5, result6, pose6))

    summary = {
        "scene": {
            "walls": [
                {"x1": w.x1, "y1": w.y1, "x2": w.x2, "y2": w.y2}
                for w in scene.walls
            ],
            "max_range": scene.max_range,
        },
        "clearance": clearance,
        "steps": steps,
        "interventions": sum(1 for s in steps if s["result"]["intervened"]),
        "total_requested_forward": sum(s["result"]["requested_forward"] for s in steps),
        "total_allowed_forward": sum(s["result"]["allowed_forward"] for s in steps),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
