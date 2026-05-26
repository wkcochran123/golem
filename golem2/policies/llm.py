from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from json import JSONDecodeError

from ..actions import ActionRequest
from .types import PolicyInput, PolicyInputLimits


class LLMPolicy:
    """OpenAI-compatible chat/completions adapter for typed actions."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
        input_limits: PolicyInputLimits | None = None,
    ):
        self.base_url = (base_url or os.environ.get("GOLEM2_LLM_BASE_URL", "")).rstrip("/")
        self.model = model or os.environ.get("GOLEM2_LLM_MODEL", "local-model")
        self.api_key = api_key or os.environ.get("GOLEM2_LLM_API_KEY", "")
        # Default 10s keeps the proximity loop responsive. Slow models that
        # need more should pass an explicit timeout=N.
        self.timeout = timeout
        self.input_limits = input_limits or PolicyInputLimits()
        if not self.base_url:
            raise ValueError("LLMPolicy requires GOLEM2_LLM_BASE_URL or base_url.")

    def choose(self, policy_input: PolicyInput) -> ActionRequest:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the policy writer for golem2. Choose exactly one "
                        "safe action from available_actions. When regimes are present, first "
                        "choose the regime whose thresholds and unstructured context best match "
                        "the operator goal, then choose threshold or urgency adjustments from "
                        "that regime's allowed actions. Treat thresholds like an analog joystick: "
                        "you shape behavior by moving latch boundaries, not by directly driving "
                        "motors. Use "
                        "policy_hints as advice, not as action_type values. Respond with JSON only, matching "
                        "this schema: {\"action_type\":\"write_text|append_text|mkdir|"
                        "move_file|read_file|done|noop|adjust_threshold\", "
                        "\"path\":\"relative/path/or/null\", "
                        "\"target_path\":\"relative/path/or/null\", \"text\":\"...\", "
                        "\"threshold_name\":\"name/or/null\", \"threshold_delta\":0.0, "
                        "\"urgency_delta\":0.0, \"rationale\":\"...\"}."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        policy_input.to_payload(limits=self.input_limits),
                        sort_keys=True,
                    ),
                },
            ],
            "temperature": 0.2,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return ActionRequest.from_payload(json.loads(_strip_fences(content)))
        except (
            JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            urllib.error.URLError,
            TimeoutError,
        ) as exc:
            return ActionRequest(
                action_type="policy_failure",
                rationale=f"LLM emitted no valid action: {type(exc).__name__}: {exc}",
            )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


def _strip_fences(content: str) -> str:
    stripped = content.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()
