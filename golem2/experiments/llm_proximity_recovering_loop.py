from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from ..graph import KnowledgeGraph
from ..mapping.occupancy import OccupancyGrid, Pose2D
from ..policies.proximity_recovering_scripted import ScriptedProximityRecoveringPolicy
from ..policies.regime_manager import RegimeManager
from ..policies.types import PolicyInput, PolicyRegime, RegimeThreshold
from ..robot.motors import SimulatedMotorExecutor
from ..store import EventLog
from ..vision.latches import ProjectionLatch, min_law
from ..vision.projection_transforms import RiskPanoramaTransform
from ..vision.quantized_heatmap import HeatMap
from .llm_proximity_two_latches_loop import (
    CLEAR_PATH_MIN_ACTIVE,
    RADIAN_DIRECTIONS,
    _two_latch_visible_events,
)
from .proximity_panorama_loop import (
    DIRECTIONS,
    arc_clearances,
    choose_avoidance_action,
    distances_to_risk,
)


def main() -> None:
    danger_distance = 0.45
    # 8 frames designed to exercise the recovery counter:
    # - Frame 0: obstacle → inner raises obstacle threshold, counter resets.
    # - Frames 1-2: distances just above danger_distance, few free cells →
    #   neither latch fires (silent), counter ticks up.
    # - Frame 3: still silent, counter ticks to 3.
    # - Frame 4: still silent, counter > 3 → revert fires (-0.02).
    # - Frame 5: clear_path latches → inner's clear-path adjustment, counter
    #   advances (positive exception doesn't reset, but takes the action slot).
    # - Frame 6: obstacle returns → counter resets, inner raises threshold again.
    # - Frame 7: silent again, counter starts ticking from 1.
    frames = [
        [0.38, 0.42, 0.8, 1.0, 1.4, 1.3, 1.1, 0.5],     # obstacle ahead
        [0.55, 0.60, 0.55, 0.60, 0.55, 0.60, 0.55, 0.60],  # silent (no latch)
        [0.55, 0.60, 0.55, 0.60, 0.55, 0.60, 0.55, 0.60],  # silent
        [0.55, 0.60, 0.55, 0.60, 0.55, 0.60, 0.55, 0.60],  # silent (counter=3)
        [0.55, 0.60, 0.55, 0.60, 0.55, 0.60, 0.55, 0.60],  # silent → revert
        [1.5, 1.4, 1.3, 1.4, 1.6, 1.5, 1.4, 1.5],       # clear_path latches
        [0.35, 0.40, 0.9, 1.2, 1.4, 1.4, 1.2, 0.4],     # obstacle returns
        [0.55, 0.60, 0.55, 0.60, 0.55, 0.60, 0.55, 0.60],  # silent again
    ]
    pose = Pose2D(x=0.0, y=0.0, theta=0.0)

    run_root = Path(__file__).resolve().parents[1] / "runs" / "llm_proximity_recovering_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    graph = KnowledgeGraph(run_root / "graph.sqlite")
    event_log = EventLog(run_root / "events.jsonl")

    regime = PolicyRegime(
        name="basement_proximity_recovering",
        objective=(
            "Two-latch threshold control with symmetric tighten-back so "
            "thresholds revert toward baseline during calm runs."
        ),
        thresholds=[
            RegimeThreshold(
                name="front_obstacle_risk",
                projection="distance_panorama",
                current_value=0.0,
                threshold=0.0,
                urgency=0.3,
                min_threshold=0.0,
                max_threshold=0.5,
                min_urgency=0.1,
                max_urgency=0.5,
                units="risk_score",
            ),
            RegimeThreshold(
                name="clear_path_low",
                projection="occupancy_free",
                current_value=0.0,
                threshold=0.5,
                urgency=0.2,
                min_threshold=0.1,
                max_threshold=0.9,
                min_urgency=0.05,
                max_urgency=0.4,
                units="free_cell_score",
            ),
        ],
        allowed_actions=["adjust_threshold", "noop"],
    )
    manager = RegimeManager([regime], graph=graph, event_log=event_log)

    front_obstacle_latch = ProjectionLatch(
        "front_obstacle_gate",
        "distance",
        parent_thresholds=[0.0],
        threshold_law=min_law,
        latch_min_active=1,
    )
    manager.bind_latch(
        "basement_proximity_recovering", "front_obstacle_risk", front_obstacle_latch
    )

    clear_path_latch = ProjectionLatch(
        "clear_path_gate",
        "occupancy",
        parent_thresholds=[0.5],
        threshold_law=min_law,
        latch_min_active=CLEAR_PATH_MIN_ACTIVE,
    )
    manager.bind_latch(
        "basement_proximity_recovering", "clear_path_low", clear_path_latch
    )

    transform = RiskPanoramaTransform(danger_distance)
    motor_executor = SimulatedMotorExecutor(max_speed=0.2, max_duration=0.4)
    policy = ScriptedProximityRecoveringPolicy(
        frames_until_revert=3,
        revert_step=0.02,
    )

    states = []
    previous_heatmap = None
    for frame_index, distances in enumerate(frames):
        risk = distances_to_risk(distances, danger_distance)
        projection = transform.apply(distances)
        heatmap = HeatMap.from_sensor_grid(
            risk,
            threshold=0.0,
            calibration=f"8-proximity-panorama danger_distance={danger_distance}",
        )
        comparison = previous_heatmap.compare(heatmap, threshold=1.0) if previous_heatmap else None
        if comparison:
            graph.record_heatmap_comparison(
                f"recovering_frame_{frame_index}", comparison
            )

        grid = OccupancyGrid(width=21, height=21, resolution=0.25)
        grid.apply_proximity_scan(pose, distances, RADIAN_DIRECTIONS, max_range=2.0)
        free_projection = grid.to_projection_map(mode="free")

        front_obstacle_state = front_obstacle_latch.update(projection)
        clear_path_state = clear_path_latch.update(free_projection)

        clearances = arc_clearances(distances)
        motor_command = choose_avoidance_action(front_obstacle_state, clearances)
        motor_result = motor_executor.execute(motor_command, distances)
        llm_visible = _two_latch_visible_events(
            front_obstacle_latched=front_obstacle_state.latched,
            clear_path_latched=clear_path_state.latched,
            motor_forced_stop=motor_result.forced_stop,
            motor_message=motor_result.message,
        )

        policy_input = PolicyInput(
            graph_summary=graph.summary(),
            recent_failures=graph.failures(),
            available_actions=["adjust_threshold", "noop"],
            policy_hints=graph.affordances(),
            task_state={
                "frame_index": frame_index,
                "front_obstacle_latch": front_obstacle_state.to_payload(),
                "clear_path_latch": clear_path_state.to_payload(),
                "llm_visible": llm_visible,
            },
            regimes=[manager.regimes["basement_proximity_recovering"]],
        )
        threshold_action = policy.choose(policy_input)
        threshold_result = None
        if threshold_action.action_type == "adjust_threshold":
            threshold_result = manager.execute(
                "basement_proximity_recovering", threshold_action
            )

        regime_after = manager.regimes["basement_proximity_recovering"]

        states.append(
            {
                "frame_index": frame_index,
                "front_obstacle_latched": front_obstacle_state.latched,
                "clear_path_latched": clear_path_state.latched,
                "frames_since_exception": policy.frames_since_exception,
                "threshold_action": threshold_action.to_payload(),
                "threshold_result": threshold_result.to_payload() if threshold_result else None,
                "front_obstacle_threshold_after": next(
                    t.threshold
                    for t in regime_after.thresholds
                    if t.name == "front_obstacle_risk"
                ),
            }
        )
        previous_heatmap = heatmap

    print(
        json.dumps(
            {
                "danger_distance": danger_distance,
                "policy_config": {
                    "frames_until_revert": policy.frames_until_revert,
                    "revert_step": policy.revert_step,
                },
                "states": states,
                "events": list(event_log.read()),
                "graph": graph.summary(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
