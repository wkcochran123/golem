from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class CameraReading:
    frame: list[list[int]]
    width: int
    height: int
    captured_at: str = ""

    def __post_init__(self) -> None:
        if not self.captured_at:
            object.__setattr__(self, "captured_at", datetime.now(timezone.utc).isoformat())
        _validate_frame_shape(self.frame, self.width, self.height)

    def age_seconds(self, now: datetime | None = None) -> float:
        now = now or datetime.now(timezone.utc)
        captured = datetime.fromisoformat(self.captured_at)
        if captured.tzinfo is None:
            captured = captured.replace(tzinfo=timezone.utc)
        return max(0.0, (now - captured).total_seconds())

    def to_payload(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "captured_at": self.captured_at,
            "frame": self.frame,
        }


class CameraDriver(Protocol):
    def read(self) -> CameraReading:
        ...


class CameraRing:
    def __init__(
        self,
        driver: CameraDriver,
        width: int,
        height: int,
        *,
        max_age_seconds: float | None = None,
    ):
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive.")
        if max_age_seconds is not None and max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative.")
        self.driver = driver
        self.width = width
        self.height = height
        self.max_age_seconds = max_age_seconds

    def read(self) -> CameraReading:
        reading = self.driver.read()
        if reading.width != self.width or reading.height != self.height:
            raise ValueError(
                f"Expected camera frame {self.width}x{self.height}, "
                f"got {reading.width}x{reading.height}."
            )
        _validate_frame_shape(reading.frame, self.width, self.height)
        self._validate_freshness(reading)
        return reading

    def _validate_freshness(self, reading: CameraReading) -> None:
        if self.max_age_seconds is None:
            return
        if reading.age_seconds() > self.max_age_seconds:
            raise ValueError(f"Stale camera frame; max_age_seconds={self.max_age_seconds}.")


class FakeCameraDriver:
    def __init__(self, frames: list[list[list[int]]], *, captured_at: str = ""):
        if not frames:
            raise ValueError("frames must not be empty.")
        self.frames = frames
        self.captured_at = captured_at
        self.index = 0

    def read(self) -> CameraReading:
        frame = self.frames[self.index % len(self.frames)]
        self.index += 1
        height = len(frame)
        width = len(frame[0]) if height else 0
        return CameraReading(frame, width, height, captured_at=self.captured_at)


def _validate_frame_shape(frame: list[list[int]], width: int, height: int) -> None:
    if len(frame) != height:
        raise ValueError(f"Expected frame height {height}, got {len(frame)}.")
    if any(len(row) != width for row in frame):
        raise ValueError(f"Expected every frame row to have width {width}.")
