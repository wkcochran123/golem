from __future__ import annotations

import json

from ..robot.proximity import ProximityReading, ProximityRing
from ..vision.projection_transforms import RiskPanoramaTransform
from .proximity_panorama_loop import DIRECTIONS, distances_to_risk


class FakeProximityDriver:
    def __init__(self, readings: list[ProximityReading]):
        self.readings = readings

    def read(self) -> list[ProximityReading]:
        return self.readings


def main() -> None:
    readings = [
        ProximityReading(direction, distance, sensor_id=f"prox_{index}")
        for index, (direction, distance) in enumerate(
            zip(
                DIRECTIONS,
                [1.5, 1.4, 1.3, 1.4, 1.6, 1.5, 1.4, 1.5],
                strict=True,
            )
        )
    ]
    ring = ProximityRing(FakeProximityDriver(readings), DIRECTIONS)
    distances = ring.distances()
    danger_distance = 0.45
    risk = distances_to_risk(distances, danger_distance)
    projection = RiskPanoramaTransform(danger_distance).apply(distances)
    print(
        json.dumps(
            {
                "readings": [reading.to_payload() for reading in ring.read()],
                "distances": distances,
                "risk": risk,
                "projection": {
                    "kind": projection.kind,
                    "width": projection.width,
                    "height": projection.height,
                    "values": list(projection.values),
                    "threshold": projection.threshold,
                    "calibration": projection.calibration,
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
