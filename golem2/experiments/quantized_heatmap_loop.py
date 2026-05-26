from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..graph import KnowledgeGraph
from ..vision.quantized_heatmap import HeatMap


def main() -> None:
    run_root = Path(__file__).resolve().parents[1] / "runs" / "quantized_heatmap_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True)

    before_sensor = [
        [-0.8, -0.2, 0.1, 0.4],
        [-0.7, -0.1, 0.2, 0.3],
        [-0.6, -0.2, 0.1, 0.2],
        [-0.9, -0.4, -0.1, 0.1],
    ]
    after_sensor = [
        [-0.8, 0.2, 0.4, 0.7],
        [-0.7, 0.1, 0.5, 0.8],
        [-0.6, -0.1, 0.4, 0.7],
        [-0.9, -0.2, 0.2, 0.5],
    ]

    before = HeatMap.from_sensor_grid(before_sensor, threshold=0.0)
    after = HeatMap.from_sensor_grid(after_sensor, threshold=0.0)
    before.write_ppm(run_root / "before.ppm")
    after.write_ppm(run_root / "after.ppm")
    comparison = before.compare(after, threshold=3.0)
    graph = KnowledgeGraph(run_root / "graph.sqlite")
    graph.record_heatmap_comparison("synthetic_sensor_score", comparison)

    result = {
        "run_root": str(run_root),
        "before_score": before.total_score(),
        "after_score": after.total_score(),
        "comparison": comparison,
        "changed_cells": before.changed_cells(after),
        "graph": graph.summary(),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
