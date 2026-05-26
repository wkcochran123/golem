from __future__ import annotations

from ..actions import ActionRequest
from .types import PolicyInput


class ScriptedProximityRegimePolicy:
    """Offline stand-in for LM Studio emitting threshold-control actions."""

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        for visible_event in policy_input.task_state.get("llm_visible", []):
            if visible_event.get("reason") == "front_obstacle_latched":
                return ActionRequest(
                    action_type="adjust_threshold",
                    threshold_name="front_obstacle_risk",
                    threshold_delta=0.1,
                    urgency_delta=-0.1,
                    rationale=(
                        "Obstacle latch is firing; reduce reflex urgency and raise the "
                        "risk threshold so local control becomes calmer."
                    ),
                )
        return ActionRequest(
            action_type="noop",
            rationale="No exceptional proximity event is visible to the policy.",
        )
