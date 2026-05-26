from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .events import Event


class EventLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: Event) -> Event:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_record(), sort_keys=True) + "\n")
        return record

    def read(self) -> Iterable[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

