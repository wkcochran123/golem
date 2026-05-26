from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class FileResidue:
    kind: str
    path: str
    sha256: str
    size: int
    preview: str

    def to_payload(self) -> dict:
        return {
            "kind": self.kind,
            "path": self.path,
            "sha256": self.sha256,
            "size": self.size,
            "preview": self.preview,
        }


class FileSystemSensor:
    def __init__(self, world_root: Path):
        self.world_root = world_root.resolve()

    def snapshot(self) -> dict[str, FileResidue]:
        self.world_root.mkdir(parents=True, exist_ok=True)
        residues: dict[str, FileResidue] = {}
        for path in sorted(self.world_root.rglob("*")):
            relative = str(path.relative_to(self.world_root))
            if path.is_dir():
                residues[relative] = FileResidue(
                    kind="directory",
                    path=relative,
                    sha256="directory",
                    size=0,
                    preview="",
                )
            elif path.is_file():
                data = path.read_bytes()
                residues[relative] = FileResidue(
                    kind="file",
                    path=relative,
                    sha256=sha256(data).hexdigest(),
                    size=len(data),
                    preview=self._preview(data),
                )
        return residues

    @staticmethod
    def _preview(data: bytes) -> str:
        text = data[:400].decode("utf-8", errors="replace")
        return text.replace("\x00", "\\0")
