from __future__ import annotations

from dataclasses import dataclass

from .salience import SalientChange


@dataclass(frozen=True)
class Distinction:
    name: str
    path: str
    evidence: str

    def to_payload(self) -> dict:
        return {"name": self.name, "path": self.path, "evidence": self.evidence}


def categorize(changes: list[SalientChange]) -> list[Distinction]:
    distinctions: list[Distinction] = []
    for change in changes:
        if change.after_sha == "directory":
            kind = "directory_artifact"
        elif change.path.endswith(".md"):
            kind = "markdown_artifact"
        elif change.path.endswith(".txt"):
            kind = "text_artifact"
        else:
            kind = "file_artifact"
        distinctions.append(
            Distinction(
                name=f"{change.change_type}_{kind}",
                path=change.path,
                evidence=change.evidence[:240],
            )
        )
    return distinctions
