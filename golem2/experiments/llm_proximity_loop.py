from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..graph import KnowledgeGraph
from ..policies.proximity_regime_scripted import ScriptedProximityRegimePolicy
from ..policies.regime_manager import RegimeManager
from ..policies.types import PolicyInput, PolicyRegime, RegimeThreshold
from ..robot.motors import SimulatedMotorExecutor
from ..store import EventLog
from ..vision.latches import ProjectionLatch, min_law
from ..vision.projection_transforms import RiskPanoramaTransform
from ..vision.quantized_heatmap import HeatMap
from .proximity_panorama_loop import (
    DIRECTIONS,
    arc_clearances,
    choose_avoidance_action,
    distances_to_risk,
    _llm_visible_events,
)


def main() -> None:
    danger_distance = 0.45
    frames = [
        [1.2, 1.0, 0.9, 0.8, 1.4, 1.1, 1.0, 1.2],
        [0.38, 0.42, 0.8, 1.0, 1.4, 1.3, 1.1, 0.5],
        [0.32, 0.35, 0.9, 1.2, 1.4, 1.4, 1.2, 0.4],
    ]
    run_root = Path(__file__).resolve().parents[1] / "runs" / "llm_proximity_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    graph = KnowledgeGraph(run_root / "graph.sqlite")
    event_log = EventLog(run_root / "events.jsonl")
    regime = PolicyRegime(
        name="basement_proximity",
        objective="Keep rolling only when the proximity panorama is calm.",
        thresholds=[
            RegimeThreshold(
                name="front_obstacle_risk",
                projection="distance_panorama",
                current_value=0.0,
                threshold=0.0625,
                urgency=0.5,
                min_threshold=0.0,
                max_threshold=0.5,
                min_urgency=0.1,
                max_urgency=0.5,
                units="risk_score",
            )
        ],
        unstructured_context={
            "operator_goal": "roll around the basement without hitting things",
            "control_note": "the LLM may adjust thresholds, but motors remain local",
        },
        allowed_actions=["adjust_threshold", "noop"],
    )
    manager = RegimeManager([regime], graph=graph, event_log=event_log)
    latch = ProjectionLatch(
        "front_obstacle_gate",
        "distance",
        parent_thresholds=[0.0],
        threshold_law=min_law,
        latch_min_active=1,
    )
    manager.bind_latch("basement_proximity", "front_obstacle_risk", latch)

    transform = RiskPanoramaTransform(danger_distance)
    motor_executor = SimulatedMotorExecutor(max_speed=0.2, max_duration=0.4)
    policy = ScriptedProximityRegimePolicy()
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
            graph.record_heatmap_comparison(f"llm_proximity_frame_{frame_index}", comparison)
        latch_state = latch.update(projection)
        clearances = arc_clearances(distances)
        motor_command = choose_avoidance_action(latch_state, clearances)
        motor_result = motor_executor.execute(motor_command, distances)
        llm_visible = _llm_visible_events(latch_state, motor_result)
        policy_input = PolicyInput(
            graph_summary=graph.summary(),
            recent_failures=graph.failures(),
            available_actions=["adjust_threshold", "noop"],
            policy_hints=graph.affordances(),
            task_state={
                "frame_index": frame_index,
                "latch": latch_state.to_payload(),
                "llm_visible": llm_visible,
            },
            regimes=[manager.regimes["basement_proximity"]],
        )
        threshold_action = policy.choose(policy_input)
        threshold_result = None
        if threshold_action.action_type == "adjust_threshold":
            threshold_result = manager.execute("basement_proximity", threshold_action)

        states.append(
            {
                "frame_index": frame_index,
                "distances_by_direction": dict(zip(DIRECTIONS, distances, strict=True)),
                "risk": risk[0],
                "latch_before_policy": latch_state.to_payload(),
                "motor_command": motor_command.to_payload(),
                "motor_result": motor_result.to_payload(),
                "llm_visible": llm_visible,
                "threshold_action": threshold_action.to_payload(),
                "threshold_result": threshold_result.to_payload() if threshold_result else None,
                "regime_after_policy": manager.regimes["basement_proximity"].to_payload(),
            }
        )
        previous_heatmap = heatmap

    print(
        json.dumps(
            {
                "danger_distance": danger_distance,
                "states": states,
                "events": list(event_log.read()),
                "graph": graph.summary(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
