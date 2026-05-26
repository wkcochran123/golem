from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class RegimeThreshold:
    name: str
    projection: str
    current_value: float
    threshold: float
    urgency: float
    min_threshold: float | None = None
    max_threshold: float | None = None
    min_urgency: float = 0.0
    max_urgency: float = 0.5
    units: str = ""

    def to_payload(self) -> dict:
        return {
            "name": self.name,
            "projection": self.projection,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "urgency": self.urgency,
            "min_threshold": self.min_threshold,
            "max_threshold": self.max_threshold,
            "min_urgency": self.min_urgency,
            "max_urgency": self.max_urgency,
            "units": self.units,
        }


@dataclass(frozen=True)
class ThresholdAdjustment:
    threshold_name: str
    threshold_delta: float = 0.0
    urgency_delta: float = 0.0
    rationale: str = ""

    def to_payload(self) -> dict:
        return {
            "threshold_name": self.threshold_name,
            "threshold_delta": self.threshold_delta,
            "urgency_delta": self.urgency_delta,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class PolicyRegime:
    name: str
    objective: str
    thresholds: list[RegimeThreshold]
    unstructured_context: dict = field(default_factory=dict)
    allowed_actions: list[str] = field(default_factory=list)
    control_style: str = "threshold_joystick"

    def to_payload(self, *, max_thresholds: int | None = None) -> dict:
        thresholds = self.thresholds
        if max_thresholds is not None:
            thresholds = thresholds[:max_thresholds]
        return {
            "name": self.name,
            "objective": self.objective,
            "thresholds": [threshold.to_payload() for threshold in thresholds],
            "unstructured_context": self.unstructured_context,
            "allowed_actions": self.allowed_actions,
            "control_style": self.control_style,
        }


@dataclass(frozen=True)
class PolicyInputLimits:
    max_graph_edges: int = 100
    max_recent_failures: int = 20
    max_policy_hints: int = 50
    max_regimes: int = 8
    max_thresholds_per_regime: int = 16

    def __post_init__(self) -> None:
        for name, value in self.to_payload().items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative.")

    def to_payload(self) -> dict[str, int]:
        return {
            "max_graph_edges": self.max_graph_edges,
            "max_recent_failures": self.max_recent_failures,
            "max_policy_hints": self.max_policy_hints,
            "max_regimes": self.max_regimes,
            "max_thresholds_per_regime": self.max_thresholds_per_regime,
        }


@dataclass(frozen=True)
class PolicyInput:
    graph_summary: dict
    recent_failures: list[dict]
    available_actions: list[str]
    policy_hints: list[str]
    task_state: dict = field(default_factory=dict)
    regimes: list[PolicyRegime] = field(default_factory=list)

    def to_payload(self, limits: PolicyInputLimits | None = None) -> dict:
        graph_summary = self.graph_summary
        recent_failures = self.recent_failures
        policy_hints = self.policy_hints
        regimes = self.regimes
        metadata: dict | None = None

        if limits is not None:
            graph_summary, graph_truncation = _limit_graph_summary(
                self.graph_summary,
                max_edges=limits.max_graph_edges,
            )
            recent_failures, failure_truncation = _limit_list(
                self.recent_failures,
                limits.max_recent_failures,
            )
            policy_hints, hint_truncation = _limit_list(
                self.policy_hints,
                limits.max_policy_hints,
            )
            regimes, regime_truncation = _limit_list(
                self.regimes,
                limits.max_regimes,
            )
            metadata = {
                "limits": limits.to_payload(),
                "truncated": {
                    "graph_edges": graph_truncation,
                    "recent_failures": failure_truncation,
                    "policy_hints": hint_truncation,
                    "regimes": regime_truncation,
                    "thresholds_per_regime": [
                        _truncation_count(
                            len(regime.thresholds),
                            limits.max_thresholds_per_regime,
                        )
                        for regime in regimes
                    ],
                },
            }

        payload = {
            "graph_summary": graph_summary,
            "recent_failures": recent_failures,
            "available_actions": self.available_actions,
            "policy_hints": policy_hints,
            "task_state": self.task_state,
            "regimes": [
                regime.to_payload(
                    max_thresholds=(
                        limits.max_thresholds_per_regime
                        if limits is not None
                        else None
                    )
                )
                for regime in regimes
            ],
        }
        if metadata is not None:
            payload["context_window"] = metadata
        return payload


def _limit_graph_summary(
    graph_summary: dict,
    *,
    max_edges: int,
) -> tuple[dict, int]:
    edges = graph_summary.get("edges")
    if not isinstance(edges, list):
        return graph_summary, 0
    limited = dict(graph_summary)
    limited["edges"] = edges[-max_edges:] if max_edges else []
    return limited, _truncation_count(len(edges), max_edges)


def _limit_list(items: list[T], max_items: int) -> tuple[list[T], int]:
    return (items[-max_items:] if max_items else []), _truncation_count(
        len(items),
        max_items,
    )


def _truncation_count(total: int, limit: int) -> int:
    return max(0, total - limit)
