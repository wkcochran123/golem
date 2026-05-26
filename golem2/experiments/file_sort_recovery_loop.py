from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..policies.file_sort_recovery_scripted import ScriptedRecoveryPolicy
from .file_sort_loop import FileSortLoop


def main() -> None:
    run_root = Path(__file__).resolve().parents[1] / "runs" / "file_sort_recovery_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    loop = FileSortLoop(run_root, policy=ScriptedRecoveryPolicy())
    loop.setup()

    ticks = []
    for _ in range(14):
        result = loop.tick()
        ticks.append(result)
        if result["grade"]["score"] >= 1.0:
            ticks.append(loop.tick())
            break

    print(json.dumps({"run_root": str(run_root), "ticks": ticks}, indent=2))


if __name__ == "__main__":
    main()

