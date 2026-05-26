from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Any, Literal


ActionType = Literal[
    "write_text",
    "append_text",
    "mkdir",
    "move_file",
    "read_file",
    "done",
    "noop",
    "adjust_threshold",
    "policy_failure",
]

AVAILABLE_ACTIONS = [
    "write_text",
    "append_text",
    "mkdir",
    "move_file",
    "read_file",
    "done",
    "noop",
    "adjust_threshold",
]


@dataclass(frozen=True)
class ActionRequest:
    action_type: ActionType
    path: str | None = None
    target_path: str | None = None
    text: str = ""
    rationale: str = ""
    threshold_name: str | None = None
    threshold_delta: float = 0.0
    urgency_delta: float = 0.0

    def to_payload(self) -> dict:
        return {
            "action_type": self.action_type,
            "path": self.path,
            "target_path": self.target_path,
            "text": self.text,
            "rationale": self.rationale,
            "threshold_name": self.threshold_name,
            "threshold_delta": self.threshold_delta,
            "urgency_delta": self.urgency_delta,
        }

    @staticmethod
    def from_payload(payload: dict) -> "ActionRequest":
        action_type = payload.get("action_type")
        # policy_failure is internal-only; policies may not emit it as JSON.
        if action_type not in set(AVAILABLE_ACTIONS):
            raise ValueError(f"Unsupported action_type: {action_type}")
        path = payload.get("path")
        target_path = payload.get("target_path")
        text = payload.get("text", "")
        rationale = payload.get("rationale", "")
        threshold_name = payload.get("threshold_name")
        threshold_delta = payload.get("threshold_delta", 0.0)
        urgency_delta = payload.get("urgency_delta", 0.0)
        if path is not None and not isinstance(path, str):
            raise ValueError("Action path must be a string or null.")
        if target_path is not None and not isinstance(target_path, str):
            raise ValueError("Action target_path must be a string or null.")
        if not isinstance(text, str):
            raise ValueError("Action text must be a string.")
        if not isinstance(rationale, str):
            raise ValueError("Action rationale must be a string.")
        if threshold_name is not None and not isinstance(threshold_name, str):
            raise ValueError("threshold_name must be a string or null.")
        if action_type == "adjust_threshold" and not threshold_name:
            raise ValueError("adjust_threshold requires threshold_name.")
        return ActionRequest(
            action_type=action_type,
            path=path,
            target_path=target_path,
            text=text,
            rationale=rationale,
            threshold_name=threshold_name,
            threshold_delta=float(threshold_delta),
            urgency_delta=float(urgency_delta),
        )


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str
    touched_path: str | None = None
    failure_kind: str | None = None
    data: dict[str, Any] | None = None

    def to_payload(self) -> dict:
        return {
            "ok": self.ok,
            "message": self.message,
            "touched_path": self.touched_path,
            "failure_kind": self.failure_kind,
            "data": self.data or {},
        }


class LocalFileActions:
    def __init__(self, world_root: Path):
        self.world_root = world_root.resolve()
        self.world_root.mkdir(parents=True, exist_ok=True)

    def execute(self, request: ActionRequest) -> ActionResult:
        if request.action_type == "noop":
            return ActionResult(ok=True, message="No action taken.")

        if request.action_type == "policy_failure":
            return ActionResult(
                ok=False,
                message=request.rationale or "Policy failed before execution.",
                failure_kind="llm_invalid_response",
            )

        if request.action_type == "done":
            return ActionResult(ok=True, message="Policy marked task done.")

        if request.action_type == "adjust_threshold":
            return ActionResult(
                ok=False,
                message="Threshold adjustments require a RegimeManager, not LocalFileActions.",
                failure_kind="wrong_executor",
                data=request.to_payload(),
            )

        if request.path is None:
            return ActionResult(
                ok=False,
                message="Missing path for file action.",
                failure_kind="missing_path",
            )

        try:
            target = self._resolve_inside_world(request.path)
        except ValueError as exc:
            return ActionResult(ok=False, message=str(exc), failure_kind="path_escape")
        target.parent.mkdir(parents=True, exist_ok=True)

        if request.action_type == "write_text":
            target.write_text(request.text, encoding="utf-8")
            return ActionResult(ok=True, message="File written.", touched_path=str(target))

        if request.action_type == "append_text":
            with target.open("a", encoding="utf-8") as handle:
                handle.write(request.text)
            return ActionResult(ok=True, message="File appended.", touched_path=str(target))

        if request.action_type == "mkdir":
            target.mkdir(parents=True, exist_ok=True)
            return ActionResult(ok=True, message="Directory created.", touched_path=str(target))

        if request.action_type == "read_file":
            if not target.is_file():
                return ActionResult(
                    ok=False,
                    message=f"Not a file: {request.path}",
                    failure_kind="not_a_file",
                )
            return ActionResult(
                ok=True,
                message="File read.",
                touched_path=str(target),
                data={"text": target.read_text(encoding="utf-8")},
            )

        if request.action_type == "move_file":
            if request.target_path is None:
                return ActionResult(
                    ok=False,
                    message="Missing target_path for move_file.",
                    failure_kind="missing_target_path",
                )
            try:
                destination = self._resolve_inside_world(request.target_path)
            except ValueError as exc:
                return ActionResult(ok=False, message=str(exc), failure_kind="path_escape")
            if not target.is_file():
                return ActionResult(
                    ok=False,
                    message=f"Source is not a file: {request.path}",
                    failure_kind="not_a_file",
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(destination))
            return ActionResult(
                ok=True,
                message="File moved.",
                touched_path=str(destination),
                data={"source_path": str(target), "target_path": str(destination)},
            )

        return ActionResult(
            ok=False,
            message=f"Unknown action: {request.action_type}",
            failure_kind="unknown_action",
        )

    def _resolve_inside_world(self, relative_path: str) -> Path:
        if relative_path in {"", ".", "/"}:
            raise ValueError("Action path must name a child of the world root.")
        target = (self.world_root / relative_path).resolve()
        if self.world_root not in target.parents and target != self.world_root:
            raise ValueError(f"Action path escapes world root: {relative_path}")
        return target
