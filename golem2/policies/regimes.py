from __future__ import annotations

from .types import PolicyRegime, RegimeThreshold


def find_cat_regime() -> PolicyRegime:
    return PolicyRegime(
        name="find_cat",
        objective="Locate the cat by choosing sensor and motion actions that reduce uncertainty.",
        thresholds=[
            RegimeThreshold(
                name="visual_catness",
                projection="visual_category_map",
                current_value=0.18,
                threshold=0.65,
                urgency=0.12,
                min_threshold=0.4,
                max_threshold=0.9,
                units="confidence",
            ),
            RegimeThreshold(
                name="motion_salience",
                projection="motion_heatmap",
                current_value=0.41,
                threshold=0.55,
                urgency=0.08,
                min_threshold=0.25,
                max_threshold=0.8,
                units="score",
            ),
            RegimeThreshold(
                name="under_furniture_gap",
                projection="depth_gap_map",
                current_value=0.72,
                threshold=0.5,
                urgency=0.1,
                min_threshold=0.2,
                max_threshold=0.8,
                units="gap_score",
            ),
        ],
        unstructured_context={
            "operator_request": "find the cat",
            "recent_observations": [
                "soft movement near basement couch",
                "no confirmed visual category yet",
                "low clearance region is unresolved",
            ],
            "known_constraints": [
                "do not drive under furniture",
                "request another angle when category confidence stays low",
            ],
        },
        allowed_actions=[
            "lower_visual_catness_threshold",
            "raise_motion_salience_urgency",
            "lower_under_furniture_gap_urgency",
            "hold_position",
            "ask_operator_for_hint",
        ],
    )
