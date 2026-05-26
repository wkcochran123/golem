from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class ProximityReading:
    direction: str
    distance_m: float
    sensor_id: str = ""
    captured_at: str = ""

    def __post_init__(self) -> None:
        if self.distance_m < 0:
            raise ValueError("distance_m must be non-negative.")
        if not self.captured_at:
            object.__setattr__(
                self,
                "captured_at",
                datetime.now(timezone.utc).isoformat(),
            )

    def to_payload(self) -> dict:
        return {
            "direction": self.direction,
            "distance_m": self.distance_m,
            "sensor_id": self.sensor_id,
            "captured_at": self.captured_at,
        }

    def age_seconds(self, now: datetime | None = None) -> float:
        now = now or datetime.now(timezone.utc)
        captured = datetime.fromisoformat(self.captured_at)
        if captured.tzinfo is None:
            captured = captured.replace(tzinfo=timezone.utc)
        return max(0.0, (now - captured).total_seconds())


class ProximityDriver(Protocol):
    def read(self) -> list[ProximityReading]:
        ...


class ProximityRing:
    """Validated 8-way proximity reader for the Pi reflex tier."""

    def __init__(
        self,
        driver: ProximityDriver,
        directions: list[str],
        *,
        max_age_seconds: float | None = None,
    ):
        if not directions:
            raise ValueError("directions must not be empty.")
        if len(set(directions)) != len(directions):
            raise ValueError("directions must be unique.")
        if max_age_seconds is not None and max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative.")
        self.driver = driver
        self.directions = directions
        self.max_age_seconds = max_age_seconds

    def read(self) -> list[ProximityReading]:
        readings = self.driver.read()
        if len(readings) != len(self.directions):
            raise ValueError(
                f"Expected {len(self.directions)} proximity readings, got {len(readings)}."
            )
        expected = set(self.directions)
        observed = {reading.direction for reading in readings}
        if observed != expected:
            raise ValueError(
                f"Expected directions {sorted(expected)}, got {sorted(observed)}."
            )
        by_direction = {reading.direction: reading for reading in readings}
        ordered = [by_direction[direction] for direction in self.directions]
        self._validate_freshness(ordered)
        return ordered

    def distances(self) -> list[float]:
        return [reading.distance_m for reading in self.read()]

    def _validate_freshness(self, readings: list[ProximityReading]) -> None:
        if self.max_age_seconds is None:
            return
        now = datetime.now(timezone.utc)
        stale = [
            reading
            for reading in readings
            if reading.age_seconds(now) > self.max_age_seconds
        ]
        if stale:
            directions = ", ".join(reading.direction for reading in stale)
            raise ValueError(
                f"Stale proximity readings for {directions}; "
                f"max_age_seconds={self.max_age_seconds}."
            )
