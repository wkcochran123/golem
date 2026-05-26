from __future__ import annotations

import json
from pathlib import Path

from ..policies.vision_model import VisionMLP


def _load_frame() -> list[list[int]]:
    candidates = sorted(Path("golem2/runs/synthetic_dataset").glob("*/dataset.jsonl"))
    if candidates:
        first = candidates[-1].read_text(encoding="utf-8").splitlines()[0]
        return json.loads(first)["frame"]
    frame = [[0 for _ in range(64)] for _ in range(64)]
    frame[32][32] = 2
    return frame


def main() -> None:
    frame = _load_frame()
    model = VisionMLP(len(frame), len(frame[0]), hidden=16, output=8, seed=0)
    print(json.dumps(model.predict(frame)))


if __name__ == "__main__":
    main()
