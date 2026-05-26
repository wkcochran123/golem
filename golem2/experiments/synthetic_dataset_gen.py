from __future__ import annotations

import json
import math
import random
import uuid
from dataclasses import asdict
from pathlib import Path

from ..mapping.occupancy import Pose2D
from ..sim.camera import render_top_down
from .maze_navigation_demo import DIRECTIONS, make_maze_world


def generate_dataset(count: int = 200, *, seed: int = 0, width: int = 64, height: int = 64) -> Path:
    rng = random.Random(seed)
    world = make_maze_world()
    run_dir = Path("golem2/runs/synthetic_dataset") / uuid.uuid4().hex
    run_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = run_dir / "dataset.jsonl"
    with dataset_path.open("w", encoding="utf-8") as handle:
        for _ in range(count):
            pose = Pose2D(
                x=rng.uniform(-1.8, 1.8),
                y=rng.uniform(-1.8, 1.8),
                theta=rng.uniform(-math.pi, math.pi),
            )
            frame = render_top_down(world.scene, pose, width=width, height=height)
            target = world.scene.proximity_scan(pose, DIRECTIONS)
            handle.write(json.dumps({"frame": frame, "target": target, "pose": asdict(pose)}) + "\n")
    return dataset_path


def ascii_frame(frame: list[list[int]], *, stride: int = 4) -> str:
    glyphs = {0: ".", 1: "#", 2: "R"}
    return "\n".join(
        "".join(glyphs.get(value, "?") for value in row[::stride])
        for row in frame[::stride]
    )


def main() -> None:
    dataset_path = generate_dataset()
    lines = dataset_path.read_text(encoding="utf-8").splitlines()
    sample = json.loads(lines[0])
    print(
        json.dumps(
            {
                "dataset_path": str(dataset_path),
                "count": len(lines),
                "frame_shape": [len(sample["frame"]), len(sample["frame"][0])],
                "target_shape": [len(sample["target"])],
            },
            indent=2,
        )
    )
    print(ascii_frame(sample["frame"]))


if __name__ == "__main__":
    main()
