from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..graph import KnowledgeGraph
from ..robot.motors import MotorCommand, SimulatedMotorExecutor
from ..vision.latches import LatchState, ProjectionLatch, min_law, split_urgency
from ..vision.projection_transforms import RiskPanoramaTransform, lorentzian_urgency
from ..vision.quantized_heatmap import HeatMap


DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
DIRECTION_INDEX = {name: index for index, name in enumerate(DIRECTIONS)}
# Front arcs wrap across the panorama boundary: NW, N, and NE are neighbors.
ARCS = {
    "front": ("NW", "N", "NE"),
    "left": ("SW", "W", "NW"),
    "right": ("NE", "E", "SE"),
}


def distances_to_risk(distances: list[float], danger_distance: float) -> list[list[float]]:
    """Convert distance readings into obstacle urgency values.

    Positive urgency means too close. Negative urgency means clear enough.
    """

    return [[lorentzian_urgency(distance, danger_distance) for distance in distances]]


def arc_clearances(distances: list[float]) -> dict[str, float]:
    return {
        name: sum(distances[DIRECTION_INDEX[direction]] for direction in directions)
        for name, directions in ARCS.items()
    }


def choose_avoidance_action(latch_state: LatchState, clearances: dict[str, float]) -> MotorCommand:
    if not latch_state.latched:
        return MotorCommand(
            "forward",
            speed=0.15,
            duration=0.25,
            rationale="Front obstacle latch is clear.",
        )
    if clearances["left"] > clearances["right"]:
        return MotorCommand(
            "turn_left",
            speed=0.12,
            duration=0.2,
            rationale="Obstacle ahead; left arc has more clearance, so turn left.",
        )
    return MotorCommand(
        "turn_right",
        speed=0.12,
        duration=0.2,
        rationale="Obstacle ahead; right arc has more clearance, so turn right.",
    )


def main() -> None:
    danger_distance = 0.45
    frames = [
        [1.2, 1.0, 0.9, 0.8, 1.4, 1.1, 1.0, 1.2],
        [0.38, 0.42, 0.8, 1.0, 1.4, 1.3, 1.1, 0.5],
        [0.32, 0.35, 0.9, 1.2, 1.4, 1.4, 1.2, 0.4],
    ]

    latch = ProjectionLatch(
        "front_obstacle_gate",
        "distance",
        parent_thresholds=split_urgency(0.5, 8),
        threshold_law=min_law,
        latch_min_active=1,
    )
    transform = RiskPanoramaTransform(danger_distance)
    motor_executor = SimulatedMotorExecutor(max_speed=0.2, max_duration=0.4)
    run_root = Path(__file__).resolve().parents[1] / "runs" / "proximity_panorama_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    graph = KnowledgeGraph(run_root / "graph.sqlite")

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
            graph.record_heatmap_comparison(f"proximity_frame_{frame_index}", comparison)
        latch_state = latch.update(projection)
        clearances = arc_clearances(distances)
        motor_command = choose_avoidance_action(latch_state, clearances)
        motor_result = motor_executor.execute(motor_command, distances)
        states.append(
            {
                "distances_by_direction": dict(zip(DIRECTIONS, distances, strict=True)),
                "risk": risk[0],
                "arc_clearances": clearances,
                "latch": latch_state.to_payload(),
                "heatmap_score": heatmap.total_score(),
                "comparison": comparison,
                "motor_command": motor_command.to_payload(),
                "motor_result": motor_result.to_payload(),
                "llm_visible": _llm_visible_events(latch_state, motor_result),
            }
        )
        previous_heatmap = heatmap

    print(
        json.dumps(
            {
                "danger_distance": danger_distance,
                "states": states,
                "graph": graph.summary(),
            },
            indent=2,
        )
    )


def _llm_visible_events(latch_state: LatchState, motor_result) -> list[dict]:
    events = []
    if latch_state.latched:
        events.append(
            {
                "kind": "exception",
                "reason": "front_obstacle_latched",
                "urgency": latch_state.sample_score,
                "llm_role": "adjust urgency downward or select a safer high-level policy",
            }
        )
    if motor_result.forced_stop:
        events.append(
            {
                "kind": "safety_gate",
                "reason": motor_result.message,
                "llm_role": "explain or re-plan; executor already stopped motors",
            }
        )
    return events


if __name__ == "__main__":
    main()
