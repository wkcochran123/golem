from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal


ProjectionKind = Literal["distance", "goal", "orientation_2d", "orientation_3d", "occupancy"]
ThresholdLaw = Callable[[list[float]], float]
UrgencyLaw = Callable[[list[float]], float]


@dataclass(frozen=True)
class ProjectionMap:
    kind: ProjectionKind
    width: int
    height: int
    values: tuple[float, ...]
    threshold: float
    calibration: str

    @staticmethod
    def from_rows(
        kind: ProjectionKind,
        rows: list[list[float]],
        *,
        threshold: float,
        calibration: str,
    ) -> "ProjectionMap":
        if not rows or not rows[0]:
            raise ValueError("Projection rows must be non-empty.")
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError("Projection rows must have equal width.")
        return ProjectionMap(
            kind=kind,
            width=width,
            height=len(rows),
            values=tuple(value for row in rows for value in row),
            threshold=threshold,
            calibration=calibration,
        )

    def filtered(self) -> tuple[float, ...]:
        return tuple(value if value >= self.threshold else 0.0 for value in self.values)

    def active_count(self) -> int:
        return sum(1 for value in self.values if value >= self.threshold)


@dataclass(frozen=True)
class LatchState:
    name: str
    projection_kind: ProjectionKind
    threshold: float
    urgency: float
    active_count: int
    velocity: float
    sample_score: float
    trial_score: float
    ema: tuple[float, ...]
    latched: bool

    def to_payload(self) -> dict:
        return {
            "name": self.name,
            "projection_kind": self.projection_kind,
            "threshold": self.threshold,
            "urgency": self.urgency,
            "active_count": self.active_count,
            "velocity": self.velocity,
            "sample_score": self.sample_score,
            "trial_score": self.trial_score,
            "latched": self.latched,
        }


class ProjectionLatch:
    """Simple latch over one known projection shape."""

    def __init__(
        self,
        name: str,
        projection_kind: ProjectionKind,
        *,
        parent_thresholds: list[float],
        threshold_law: ThresholdLaw,
        urgency_law: UrgencyLaw | None = None,
        ema_alpha: float | None = None,
        latch_min_active: int = 1,
    ):
        self.name = name
        self.projection_kind = projection_kind
        self.parent_thresholds = parent_thresholds
        self.threshold_law = threshold_law
        self.urgency_law = urgency_law or total_urgency_law
        self.ema_alpha = ema_alpha
        self.latch_min_active = latch_min_active
        self._ema: tuple[float, ...] | None = None

    def update(self, projection: ProjectionMap) -> LatchState:
        if projection.kind != self.projection_kind:
            raise ValueError(
                f"Latch {self.name} expects {self.projection_kind}, got {projection.kind}."
            )
        threshold = self.threshold_law(self.parent_thresholds)
        urgency = self.ema_alpha if self.ema_alpha is not None else self.urgency_law(self.parent_thresholds)
        projection = ProjectionMap(
            kind=projection.kind,
            width=projection.width,
            height=projection.height,
            values=projection.values,
            threshold=threshold,
            calibration=projection.calibration,
        )
        filtered = projection.filtered()
        ema = self._update_ema(filtered, urgency)
        velocity = self._sample_trial_velocity(filtered, ema)
        active_count = sum(1 for value in filtered if value != 0.0)
        state = LatchState(
            name=self.name,
            projection_kind=self.projection_kind,
            threshold=threshold,
            urgency=urgency,
            active_count=active_count,
            velocity=velocity,
            sample_score=sum(filtered),
            trial_score=sum(ema),
            ema=ema,
            latched=active_count >= self.latch_min_active,
        )
        return state

    def _update_ema(self, current: tuple[float, ...], urgency: float) -> tuple[float, ...]:
        if self._ema is None:
            self._ema = current
            return current
        self._ema = tuple(
            urgency * value + (1.0 - urgency) * prior
            for value, prior in zip(current, self._ema, strict=True)
        )
        return self._ema

    @staticmethod
    def _sample_trial_velocity(sample: tuple[float, ...], trial: tuple[float, ...]) -> float:
        delta = sum(abs(value - prior) for value, prior in zip(sample, trial, strict=True))
        return delta / len(sample)


def min_law(values: list[float]) -> float:
    return min(values)


def max_law(values: list[float]) -> float:
    return max(values)


def mean_law(values: list[float]) -> float:
    return sum(values) / len(values)


def total_urgency_law(values: list[float]) -> float:
    """Allocate a fixed level urgency budget across parent thresholds."""

    if not values:
        return 0.5
    return max(0.0, min(0.5, sum(values)))


def split_urgency(total: float, parts: int) -> list[float]:
    if parts <= 0:
        raise ValueError("parts must be positive.")
    total = max(0.0, min(0.5, total))
    share = total / parts
    return [share for _ in range(parts)]
