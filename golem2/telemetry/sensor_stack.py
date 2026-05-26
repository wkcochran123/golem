from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from .snapshot import TelemetrySnapshot


SensorCommandName = Literal[
    "set_alpha",
    "set_lower_bound",
    "set_upper_bound",
    "nudge_up",
    "nudge_down",
    "grow_spread",
    "shrink_spread",
]


@dataclass(frozen=True)
class SensorCommand:
    name: SensorCommandName
    value: float
    rationale: str = ""

    def to_payload(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class SensorKnobs:
    alpha: float = 0.5
    lower_bound: float = 0.0
    upper_bound: float = 1.0
    nudge_step: float = 0.05
    spread_step: float = 0.05

    def to_payload(self) -> dict:
        return {
            "alpha": self.alpha,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "nudge_step": self.nudge_step,
            "spread_step": self.spread_step,
        }


class StackedSensor:
    """A tiny telemetry sensor that can be stacked on top of other sensors.

    The child values are averaged, clipped into a tunable band, then smoothed
    with an EMA. The exposed commands are deliberately small and bounded so an
    LLM or notebook UI can steer attention without directly controlling motors.
    """

    def __init__(
        self,
        name: str,
        *,
        kind: str,
        knobs: SensorKnobs | None = None,
    ):
        self.name = name
        self.kind = kind
        self.knobs = knobs or SensorKnobs()
        self._ema: float | None = None

    def apply(self, snapshots: list[TelemetrySnapshot]) -> TelemetrySnapshot:
        if not snapshots:
            raise ValueError("StackedSensor.apply requires at least one child snapshot.")
        raw_value = sum(_snapshot_value(snapshot) for snapshot in snapshots) / len(snapshots)
        clipped_value = max(self.knobs.lower_bound, min(self.knobs.upper_bound, raw_value))
        if self._ema is None:
            self._ema = clipped_value
        else:
            self._ema = self.knobs.alpha * clipped_value + (1.0 - self.knobs.alpha) * self._ema
        return TelemetrySnapshot.capture(
            self.name,
            self.kind,
            {
                "value": self._ema,
                "raw_value": raw_value,
                "clipped_value": clipped_value,
                "child_snapshot_ids": [snapshot.id for snapshot in snapshots],
                "knobs": self.knobs.to_payload(),
            },
        )

    def execute(self, command: SensorCommand) -> TelemetrySnapshot:
        self.knobs = _apply_command(self.knobs, command)
        return TelemetrySnapshot.capture(
            self.name,
            "sensor_control",
            {
                "command": command.to_payload(),
                "knobs": self.knobs.to_payload(),
            },
        )


def scalar_snapshot(component: str, kind: str, value: float, **extra: object) -> TelemetrySnapshot:
    payload = {"value": value, **extra}
    return TelemetrySnapshot.capture(component, kind, payload)


def _apply_command(knobs: SensorKnobs, command: SensorCommand) -> SensorKnobs:
    if command.name == "set_alpha":
        return replace(knobs, alpha=_clamp(command.value, 0.0, 1.0))
    if command.name == "set_lower_bound":
        return _with_bounds(knobs, lower=command.value, upper=knobs.upper_bound)
    if command.name == "set_upper_bound":
        return _with_bounds(knobs, lower=knobs.lower_bound, upper=command.value)
    if command.name == "nudge_up":
        amount = command.value or knobs.nudge_step
        return _with_bounds(
            knobs,
            lower=knobs.lower_bound + amount,
            upper=knobs.upper_bound + amount,
        )
    if command.name == "nudge_down":
        amount = command.value or knobs.nudge_step
        return _with_bounds(
            knobs,
            lower=knobs.lower_bound - amount,
            upper=knobs.upper_bound - amount,
        )
    if command.name == "grow_spread":
        amount = command.value or knobs.spread_step
        return _with_bounds(
            knobs,
            lower=knobs.lower_bound - amount,
            upper=knobs.upper_bound + amount,
        )
    if command.name == "shrink_spread":
        amount = command.value or knobs.spread_step
        return _with_bounds(
            knobs,
            lower=knobs.lower_bound + amount,
            upper=knobs.upper_bound - amount,
        )
    raise ValueError(f"Unknown sensor command: {command.name}")


def _with_bounds(knobs: SensorKnobs, *, lower: float, upper: float) -> SensorKnobs:
    if lower > upper:
        midpoint = (lower + upper) / 2
        lower = midpoint
        upper = midpoint
    return replace(knobs, lower_bound=lower, upper_bound=upper)


def _snapshot_value(snapshot: TelemetrySnapshot) -> float:
    payload = snapshot.payload
    for key in ("value", "score", "sample_score", "risk", "coverage"):
        value = payload.get(key)
        if isinstance(value, int | float):
            return float(value)
    raise ValueError(
        f"Snapshot {snapshot.component}/{snapshot.kind} does not expose a scalar value."
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
