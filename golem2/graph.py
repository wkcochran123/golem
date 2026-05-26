from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from .actions import ActionRequest, ActionResult
from .categorizer import Distinction
from .salience import SalientChange


class KnowledgeGraph:
    FAILURE_HINTS = {
        "llm_invalid_response": (
            "emit_valid_action_json",
            "Policy adapters must emit valid typed action JSON.",
        ),
        "path_escape": (
            "choose_valid_relative_path",
            "File actions must stay inside the local world root.",
        ),
        "missing_path": ("provide_action_path", "File actions require a relative path."),
        "missing_target_path": (
            "provide_move_target_path",
            "move_file requires a relative target_path.",
        ),
        "not_a_file": ("choose_existing_file_source", "File source must exist and be a file."),
        "unknown_action": (
            "choose_known_action_type",
            "Action type must be in the executor vocabulary.",
        ),
        "wrong_executor": (
            "route_action_to_correct_executor",
            "Action type is valid but must be handled by the matching executor.",
        ),
        "missing_threshold_name": (
            "provide_threshold_name",
            "Threshold adjustment actions must name the threshold to adjust.",
        ),
        "unknown_regime": (
            "choose_known_regime",
            "Threshold adjustment actions must target an active regime.",
        ),
        "unknown_threshold": (
            "choose_known_threshold",
            "Threshold adjustment actions must target a threshold exposed by the regime.",
        ),
        "urgency_budget_exceeded": (
            "lower_other_urgency_first",
            "Threshold urgency is conserved; total urgency must stay within the level budget.",
        ),
        "adjustment_rate_limited": (
            "wait_for_adjustment_cooldown",
            "Threshold adjustments are rate-limited; wait for the cooldown before retrying.",
        ),
    }
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists nodes (
                    id integer primary key,
                    kind text not null,
                    name text not null,
                    unique(kind, name)
                )
                """
            )
            conn.execute(
                """
                create table if not exists edges (
                    id integer primary key,
                    source_kind text not null,
                    source_name text not null,
                    relation text not null,
                    target_kind text not null,
                    target_name text not null,
                    evidence text not null,
                    unique(source_kind, source_name, relation, target_kind, target_name)
                )
                """
            )

    def record_change(self, change: SalientChange, distinction: Distinction) -> None:
        with self._connect() as conn:
            self._node(conn, "file", change.path)
            self._node(conn, "distinction", distinction.name)
            self._edge(
                conn,
                "file",
                change.path,
                "has_salient_change",
                "change",
                change.change_type,
                change.evidence,
            )
            self._edge(
                conn,
                "file",
                change.path,
                "is_named_by",
                "distinction",
                distinction.name,
                distinction.evidence,
            )
            self._edge(
                conn,
                "distinction",
                distinction.name,
                "affords",
                "policy_hint",
                "inspect_or_refine",
                "Changed artifacts can be inspected or refined by the next policy.",
            )

    def record_action_result(self, action: ActionRequest, result: ActionResult) -> None:
        if result.ok:
            return
        action_name = action.action_type
        if result.failure_kind is None:
            raise ValueError("Failed ActionResult must include failure_kind.")
        failure_name = result.failure_kind
        with self._connect() as conn:
            self._node(conn, "action", action_name)
            self._node(conn, "failure", failure_name)
            self._edge(
                conn,
                "action",
                action_name,
                "failed_with",
                "failure",
                failure_name,
                result.message,
            )
            self._edge(
                conn,
                "failure",
                failure_name,
                "affords",
                "policy_hint",
                self._failure_hint(failure_name),
                self._failure_evidence(failure_name),
            )

    def record_heatmap_comparison(self, name: str, comparison: dict) -> None:
        crossing_name = f"{name}_threshold_crossing"
        opportunity_name = f"{name}_near_threshold"
        crossed = str(comparison["threshold_crossed"]).lower()
        with self._connect() as conn:
            self._node(conn, "heatmap_comparison", name)
            self._edge(
                conn,
                "heatmap_comparison",
                name,
                "compared_to",
                "threshold",
                str(comparison["threshold"]),
                f"delta={comparison['delta']}; crossed={crossed}.",
            )
            if comparison["threshold_crossed"]:
                self._node(conn, "threshold_crossing", crossing_name)
                self._edge(
                    conn,
                    "heatmap_comparison",
                    name,
                    "crossed_threshold",
                    "threshold_crossing",
                    crossing_name,
                    (
                        f"delta={comparison['delta']}; "
                        f"average_delta={comparison['average_delta']}; "
                        f"threshold={comparison['threshold']}; "
                        f"changed_cell_count={comparison['changed_cell_count']}"
                    ),
                )
                self._edge(
                    conn,
                    "threshold_crossing",
                    crossing_name,
                    "affords",
                    "policy_hint",
                    "inspect_crossing_residue",
                    "A crossing happened; inspect residue before treating it as a future opportunity.",
                )
                return
            if abs(comparison["delta"]) < comparison["threshold"] * 0.5:
                return
            self._node(conn, "slip_opportunity", opportunity_name)
            self._edge(
                conn,
                "heatmap_comparison",
                name,
                "has_slip_opportunity",
                "slip_opportunity",
                opportunity_name,
                (
                    f"delta={comparison['delta']}; "
                    f"average_delta={comparison['average_delta']}; "
                    f"threshold={comparison['threshold']}; "
                    f"crossed={crossed}; "
                    f"changed_cell_count={comparison['changed_cell_count']}"
                ),
            )
            self._edge(
                conn,
                "slip_opportunity",
                opportunity_name,
                "near_threshold_for",
                "threshold",
                str(comparison["threshold"]),
                "Heat-map score is near a threshold but has not crossed.",
            )
            self._edge(
                conn,
                "slip_opportunity",
                opportunity_name,
                "affords",
                "policy_hint",
                "inspect_heatmap_threshold",
                "Compare score delta and changed cells before selecting the next action.",
            )

    def record_threshold_adjustment(
        self,
        regime_name: str,
        request: ActionRequest,
        result: ActionResult,
    ) -> None:
        threshold_name = request.threshold_name or "unknown_threshold"
        adjustment_name = (
            f"{uuid4().hex}:{regime_name}:{threshold_name}:"
            f"threshold_delta={request.threshold_delta}:urgency_delta={request.urgency_delta}"
        )
        result_name = "applied" if result.ok else f"rejected:{result.failure_kind}"
        with self._connect() as conn:
            self._node(conn, "regime", regime_name)
            self._node(conn, "threshold", threshold_name)
            self._node(conn, "threshold_adjustment", adjustment_name)
            self._node(conn, "adjustment_result", result_name)
            self._edge(
                conn,
                "regime",
                regime_name,
                "adjusted_threshold",
                "threshold",
                threshold_name,
                request.rationale or "No rationale supplied.",
            )
            self._edge(
                conn,
                "threshold_adjustment",
                adjustment_name,
                "targeted",
                "threshold",
                threshold_name,
                (
                    f"threshold_delta={request.threshold_delta}; "
                    f"urgency_delta={request.urgency_delta}"
                ),
            )
            self._edge(
                conn,
                "threshold_adjustment",
                adjustment_name,
                "had_result",
                "adjustment_result",
                result_name,
                result.message,
            )
            if not result.ok and result.failure_kind is not None:
                self._node(conn, "failure", result.failure_kind)
                self._edge(
                    conn,
                    "threshold_adjustment",
                    adjustment_name,
                    "failed_with",
                    "failure",
                    result.failure_kind,
                    result.message,
                )
                self._edge(
                    conn,
                    "failure",
                    result.failure_kind,
                    "affords",
                    "policy_hint",
                    self._failure_hint(result.failure_kind),
                    self._failure_evidence(result.failure_kind),
                )

    def failures(self) -> list[dict[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select source_name, target_name, evidence
                from edges
                where relation = 'failed_with'
                order by id desc
                limit 20
                """
            ).fetchall()
        return [
            {"action": row[0], "failure": row[1], "evidence": row[2]}
            for row in rows
        ]

    def affordances(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select distinct target_name
                from edges
                where relation = 'affords'
                order by target_name
                """
            ).fetchall()
        return [row[0] for row in rows]

    def summary(self) -> dict[str, list[dict[str, str]]]:
        with self._connect() as conn:
            edges = conn.execute(
                """
                select source_kind, source_name, relation, target_kind, target_name
                from edges
                order by id
                """
            ).fetchall()
        return {
            "edges": [
                {
                    "source": f"{row[0]}:{row[1]}",
                    "relation": row[2],
                    "target": f"{row[3]}:{row[4]}",
                }
                for row in edges
            ]
        }

    @staticmethod
    def _node(conn: sqlite3.Connection, kind: str, name: str) -> None:
        conn.execute(
            "insert or ignore into nodes(kind, name) values (?, ?)",
            (kind, name),
        )

    @staticmethod
    def _edge(
        conn: sqlite3.Connection,
        source_kind: str,
        source_name: str,
        relation: str,
        target_kind: str,
        target_name: str,
        evidence: str,
    ) -> None:
        conn.execute(
            """
            insert or ignore into edges(
                source_kind, source_name, relation, target_kind, target_name, evidence
            ) values (?, ?, ?, ?, ?, ?)
            """,
            (source_kind, source_name, relation, target_kind, target_name, evidence),
        )

    @staticmethod
    def _failure_hint(failure_name: str) -> str:
        return KnowledgeGraph.FAILURE_HINTS[failure_name][0]

    @staticmethod
    def _failure_evidence(failure_name: str) -> str:
        return KnowledgeGraph.FAILURE_HINTS[failure_name][1]
