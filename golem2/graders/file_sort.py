from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileSortExample:
    filename: str
    topic: str
    text: str


@dataclass(frozen=True)
class Grade:
    score: float
    correct: int
    total: int
    misplaced: list[dict[str, str]]

    def to_payload(self) -> dict:
        return {
            "score": self.score,
            "correct": self.correct,
            "total": self.total,
            "misplaced": self.misplaced,
        }


EXAMPLES = [
    FileSortExample(
        filename="cat.txt",
        topic="animals",
        text="Cats stalk quietly, purr, and curl into warm patches of sun.\n",
    ),
    FileSortExample(
        filename="train.txt",
        topic="vehicles",
        text="The train left the station with steel wheels and a bright horn.\n",
    ),
    FileSortExample(
        filename="apple.txt",
        topic="fruit",
        text="A crisp apple can be sliced into a pie or eaten fresh from the tree.\n",
    ),
]


class FileSortGrader:
    def __init__(self, examples: list[FileSortExample] | None = None):
        self.examples = examples or EXAMPLES

    def seed_world(self, world_root: Path) -> None:
        inbox = world_root / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for example in self.examples:
            (inbox / example.filename).write_text(example.text, encoding="utf-8")

    def task_state(self, world_root: Path) -> dict:
        return {
            "goal": "Move each snippet from inbox/ into the folder matching its topic.",
            "topics": sorted({example.topic for example in self.examples}),
            "snippets": [
                {
                    "filename": example.filename,
                    "text": example.text,
                }
                for example in self.examples
            ],
        }

    def grade(self, world_root: Path) -> Grade:
        correct = 0
        misplaced: list[dict[str, str]] = []
        for example in self.examples:
            expected = world_root / example.topic / example.filename
            if expected.is_file():
                correct += 1
                continue
            actual = self._find(world_root, example.filename)
            misplaced.append(
                {
                    "filename": example.filename,
                    "expected_topic": example.topic,
                    "actual_path": str(actual.relative_to(world_root)) if actual else "missing",
                }
            )
        total = len(self.examples)
        return Grade(
            score=correct / total if total else 1.0,
            correct=correct,
            total=total,
            misplaced=misplaced,
        )

    @staticmethod
    def _find(world_root: Path, filename: str) -> Path | None:
        for path in world_root.rglob(filename):
            if path.is_file():
                return path
        return None

