from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from ..mapping.occupancy import Pose2D
from ..sim.ideal_basement import IdealBasementScene
from ..vision.projection_transforms import RiskPanoramaTransform
from ..vision.quantized_heatmap import HeatMap


DIRECTIONS = [
    0.0,
    math.pi / 4,
    math.pi / 2,
    3 * math.pi / 4,
    math.pi,
    -3 * math.pi / 4,
    -math.pi / 2,
    -math.pi / 4,
]


def make_example(scene: IdealBasementScene, before: Pose2D, after: Pose2D, danger_distance: float) -> dict:
    transform = RiskPanoramaTransform(danger_distance)
    before_distances = scene.proximity_scan(before, DIRECTIONS)
    after_distances = scene.proximity_scan(after, DIRECTIONS)
    before_projection = transform.apply(before_distances)
    after_projection = transform.apply(after_distances)
    before_heatmap = HeatMap.from_sensor_grid([list(before_projection.values)], threshold=0.0)
    after_heatmap = HeatMap.from_sensor_grid([list(after_projection.values)], threshold=0.0)
    return {
        "before_pose": before.__dict__,
        "after_pose": after.__dict__,
        "before_distances": before_distances,
        "after_distances": after_distances,
        "before_risk": list(before_projection.values),
        "after_risk": list(after_projection.values),
        "comparison": before_heatmap.compare(after_heatmap, threshold=1.0),
    }


def main() -> None:
    run_root = Path(__file__).resolve().parents[1] / "runs" / "ideal_basement_dataset"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True)

    scene = IdealBasementScene.box(width=4.0, height=3.0, max_range=2.0)
    danger_distance = 0.45
    poses = [
        Pose2D(0.0, 0.0, 0.0),
        Pose2D(0.3, 0.0, 0.0),
        Pose2D(0.6, 0.0, 0.0),
        Pose2D(0.6, 0.0, math.pi / 8),
        Pose2D(1.3, 0.0, 0.0),
        Pose2D(1.6, 0.0, 0.0),
    ]
    examples = [
        make_example(scene, before, after, danger_distance)
        for before, after in zip(poses, poses[1:])
    ]
    dataset_path = run_root / "examples.jsonl"
    with dataset_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example, sort_keys=True) + "\n")
    print(json.dumps({"dataset": str(dataset_path), "examples": examples}, indent=2))


if __name__ == "__main__":
    main()
