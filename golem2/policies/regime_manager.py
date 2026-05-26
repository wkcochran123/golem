from __future__ import annotations

from dataclasses import replace
from typing import Callable

from ..actions import ActionRequest, ActionResult
from ..events import event
from ..graph import KnowledgeGraph
from ..store import EventLog
from ..vision.latches import ProjectionLatch
from .types import PolicyRegime, RegimeThreshold


class RegimeManager:
    """Applies bounded threshold-control actions to policy regimes."""

    def __init__(
        self,
        regimes: list[PolicyRegime],
        graph: KnowledgeGraph | None = None,
        event_log: EventLog | None = None,
        adjustment_cooldown_steps: int = 0,
    ):
        if adjustment_cooldown_steps < 0:
            raise ValueError("adjustment_cooldown_steps must be non-negative.")
        self.regimes = {regime.name: regime for regime in regimes}
        self.graph = graph
        self.event_log = event_log
        self.adjustment_cooldown_steps = adjustment_cooldown_steps
        self._callbacks: dict[tuple[str, str], list[Callable[[RegimeThreshold], None]]] = {}
        self._step_index = 0
        self._last_adjustment_step: dict[tuple[str, str], int] = {}

    def bind_callback(
        self,
        regime_name: str,
        threshold_name: str,
        callback: Callable[[RegimeThreshold], None],
    ) -> None:
        self._callbacks.setdefault((regime_name, threshold_name), []).append(callback)
        callback(self._find_threshold(regime_name, threshold_name))

    def bind_latch(
        self,
        regime_name: str,
        threshold_name: str,
        latch: ProjectionLatch,
        *,
        parent_index: int = 0,
    ) -> None:
        def update_latch(threshold: RegimeThreshold) -> None:
            if parent_index >= len(latch.parent_thresholds):
                raise IndexError("parent_index is outside latch.parent_thresholds.")
            latch.parent_thresholds[parent_index] = threshold.threshold
            latch.ema_alpha = threshold.urgency

        self.bind_callback(regime_name, threshold_name, update_latch)

    def execute(self, regime_name: str, request: ActionRequest) -> ActionResult:
        self._step_index += 1
        if request.action_type != "adjust_threshold":
            return self._record_result(
                regime_name,
                request,
                ActionResult(
                    ok=False,
                    message=f"RegimeManager cannot execute {request.action_type}.",
                    failure_kind="wrong_executor",
                ),
            )
        if request.threshold_name is None:
            return self._record_result(
                regime_name,
                request,
                ActionResult(
                    ok=False,
                    message="Missing threshold_name.",
                    failure_kind="missing_threshold_name",
                ),
            )
        regime = self.regimes.get(regime_name)
        if regime is None:
            return self._record_result(
                regime_name,
                request,
                ActionResult(
                    ok=False,
                    message=f"Unknown regime: {regime_name}",
                    failure_kind="unknown_regime",
                ),
            )

        threshold_key = (regime_name, request.threshold_name)
        last_step = self._last_adjustment_step.get(threshold_key)
        if (
            last_step is not None
            and self._step_index - last_step <= self.adjustment_cooldown_steps
        ):
            return self._record_result(
                regime_name,
                request,
                ActionResult(
                    ok=False,
                    message="Threshold adjustment rate-limited.",
                    failure_kind="adjustment_rate_limited",
                    data={
                        "threshold_name": request.threshold_name,
                        "current_step": self._step_index,
                        "last_adjustment_step": last_step,
                        "cooldown_steps": self.adjustment_cooldown_steps,
                    },
                ),
            )

        thresholds: list[RegimeThreshold] = []
        changed: RegimeThreshold | None = None
        for threshold in regime.thresholds:
            if threshold.name != request.threshold_name:
                thresholds.append(threshold)
                continue
            changed = _adjust_threshold(
                threshold,
                threshold_delta=request.threshold_delta,
                urgency_delta=request.urgency_delta,
            )
            thresholds.append(changed)

        if changed is None:
            return self._record_result(
                regime_name,
                request,
                ActionResult(
                    ok=False,
                    message=f"Unknown threshold: {request.threshold_name}",
                    failure_kind="unknown_threshold",
                ),
            )

        total_urgency = sum(threshold.urgency for threshold in thresholds)
        if total_urgency > 0.5:
            return self._record_result(
                regime_name,
                request,
                ActionResult(
                    ok=False,
                    message="Urgency budget exceeded.",
                    failure_kind="urgency_budget_exceeded",
                    data={"total_urgency": total_urgency, "budget": 0.5},
                ),
            )

        self.regimes[regime_name] = replace(regime, thresholds=thresholds)
        self._last_adjustment_step[threshold_key] = self._step_index
        for callback in self._callbacks.get((regime_name, changed.name), []):
            callback(changed)
        return self._record_result(
            regime_name,
            request,
            ActionResult(
                ok=True,
                message="Threshold adjustment applied.",
                data={
                    "regime": regime_name,
                    "threshold": changed.to_payload(),
                    "total_urgency": total_urgency,
                },
            ),
        )

    def _record_result(
        self,
        regime_name: str,
        request: ActionRequest,
        result: ActionResult,
    ) -> ActionResult:
        if self.event_log is not None:
            self.event_log.append(
                event(
                    "threshold_adjustment",
                    {
                        "regime": regime_name,
                        "request": request.to_payload(),
                        "result": result.to_payload(),
                    },
                )
            )
        if self.graph is not None:
            self.graph.record_threshold_adjustment(regime_name, request, result)
        return result

    def _find_threshold(self, regime_name: str, threshold_name: str) -> RegimeThreshold:
        regime = self.regimes.get(regime_name)
        if regime is None:
            raise ValueError(f"Unknown regime: {regime_name}")
        for threshold in regime.thresholds:
            if threshold.name == threshold_name:
                return threshold
        raise ValueError(f"Unknown threshold: {threshold_name}")


def _adjust_threshold(
    threshold: RegimeThreshold,
    *,
    threshold_delta: float,
    urgency_delta: float,
) -> RegimeThreshold:
    next_threshold = threshold.threshold + threshold_delta
    if threshold.min_threshold is not None:
        next_threshold = max(threshold.min_threshold, next_threshold)
    if threshold.max_threshold is not None:
        next_threshold = min(threshold.max_threshold, next_threshold)
    next_urgency = max(
        threshold.min_urgency,
        min(threshold.max_urgency, threshold.urgency + urgency_delta),
    )
    return replace(threshold, threshold=next_threshold, urgency=next_urgency)
