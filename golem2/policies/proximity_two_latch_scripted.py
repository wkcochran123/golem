from __future__ import annotations

from ..actions import ActionRequest
from .types import PolicyInput


class ScriptedProximityTwoLatchPolicy:
    """Offline stand-in for LM Studio that handles two regime thresholds.

    Reacts to two exception kinds from policy_input.task_state['llm_visible']:

    - `front_obstacle_latched`: the obstacle gate fired.
      Response: raise `front_obstacle_risk` threshold (latch becomes less
      sensitive to marginal obstacles), shed a bit of urgency to make
      room within the regime's urgency budget for the clear-path
      threshold.

    - `clear_path_latched`: the clear-path gate fired (lots of free
      cells visible, environment is calm).
      Response: lower `clear_path_low` threshold (latch becomes more
      sensitive to clear paths, so we keep noticing calm conditions),
      restore a small amount of urgency.

    Obstacle takes priority when both fire in the same tick (safety-first).
    """

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        visible = policy_input.task_state.get("llm_visible", [])
        reasons = {event.get("reason", "") for event in visible}

        if "front_obstacle_latched" in reasons:
            return ActionRequest(
                action_type="adjust_threshold",
                threshold_name="front_obstacle_risk",
                threshold_delta=0.1,
                urgency_delta=-0.05,
                rationale=(
                    "Obstacle latch fired; raise risk threshold so reflex policy "
                    "stops twitching on marginal cells, shed urgency to keep "
                    "headroom in the regime budget."
                ),
            )
        if "clear_path_latched" in reasons:
            # Urgency-neutral: budget is conserved, so this adjustment always
            # passes the RegimeManager budget check regardless of starting state.
            # Threshold-only is enough to keep noticing calm conditions; restoring
            # urgency is left to the obstacle-side adjustment's shed-and-recycle
            # pattern across multi-tick runs.
            return ActionRequest(
                action_type="adjust_threshold",
                threshold_name="clear_path_low",
                threshold_delta=-0.05,
                urgency_delta=0.0,
                rationale=(
                    "Clear-path latch fired; environment is calm, so lower the "
                    "clear-path threshold to keep noticing calm conditions. "
                    "Urgency unchanged to stay within budget."
                ),
            )
        return ActionRequest(
            action_type="noop",
            rationale="No exceptional proximity event is visible to the policy.",
        )
