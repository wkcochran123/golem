from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    work = root / ".jupyter-work"
    os.environ.setdefault("MPLCONFIGDIR", str(work / "matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", str(work / "cache"))
    os.environ.setdefault("JUPYTER_CONFIG_DIR", str(work / "config"))
    os.environ.setdefault("JUPYTER_DATA_DIR", str(work / "data"))
    os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(work / "runtime"))
    os.environ.setdefault("IPYTHONDIR", str(work / "ipython"))
    for path in (
        os.environ["MPLCONFIGDIR"],
        os.environ["XDG_CACHE_HOME"],
        os.environ["JUPYTER_CONFIG_DIR"],
        os.environ["JUPYTER_DATA_DIR"],
        os.environ["JUPYTER_RUNTIME_DIR"],
        os.environ["IPYTHONDIR"],
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

    notebook = json.loads(
        (root / "golem2/notebooks/06_maze_navigation_demo.ipynb").read_text(
            encoding="utf-8"
        )
    )
    if not notebook.get("cells"):
        raise SystemExit("notebook has no cells")

    try:
        import matplotlib
    except ModuleNotFoundError:
        print("notebook structure ok; skipped code execution (matplotlib missing)")
        return

    matplotlib.use("Agg")
    namespace: dict[str, object] = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            exec("".join(cell["source"]), namespace)
    print("notebook code cells ok")


if __name__ == "__main__":
    main()
