from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..runtime.loop import LocalWorldLoop


def main() -> None:
    run_root = Path(__file__).resolve().parents[1] / "runs" / "local_file_loop"
    if run_root.exists():
        shutil.rmtree(run_root)
    loop = LocalWorldLoop(run_root)
    results = [loop.tick(), loop.tick()]
    print(json.dumps({"run_root": str(run_root), "ticks": results}, indent=2))


if __name__ == "__main__":
    main()
