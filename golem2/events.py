from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


EventKind = str


@dataclass(frozen=True)
class Event:
    kind: EventKind
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    parent_id: str | None = None

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


def event(kind: EventKind, payload: dict[str, Any], parent_id: str | None = None) -> Event:
    return Event(kind=kind, payload=payload, parent_id=parent_id)

