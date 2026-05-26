from __future__ import annotations

from ..actions import ActionRequest
from .file_sort_scripted import ScriptedFileSortPolicy
from .types import PolicyInput


class ScriptedRecoveryPolicy:
    """Proves failure -> graph -> policy recovery without an LLM."""

    def __init__(self):
        self.sort_policy = ScriptedFileSortPolicy()

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        saw_path_escape = any(
            failure["failure"] == "path_escape"
            for failure in policy_input.recent_failures
        )
        if not saw_path_escape:
            return ActionRequest(
                action_type="move_file",
                path="../escape.txt",
                target_path="animals/cat.txt",
                rationale="Deliberately trigger path_escape to test graph recovery.",
            )
        return self.sort_policy.choose(policy_input)

