from __future__ import annotations

import math
import random


class VisionMLP:
    def __init__(self, input_h: int, input_w: int, hidden: int, output: int, seed: int = 0):
        if min(input_h, input_w, hidden, output) <= 0:
            raise ValueError("dimensions must be positive.")
        self.input_h = input_h
        self.input_w = input_w
        self.hidden = hidden
        self.output = output
        rng = random.Random(seed)
        scale_in = 1.0 / math.sqrt(input_h * input_w)
        scale_hidden = 1.0 / math.sqrt(hidden)
        self.w1 = [
            [rng.uniform(-scale_in, scale_in) for _ in range(input_h * input_w)]
            for _ in range(hidden)
        ]
        self.b1 = [rng.uniform(-scale_in, scale_in) for _ in range(hidden)]
        self.w2 = [
            [rng.uniform(-scale_hidden, scale_hidden) for _ in range(hidden)]
            for _ in range(output)
        ]
        self.b2 = [rng.uniform(-scale_hidden, scale_hidden) for _ in range(output)]

    def predict(self, frame: list[list[int]]) -> list[float]:
        if len(frame) != self.input_h or any(len(row) != self.input_w for row in frame):
            raise ValueError(f"expected frame shape {self.input_h}x{self.input_w}.")
        flat = [value / 2.0 for row in frame for value in row]
        hidden_values = [
            max(0.0, sum(weight * value for weight, value in zip(weights, flat, strict=True)) + bias)
            for weights, bias in zip(self.w1, self.b1, strict=True)
        ]
        return [
            sum(weight * value for weight, value in zip(weights, hidden_values, strict=True)) + bias
            for weights, bias in zip(self.w2, self.b2, strict=True)
        ]
