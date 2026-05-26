from __future__ import annotations

from .types import PolicyInput
from ..actions import ActionRequest


class ScriptedPolicy:
    """Deterministic policy stub with the same output shape an LLM should use."""

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        if not policy_input.graph_summary["edges"]:
            return ActionRequest(
                action_type="write_text",
                path="observation.md",
                text="# First residue\n\nThe world was empty, so the policy created a marker.\n",
                rationale="Create residue so sensors and salience have something to observe.",
            )

        return ActionRequest(
            action_type="append_text",
            path="observation.md",
            text="\nThe graph now contains evidence of a prior residue.\n",
            rationale="Refine the existing artifact based on graph feedback.",
        )

