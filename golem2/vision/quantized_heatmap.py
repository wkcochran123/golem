from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class HeatCell:
    r: int
    g: int
    b: int

    def score(self, weights: tuple[float, float, float]) -> float:
        return self.r * weights[0] + self.g * weights[1] + self.b * weights[2]


@dataclass(frozen=True)
class HeatMap:
    width: int
    height: int
    cells: tuple[HeatCell, ...]
    threshold: float
    calibration: str

    @staticmethod
    def from_sensor_grid(
        values: list[list[float]],
        *,
        threshold: float = 0.0,
        calibration: str = "sign(value - threshold)",
        neutral_zero: bool = False,
    ) -> "HeatMap":
        if not values or not values[0]:
            raise ValueError("Sensor grid must be non-empty.")
        width = len(values[0])
        if any(len(row) != width for row in values):
            raise ValueError("Sensor grid rows must have equal width.")

        cells: list[HeatCell] = []
        for y, row in enumerate(values):
            for x, value in enumerate(row):
                if neutral_zero and value == threshold:
                    sign = 0
                else:
                    sign = 1 if value >= threshold else -1
                blue = _balanced_blue(x, y, threshold, calibration)
                cells.append(
                    HeatCell(
                        r=-1 if sign < 0 else 0,
                        g=1 if sign > 0 else 0,
                        b=blue,
                    )
                )
        return HeatMap(
            width=width,
            height=len(values),
            cells=tuple(cells),
            threshold=threshold,
            calibration=calibration,
        )

    def total_score(self, weights: tuple[float, float, float] = (1.0, 1.0, 0.0)) -> float:
        # Blue is a calibration/reference channel; it stays out of comparable
        # score until a learned optical weighting has a reason to use it.
        return sum(cell.score(weights) for cell in self.cells)

    def compare(
        self,
        other: "HeatMap",
        *,
        weights: tuple[float, float, float] = (1.0, 1.0, 0.0),
        threshold: float = 1.0,
    ) -> dict:
        if self.width != other.width or self.height != other.height:
            raise ValueError("Heat maps must have matching dimensions.")
        before = self.total_score(weights)
        after = other.total_score(weights)
        delta = after - before
        changed_cells = self.changed_cells(other)
        average_delta = delta / len(self.cells)
        return {
            "before_score": before,
            "after_score": after,
            "delta": delta,
            "increased": delta > 0,
            "decreased": delta < 0,
            "stable": delta == 0,
            "score_stable_but_cells_changed": delta == 0 and bool(changed_cells),
            "average_delta": average_delta,
            "strain": average_delta,
            "threshold": threshold,
            "threshold_crossed": abs(delta) >= threshold,
            "calibration": other.calibration,
            "changed_cell_count": len(changed_cells),
        }

    def changed_cells(self, other: "HeatMap") -> list[dict]:
        if self.width != other.width or self.height != other.height:
            raise ValueError("Heat maps must have matching dimensions.")
        changes: list[dict] = []
        for index, (left, right) in enumerate(zip(self.cells, other.cells, strict=True)):
            if left == right:
                continue
            changes.append(
                {
                    "x": index % self.width,
                    "y": index // self.width,
                    "before": {"r": left.r, "g": left.g, "b": left.b},
                    "after": {"r": right.r, "g": right.g, "b": right.b},
                }
            )
        return changes

    def write_ppm(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="ascii") as handle:
            handle.write(f"P3\n{self.width} {self.height}\n255\n")
            for row in _chunks(self.cells, self.width):
                parts = []
                for cell in row:
                    parts.append(
                        f"{_channel_to_byte(cell.r, negative_is_visible=True)} "
                        f"{_channel_to_byte(cell.g)} "
                        f"{_blue_to_byte(cell.b)}"
                    )
                handle.write("  ".join(parts) + "\n")


def _balanced_blue(x: int, y: int, threshold: float, calibration: str) -> int:
    digest = sha256(f"{x}:{y}:{threshold}:{calibration}".encode("utf-8")).digest()
    return 1 if digest[0] < 128 else -1


def _channel_to_byte(value: int, *, negative_is_visible: bool = False) -> int:
    if value > 0:
        return 255
    if value < 0:
        return 255 if negative_is_visible else 0
    return 0


def _blue_to_byte(value: int) -> int:
    return 128 + 127 * value


def _chunks(items: Iterable[HeatCell], size: int) -> Iterable[tuple[HeatCell, ...]]:
    row: list[HeatCell] = []
    for item in items:
        row.append(item)
        if len(row) == size:
            yield tuple(row)
            row = []
