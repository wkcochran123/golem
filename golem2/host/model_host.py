from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any


# Default timeouts are real-time-loop friendly. Callers that legitimately
# need longer (sleep replay, slow models) should pass an explicit timeout.
DEFAULT_GET_TIMEOUT = 5.0
DEFAULT_POST_TIMEOUT = 10.0


@dataclass(frozen=True)
class ModelHostClient:
    base_url: str

    def health(self) -> dict[str, Any]:
        return self._get("/health", timeout=DEFAULT_GET_TIMEOUT)

    def list_models(self) -> dict[str, Any]:
        return self._get("/models", timeout=DEFAULT_GET_TIMEOUT)

    def infer(self, model: str, payload: dict[str, Any], *, timeout: float = DEFAULT_POST_TIMEOUT) -> dict[str, Any]:
        return self._post(f"/models/{model}/infer", payload, timeout=timeout)

    def train_step(self, model: str, payload: dict[str, Any], *, timeout: float = DEFAULT_POST_TIMEOUT) -> dict[str, Any]:
        return self._post(f"/models/{model}/train_step", payload, timeout=timeout)

    def start_sleep(self, payload: dict[str, Any], *, timeout: float = DEFAULT_POST_TIMEOUT) -> dict[str, Any]:
        return self._post("/sleep/start", payload, timeout=timeout)

    def sleep_status(self, job_id: str) -> dict[str, Any]:
        return self._get(f"/sleep/{job_id}", timeout=DEFAULT_GET_TIMEOUT)

    def _get(self, path: str, *, timeout: float = DEFAULT_GET_TIMEOUT) -> dict[str, Any]:
        with urllib.request.urlopen(self.base_url.rstrip("/") + path, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, payload: dict[str, Any], *, timeout: float = DEFAULT_POST_TIMEOUT) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url.rstrip("/") + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))


@dataclass(frozen=True)
class LMStudioClient:
    base_url: str

    def list_models(self) -> dict[str, Any]:
        return self._get("/v1/models", timeout=DEFAULT_GET_TIMEOUT)

    def chat_completions(self, payload: dict[str, Any], *, timeout: float = DEFAULT_POST_TIMEOUT) -> dict[str, Any]:
        return self._post("/v1/chat/completions", payload, timeout=timeout)

    def _get(self, path: str, *, timeout: float = DEFAULT_GET_TIMEOUT) -> dict[str, Any]:
        with urllib.request.urlopen(self.base_url.rstrip("/") + path, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, path: str, payload: dict[str, Any], *, timeout: float = DEFAULT_POST_TIMEOUT) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url.rstrip("/") + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
