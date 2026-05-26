from __future__ import annotations

from pathlib import Path

from ..actions import AVAILABLE_ACTIONS, LocalFileActions
from ..categorizer import categorize
from ..events import event
from ..graph import KnowledgeGraph
from ..policies.scripted import ScriptedPolicy
from ..policies.types import PolicyInput
from ..salience import compare_snapshots
from ..sensors import FileSystemSensor
from ..store import EventLog


class LocalWorldLoop:
    def __init__(self, run_root: Path, policy: ScriptedPolicy | None = None):
        self.run_root = run_root
        self.world_root = run_root / "world"
        self.events = EventLog(run_root / "events.jsonl")
        self.graph = KnowledgeGraph(run_root / "graph.sqlite")
        self.sensor = FileSystemSensor(self.world_root)
        self.actions = LocalFileActions(self.world_root)
        self.policy = policy or ScriptedPolicy()

    def tick(self) -> dict:
        graph_summary = self.graph.summary()
        policy_input = PolicyInput(
            graph_summary=graph_summary,
            recent_failures=self.graph.failures(),
            available_actions=AVAILABLE_ACTIONS,
            policy_hints=self.graph.affordances(),
        )
        input_event = self.events.append(event("policy_input", policy_input.to_payload()))

        action = self.policy.choose(policy_input)
        policy_event = self.events.append(
            event("policy", action.to_payload(), parent_id=input_event.id)
        )

        before = self.sensor.snapshot()
        before_event = self.events.append(
            event(
                "sensor",
                {"phase": "before", "files": [item.to_payload() for item in before.values()]},
                parent_id=policy_event.id,
            )
        )

        result = self.actions.execute(action)
        self.graph.record_action_result(action, result)
        action_event = self.events.append(
            event("action_result", result.to_payload(), parent_id=policy_event.id)
        )

        after = self.sensor.snapshot()
        self.events.append(
            event(
                "sensor",
                {"phase": "after", "files": [item.to_payload() for item in after.values()]},
                parent_id=action_event.id,
            )
        )

        changes = compare_snapshots(before, after)
        salience_event = self.events.append(
            event(
                "salience",
                {"changes": [change.to_payload() for change in changes]},
                parent_id=before_event.id,
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

        graph_event = self.events.append(
            event("graph", self.graph.summary(), parent_id=salience_event.id)
        )

        return {
            "action": action.to_payload(),
            "result": result.to_payload(),
            "changes": [change.to_payload() for change in changes],
            "graph_event": graph_event.to_record(),
        }
