from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class TelemetrySnapshot:
    component: str
    kind: str
    payload: dict[str, Any]
    id: str
    timestamp: str

    @staticmethod
    def capture(component: str, kind: str, payload: dict[str, Any]) -> "TelemetrySnapshot":
        return TelemetrySnapshot(
            component=component,
            kind=kind,
            payload=payload,
            id=uuid4().hex,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "component": self.component,
            "kind": self.kind,
            "payload": self.payload,
        }

