from __future__ import annotations

from ..actions import ActionRequest
from .types import PolicyInput


class ScriptedFileSortPolicy:
    """Small deterministic policy for proving the graded loop can climb."""

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        grade = policy_input.task_state.get("grade", {})
        if grade.get("score", 0.0) >= 1.0:
            return ActionRequest(
                action_type="done",
                rationale="All snippets are sorted correctly.",
            )

        existing_paths = {
            file_info["path"]
            for file_info in policy_input.task_state.get("files", [])
            if file_info["kind"] == "file"
        }
        existing_dirs = {
            file_info["path"]
            for file_info in policy_input.task_state.get("files", [])
            if file_info["kind"] == "directory"
        }

        topics = policy_input.task_state["assignment"]
        for topic in sorted(set(topics.values())):
            if topic not in existing_dirs:
                return ActionRequest(
                    action_type="mkdir",
                    path=topic,
                    rationale=f"Create topic folder {topic}.",
                )

        for filename, topic in topics.items():
            source = f"inbox/{filename}"
            destination = f"{topic}/{filename}"
            if destination in existing_paths:
                continue
            if source in existing_paths:
                return ActionRequest(
                    action_type="move_file",
                    path=source,
                    target_path=destination,
                    rationale=f"Move {filename} into {topic}.",
                )

        return ActionRequest(
            action_type="done",
            rationale="No remaining sortable snippets were found.",
        )

