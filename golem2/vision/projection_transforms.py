from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .latches import ProjectionMap


class ProjectionTransform(Protocol):
    name: str

    def apply(self, values: list[float]) -> ProjectionMap:
        ...


@dataclass(frozen=True)
class RiskPanoramaTransform:
    danger_distance: float
    name: str = "risk_panorama"

    def apply(self, values: list[float]) -> ProjectionMap:
        risk = [lorentzian_urgency(value, self.danger_distance) for value in values]
        return ProjectionMap.from_rows(
            "distance",
            [risk],
            threshold=0.0,
            calibration=f"risk=lorentzian_urgency(distance,danger_distance={self.danger_distance})",
        )


@dataclass(frozen=True)
class ClearancePanoramaTransform:
    danger_distance: float
    name: str = "clearance_panorama"

    def apply(self, values: list[float]) -> ProjectionMap:
        clearance = [value - self.danger_distance for value in values]
        return ProjectionMap.from_rows(
            "distance",
            [clearance],
            threshold=0.0,
            calibration=f"clearance=distance-danger_distance({self.danger_distance})",
        )


def lorentzian_urgency(distance: float, danger_distance: float) -> float:
    """Map a distance reading to a signed urgency surface.

    Positive means inside the danger boundary. Outside the boundary remains
    negative clearance. Inside the boundary, normalized closeness is quantized
    into the series 1/2, 3/4, 7/8, 15/16, ... so urgency steepens near contact.
    """

    if distance >= danger_distance:
        return danger_distance - distance
    if danger_distance <= 0:
        return 1.0
    normalized_closeness = max(0.0, min(1.0, 1.0 - distance / danger_distance))
    return lorentzian_quantize(normalized_closeness)


def lorentzian_quantize(value: float, *, max_level: int = 8) -> float:
    if value <= 0.0:
        return 0.0
    if value >= 1.0:
        return 1.0
    for level in range(1, max_level + 1):
        boundary = 1.0 - 1.0 / (2**level)
        if value <= boundary:
            return boundary
    return 1.0 - 1.0 / (2**max_level)
