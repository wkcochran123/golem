from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from ..robot.camera import CameraRing, FakeCameraDriver


def _frames() -> list[list[list[int]]]:
    frames: list[list[list[int]]] = []
    for offset in range(5):
        frame = [[0 for _ in range(8)] for _ in range(8)]
        frame[0][offset] = 1
        frame[4][4] = 2
        frames.append(frame)
    return frames


def main() -> None:
    fresh_ring = CameraRing(FakeCameraDriver(_frames()), width=8, height=8, max_age_seconds=1.0)
    shapes = []
    for _ in range(5):
        reading = fresh_ring.read()
        shapes.append([reading.height, reading.width])

    stale_time = (datetime.now(timezone.utc) - timedelta(seconds=5)).isoformat()
    stale_ring = CameraRing(
        FakeCameraDriver(_frames(), captured_at=stale_time),
        width=8,
        height=8,
        max_age_seconds=1.0,
    )
    stale_error = ""
    try:
        stale_ring.read()
    except ValueError as exc:
        stale_error = str(exc)

    print(json.dumps({"shapes": shapes, "stale_error": stale_error}, indent=2))


if __name__ == "__main__":
    main()
