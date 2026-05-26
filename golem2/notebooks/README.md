# Notebooks

Notebook ideas for exploring `golem2` behavior:

- `01_heatmap_basics.ipynb`: tweak sensor grids and watch signed heat-map
  scores, changed cells, and thresholds.
- `02_projection_latches.ipynb`: vary parent urgency splits and see EMA/trial
  behavior.
- `03_ideal_basement.ipynb`: move a simulated robot through a perfect box room
  and inspect before/after proximity panoramas.
- `04_mapping_from_proximity.ipynb`: build an occupancy map from perfect 8-ray
  scans.
- `05_sleep_replay.ipynb`: sample high-urgency and failed transitions from a
  generated JSONL ledger.
- `06_maze_navigation_demo.ipynb`: a playful simulation where the robot clips
  unsafe motion, builds a 2-D occupancy map, and solves a maze through known
  free cells.

The notebooks should be playful sandboxes, not production dependencies. The
underlying experiments write JSON/JSONL so notebooks can reload and visualize
without rerunning control code.

## Launching On This Box

Use the repo launcher instead of the stale `jupyter` script on PATH:

```bash
./start_jupyter.sh
```

The launcher uses `python3 -m jupyterlab`, points Jupyter at this repository,
and stores runtime/config/cache files under `.jupyter-work/` so Matplotlib and
Jupyter do not try to write into unwritable home-directory caches.

To sanity-check the maze notebook without opening a browser:

```bash
python3 check_jupyter_demo.py
```
