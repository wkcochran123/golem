from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from ..robot.proximity import ProximityReading, ProximityRing
from .proximity_panorama_loop import DIRECTIONS


class FakeProximityDriver:
    def __init__(self, readings: list[ProximityReading]):
        self.readings = readings

    def read(self) -> list[ProximityReading]:
        return self.readings


def _readings(captured_at: str) -> list[ProximityReading]:
    return [
        ProximityReading(direction, 1.0, sensor_id=f"prox_{index}", captured_at=captured_at)
        for index, direction in enumerate(DIRECTIONS)
    ]


def main() -> None:
    now = datetime.now(timezone.utc)
    fresh_ring = ProximityRing(
        FakeProximityDriver(_readings(now.isoformat())),
        DIRECTIONS,
        max_age_seconds=1.0,
    )
    stale_ring = ProximityRing(
        FakeProximityDriver(_readings((now - timedelta(seconds=5)).isoformat())),
        DIRECTIONS,
        max_age_seconds=1.0,
    )

    stale_error = ""
    try:
        stale_ring.distances()
    except ValueError as exc:
        stale_error = str(exc)

    print(
        json.dumps(
            {
                "fresh_distances": fresh_ring.distances(),
                "stale_error": stale_error,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
