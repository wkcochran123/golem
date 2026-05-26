from __future__ import annotations

import json

from ..robot.motors import MotorCommand, MotorResult, RealMotorExecutor


class FakeMotorDriver:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, command: MotorCommand) -> MotorResult:
        self.sent.append(command.to_payload())
        return MotorResult(
            ok=True,
            command=command,
            message="Fake driver accepted command.",
        )


def main() -> None:
    driver = FakeMotorDriver()
    executor = RealMotorExecutor(
        driver,
        max_speed=0.2,
        max_duration=0.4,
        hard_stop_distance=0.15,
    )
    attempts = [
        {
            "label": "safe_forward",
            "command": MotorCommand("forward", speed=0.12, duration=0.2),
            "distances": [0.8, 0.7, 1.0],
        },
        {
            "label": "too_close",
            "command": MotorCommand("forward", speed=0.12, duration=0.2),
            "distances": [0.1, 0.7, 1.0],
        },
        {
            "label": "too_fast",
            "command": MotorCommand("turn_left", speed=0.25, duration=0.2),
            "distances": [0.8, 0.7, 1.0],
        },
        {
            "label": "too_long",
            "command": MotorCommand("turn_right", speed=0.12, duration=0.5),
            "distances": [0.8, 0.7, 1.0],
        },
        {
            "label": "explicit_stop_near_obstacle",
            "command": MotorCommand("stop"),
            "distances": [0.1, 0.7, 1.0],
        },
    ]
    results = [
        {
            "label": attempt["label"],
            "result": executor.execute(
                attempt["command"],
                attempt["distances"],
            ).to_payload(),
        }
        for attempt in attempts
    ]
    print(
        json.dumps(
            {
                "results": results,
                "driver_received": driver.sent,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
