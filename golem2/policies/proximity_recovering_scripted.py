from __future__ import annotations

from ..actions import ActionRequest
from .proximity_two_latch_scripted import ScriptedProximityTwoLatchPolicy
from .types import PolicyInput


class ScriptedProximityRecoveringPolicy:
    """Two-latch policy with frame-counted symmetric tighten-back (U1).

    Wraps `ScriptedProximityTwoLatchPolicy`. When an exception is visible,
    delegates to the inner policy (raises obstacle threshold or lowers
    clear-path threshold per the existing rules). When no exception has
    been visible for `frames_until_revert` consecutive frames, emits a
    small revert adjustment that pulls `front_obstacle_risk` back toward
    its baseline (smaller threshold = stricter obstacle detection).

    This closes the "thresholds drift open indefinitely on multi-minute
    runs" gap noted in earlier audits. The inner policy still owns all
    exception-driven adjustments; this wrapper only adds calm-period
    recovery.

    Bounds: revert delta is small (`revert_step`) and `RegimeManager`
    clamps to `min_threshold` on `RegimeThreshold`, so reverts can never
    push threshold below the configured floor.
    """

    def __init__(
        self,
        inner: ScriptedProximityTwoLatchPolicy | None = None,
        *,
        frames_until_revert: int = 3,
        revert_step: float = 0.02,
    ):
        if frames_until_revert < 1:
            raise ValueError("frames_until_revert must be >= 1.")
        if revert_step < 0:
            raise ValueError("revert_step must be non-negative.")
        self.inner = inner or ScriptedProximityTwoLatchPolicy()
        self.frames_until_revert = frames_until_revert
        self.revert_step = revert_step
        self._frames_since_exception = 0

    @property
    def frames_since_exception(self) -> int:
        return self._frames_since_exception

    # Negative exceptions reset the recovery counter (the system is actively
    # in trouble). Positive exceptions like `clear_path_latched` do not reset
    # the counter — they're affirming calm. But positive exceptions still
    # get the inner policy's response this tick (one action per tick), so
    # recovery only fires on PURE silent ticks past the horizon.
    NEGATIVE_REASONS = frozenset({"front_obstacle_latched"})

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        visible = policy_input.task_state.get("llm_visible", [])
        reasons = {event.get("reason", "") for event in visible}

        if reasons & self.NEGATIVE_REASONS:
            # Active trouble: reset counter, delegate to inner.
            self._frames_since_exception = 0
            return self.inner.choose(policy_input)

        # No active trouble this tick — recovery counter advances regardless
        # of whether positive exceptions (clear_path_latched) are visible.
        self._frames_since_exception += 1

        if reasons:
            # Positive exception present (e.g. clear_path_latched). Inner
            # policy gets the action slot this tick; recovery waits.
            return self.inner.choose(policy_input)

        if self._frames_since_exception > self.frames_until_revert:
            # Pure silence past the horizon: pull obstacle threshold back
            # toward baseline. RegimeManager clamps at min_threshold so this
            # can never push below the safe floor.
            return ActionRequest(
                action_type="adjust_threshold",
                threshold_name="front_obstacle_risk",
                threshold_delta=-self.revert_step,
                urgency_delta=0.0,
                rationale=(
                    f"No exception for {self._frames_since_exception} silent frames; "
                    f"tightening obstacle threshold back toward baseline by "
                    f"{self.revert_step}."
                ),
            )

        return ActionRequest(
            action_type="noop",
            rationale=(
                f"Silent tick {self._frames_since_exception}/{self.frames_until_revert}; "
                f"holding thresholds until revert horizon."
            ),
        )
