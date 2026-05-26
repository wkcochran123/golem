from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..actions import LocalFileActions
from ..categorizer import categorize
from ..events import event
from ..graders.file_sort import FileSortGrader
from ..graph import KnowledgeGraph
from ..policies.file_sort_scripted import ScriptedFileSortPolicy
from ..policies.types import PolicyInput
from ..salience import compare_snapshots
from ..sensors import FileSystemSensor
from ..store import EventLog


class FileSortLoop:
    def __init__(self, run_root: Path, policy: object | None = None):
        self.run_root = run_root
        self.world_root = run_root / "world"
        self.events = EventLog(run_root / "events.jsonl")
        self.graph = KnowledgeGraph(run_root / "graph.sqlite")
        self.sensor = FileSystemSensor(self.world_root)
        self.actions = LocalFileActions(self.world_root)
        self.grader = FileSortGrader()
        self.policy = policy or ScriptedFileSortPolicy()
        self.assignment = {
            example.filename: example.topic for example in self.grader.examples
        }

    def setup(self) -> None:
        self.grader.seed_world(self.world_root)

    def tick(self) -> dict:
        before = self.sensor.snapshot()
        grade_before = self.grader.grade(self.world_root)
        task_state = {
            **self.grader.task_state(self.world_root),
            "assignment": self.assignment,
            "grade": grade_before.to_payload(),
            "files": self._file_listing(),
        }
        policy_input = PolicyInput(
            graph_summary=self.graph.summary(),
            recent_failures=self.graph.failures(),
            available_actions=["mkdir", "move_file", "read_file", "done"],
            policy_hints=self.graph.affordances(),
            task_state=task_state,
        )
        input_event = self.events.append(event("policy_input", policy_input.to_payload()))

        action = self.policy.choose(policy_input)
        policy_event = self.events.append(
            event("policy", action.to_payload(), parent_id=input_event.id)
        )
        result = self.actions.execute(action)
        self.graph.record_action_result(action, result)
        action_event = self.events.append(
            event("action_result", result.to_payload(), parent_id=policy_event.id)
        )

        after = self.sensor.snapshot()
        changes = compare_snapshots(before, after)
        salience_event = self.events.append(
            event(
                "salience",
                {"changes": [change.to_payload() for change in changes]},
                parent_id=action_event.id,
            )
        )
        distinctions = categorize(changes)
        self.events.append(
            event(
                "categorizer",
                {"distinctions": [item.to_payload() for item in distinctions]},
                parent_id=salience_event.id,
            )
        )
        for change, distinction in zip(changes, distinctions, strict=True):
            self.graph.record_change(change, distinction)

        grade_after = self.grader.grade(self.world_root)
        grade_event = self.events.append(
            event("grade", grade_after.to_payload(), parent_id=action_event.id)
        )
        self.events.append(event("graph", self.graph.summary(), parent_id=grade_event.id))

        return {
            "action": action.to_payload(),
            "result": result.to_payload(),
            "grade": grade_after.to_payload(),
            "changes": [change.to_payload() for change in changes],
        }

    def _file_listing(self) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        if not self.world_root.exists():
            return entries
        for path in sorted(self.world_root.rglob("*")):
            entries.append(
                {
                    "kind": "directory" if path.is_dir() else "file",
                    "path": str(path.relative_to(self.world_root)),
                }
            )
        return entries


def main() -> None:
    run_root = Path(__file__).resolve().parents[1] / "runs" / "file_sort_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    loop = FileSortLoop(run_root)
    loop.setup()

    ticks = []
    for _ in range(12):
        result = loop.tick()
        ticks.append(result)
        if result["grade"]["score"] >= 1.0:
            ticks.append(loop.tick())
            break

    print(json.dumps({"run_root": str(run_root), "ticks": ticks}, indent=2))


if __name__ == "__main__":
    main()
