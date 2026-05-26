from __future__ import annotations

import argparse
import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse


DEFAULT_MODELS = ("heatmap_reader", "urgency_policy", "vision_mlp_stub")


@dataclass
class HostState:
    started_at: float = field(default_factory=time.monotonic)
    sleep_jobs: dict[str, dict[str, Any]] = field(default_factory=dict)


class ModelHostHandler(BaseHTTPRequestHandler):
    server_version = "GolemModelHost/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._write_json({"ok": True, "service": "golem-model-host", "uptime_s": self._uptime()})
            return
        if path == "/models":
            self._write_json({"models": list(DEFAULT_MODELS)})
            return
        if path == "/v1/models":
            self._write_json({"data": [{"id": model, "object": "model"} for model in DEFAULT_MODELS]})
            return
        if path.startswith("/sleep/"):
            job_id = path.rsplit("/", 1)[-1]
            job = self._state.sleep_jobs.get(job_id)
            if job is None:
                self._write_json({"error": "sleep job not found", "job_id": job_id}, status=404)
                return
            elapsed = max(0.0, time.monotonic() - job["created_monotonic"])
            progress = min(1.0, elapsed / job["duration_s"])
            job["progress"] = max(job["progress"], progress)
            status = "complete" if job["progress"] >= 1.0 else "running"
            self._write_json(
                {
                    "job_id": job_id,
                    "status": status,
                    "progress": round(job["progress"], 3),
                    "models": job["models"],
                    "ledger_path": job["ledger_path"],
                }
            )
            return
        self._write_json({"error": "not found", "path": path}, status=404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "models" and parts[2] == "infer":
            model = parts[1]
            self._write_json(
                {
                    "model": model,
                    "output": {
                        "score": _score_payload(payload),
                        "distinctions": ["stub_inference", "host_roundtrip"],
                    },
                }
            )
            return
        if len(parts) == 3 and parts[0] == "models" and parts[2] == "train_step":
            model = parts[1]
            self._write_json(
                {
                    "model": model,
                    "accepted": True,
                    "loss": _score_payload(payload),
                    "step_id": uuid.uuid4().hex,
                }
            )
            return
        if path == "/sleep/start":
            job_id = uuid.uuid4().hex
            models = payload.get("models") if isinstance(payload.get("models"), list) else list(DEFAULT_MODELS)
            ledger_path = str(payload.get("ledger_path", ""))
            self._state.sleep_jobs[job_id] = {
                "created_monotonic": time.monotonic(),
                "duration_s": 0.2,
                "progress": 0.0,
                "models": models,
                "ledger_path": ledger_path,
            }
            self._write_json({"job_id": job_id, "status": "started", "progress": 0.0})
            return
        if path == "/v1/chat/completions":
            self._write_json(
                {
                    "id": f"chatcmpl-{uuid.uuid4().hex}",
                    "object": "chat.completion",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": json.dumps({"action_type": "noop", "reason": "stub_host"}),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                }
            )
            return
        self._write_json({"error": "not found", "path": path}, status=404)

    @property
    def _state(self) -> HostState:
        return self.server.state  # type: ignore[attr-defined]

    def _uptime(self) -> float:
        return round(time.monotonic() - self._state.started_at, 3)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object.")
        return data

    def _write_json(self, payload: dict[str, Any], *, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


class GolemModelHost(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int]):
        super().__init__(server_address, ModelHostHandler)
        self.state = HostState()


def serve(host: str = "127.0.0.1", port: int = 8765) -> GolemModelHost:
    server = GolemModelHost((host, port))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _score_payload(payload: dict[str, Any]) -> float:
    encoded = json.dumps(payload, sort_keys=True)
    return round((sum(ord(ch) for ch in encoded) % 1000) / 1000, 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Golem model-host stub.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = GolemModelHost((args.host, args.port))
    print(f"golem model host listening on http://{args.host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
