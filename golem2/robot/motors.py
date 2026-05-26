from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


MotorCommandType = Literal["forward", "turn_left", "turn_right", "stop"]


@dataclass(frozen=True)
class MotorCommand:
    command: MotorCommandType
    speed: float = 0.0
    duration: float = 0.0
    rationale: str = ""

    def to_payload(self) -> dict:
        return {
            "command": self.command,
            "speed": self.speed,
            "duration": self.duration,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class MotorResult:
    ok: bool
    command: MotorCommand
    message: str
    forced_stop: bool = False

    def to_payload(self) -> dict:
        return {
            "ok": self.ok,
            "command": self.command.to_payload(),
            "message": self.message,
            "forced_stop": self.forced_stop,
        }


class MotorDriver(Protocol):
    """Hardware adapter used by RealMotorExecutor after safety gates pass."""

    def send(self, command: MotorCommand) -> MotorResult:
        ...


class MotorSafetyGate:
    def __init__(
        self,
        *,
        max_speed: float = 0.25,
        max_duration: float = 0.5,
        hard_stop_distance: float = 0.15,
    ):
        self.max_speed = max_speed
        self.max_duration = max_duration
        self.hard_stop_distance = hard_stop_distance

    def check(self, command: MotorCommand, distances: list[float]) -> MotorResult | None:
        nearest = min(distances) if distances else 0.0
        if nearest < self.hard_stop_distance and command.command != "stop":
            return MotorResult(
                ok=False,
                command=MotorCommand(
                    "stop",
                    rationale="Hard distance gate forced stop before motor command.",
                ),
                message=f"Nearest obstacle {nearest} below hard stop {self.hard_stop_distance}.",
                forced_stop=True,
            )
        if command.speed > self.max_speed:
            return MotorResult(
                ok=False,
                command=MotorCommand("stop", rationale="Speed cap forced stop."),
                message=f"Requested speed {command.speed} exceeds cap {self.max_speed}.",
                forced_stop=True,
            )
        if command.duration > self.max_duration:
            return MotorResult(
                ok=False,
                command=MotorCommand("stop", rationale="Duration cap forced stop."),
                message=f"Requested duration {command.duration} exceeds cap {self.max_duration}.",
                forced_stop=True,
            )
        return None


class SimulatedMotorExecutor:
    """Safety-checked motor executor that does not touch real hardware."""

    def __init__(
        self,
        *,
        max_speed: float = 0.25,
        max_duration: float = 0.5,
        hard_stop_distance: float = 0.15,
    ):
        self.safety_gate = MotorSafetyGate(
            max_speed=max_speed,
            max_duration=max_duration,
            hard_stop_distance=hard_stop_distance,
        )

    def execute(self, command: MotorCommand, distances: list[float]) -> MotorResult:
        safety_result = self.safety_gate.check(command, distances)
        if safety_result is not None:
            return safety_result
        return MotorResult(ok=True, command=command, message="Simulated motor command accepted.")


class RealMotorExecutor:
    """Safety-checked motor executor for Pi-side hardware drivers.

    Hardware-specific GPIO, PWM, or serial code lives behind `driver`; this
    executor owns only the common safety gates and the executor contract.
    """

    def __init__(
        self,
        driver: MotorDriver,
        *,
        max_speed: float = 0.25,
        max_duration: float = 0.5,
        hard_stop_distance: float = 0.15,
    ):
        self.driver = driver
        self.safety_gate = MotorSafetyGate(
            max_speed=max_speed,
            max_duration=max_duration,
            hard_stop_distance=hard_stop_distance,
        )

    def execute(self, command: MotorCommand, distances: list[float]) -> MotorResult:
        safety_result = self.safety_gate.check(command, distances)
        if safety_result is not None:
            return safety_result
        return self.driver.send(command)
