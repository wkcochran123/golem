from __future__ import annotations

import json

from ..policies.types import (
    PolicyInput,
    PolicyInputLimits,
    PolicyRegime,
    RegimeThreshold,
)


def main() -> None:
    regimes = [
        PolicyRegime(
            name=f"regime_{index}",
            objective="Prove PolicyInput context limits are explicit.",
            thresholds=[
                RegimeThreshold(
                    name=f"threshold_{index}_{threshold_index}",
                    projection="distance_panorama",
                    current_value=0.0,
                    threshold=0.1 * threshold_index,
                    urgency=0.05,
                )
                for threshold_index in range(4)
            ],
        )
        for index in range(3)
    ]
    policy_input = PolicyInput(
        graph_summary={
            "edges": [
                {
                    "source": f"node:{index}",
                    "relation": "leads_to",
                    "target": f"node:{index + 1}",
                }
                for index in range(6)
            ]
        },
        recent_failures=[
            {
                "action": "adjust_threshold",
                "failure": f"failure_{index}",
                "evidence": "synthetic oversized context",
            }
            for index in range(4)
        ],
        available_actions=["adjust_threshold", "noop"],
        policy_hints=[f"hint_{index}" for index in range(5)],
        regimes=regimes,
    )
    bounded = policy_input.to_payload(
        limits=PolicyInputLimits(
            max_graph_edges=2,
            max_recent_failures=2,
            max_policy_hints=3,
            max_regimes=2,
            max_thresholds_per_regime=2,
        )
    )
    print(json.dumps(bounded, indent=2))


if __name__ == "__main__":
    main()
