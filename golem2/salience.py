from __future__ import annotations

from dataclasses import dataclass

from .sensors import FileResidue


@dataclass(frozen=True)
class SalientChange:
    change_type: str
    path: str
    score: float
    before_sha: str | None
    after_sha: str | None
    evidence: str

    def to_payload(self) -> dict:
        return {
            "change_type": self.change_type,
            "path": self.path,
            "score": self.score,
            "before_sha": self.before_sha,
            "after_sha": self.after_sha,
            "evidence": self.evidence,
        }


def compare_snapshots(
    before: dict[str, FileResidue], after: dict[str, FileResidue]
) -> list[SalientChange]:
    changes: list[SalientChange] = []
    paths = sorted(set(before) | set(after))
    for path in paths:
        left = before.get(path)
        right = after.get(path)
        if left is None and right is not None:
            changes.append(
                SalientChange(
                    change_type="created",
                    path=path,
                    score=1.0,
                    before_sha=None,
                    after_sha=right.sha256,
                    evidence=right.preview,
                )
            )
        elif left is not None and right is None:
            changes.append(
                SalientChange(
                    change_type="deleted",
                    path=path,
                    score=1.0,
                    before_sha=left.sha256,
                    after_sha=None,
                    evidence=left.preview,
                )
            )
        elif left is not None and right is not None and left.sha256 != right.sha256:
            size_delta = abs(right.size - left.size)
            score = min(1.0, 0.5 + size_delta / max(right.size, left.size, 1))
            changes.append(
                SalientChange(
                    change_type="modified",
                    path=path,
                    score=score,
                    before_sha=left.sha256,
                    after_sha=right.sha256,
                    evidence=right.preview,
                )
            )
    return changes

