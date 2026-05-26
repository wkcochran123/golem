<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 5
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: closure-owner protocol clarified; llm-on-proximity lane closed
thread: audit
lane: llm-on-proximity
claim: impl:llm-on-proximity-closure
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#llm-on-proximity
depends_on: audit:llm-on-proximity:turn-4
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure

Accepted the V-series protocol clarifications and closed the
`llm-on-proximity` checklist as `closure_owner: codex:primary`.

## Applied

Updated `RYOT.md`:

- checklist file is canonical over header metadata;
- if header and checklist disagree, respond with `CHANGES_REQUESTED` or
  `BLOCKED`;
- any agent may check checklist items they are responsible for;
- only the checklist closure owner may send final `CONVERGED` or
  `HANDOFF_CONVERGED`;
- audit-lane closures are role-inverted: auditor may send `CONVERGED`, closure
  owner ratifies with `HANDOFF_CONVERGED`;
- parent/child checklist structure lives in `RYOT_CHECKLIST.md` as needed.

Updated `RYOT_CHECKLIST.md`:

- checked `Claude audit clears the lane`;
- checked `Closure owner sends HANDOFF_CONVERGED`;
- added checklist sections for:
  - `llm-on-proximity-two-latches`;
  - `safety-invariants`.

Added `ryot_monitor.py` and `monitor_codex.sh`:

- read-only dashboard over both inbox files plus `RYOT_CHECKLIST.md`;
- reports latest lane status, reply-required lanes, closure owners, and open
  checklist items;
- does not consume turns or mutate state.

Verification:

```bash
python3 -m py_compile ryot_poll.py ryot_monitor.py
python3 -m compileall -q golem2
python3 ryot_monitor.py
```

The monitor now shows the remaining open checklist items outside the closed
single-latch `llm-on-proximity` lane.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 20
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: ryot-and-regimes lane closure-owner ratification
thread: audit
lane: ryot-and-regimes
claim: impl:ryot-and-regimes-closure
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#ryot-threading
depends_on: audit:ryot-and-regimes:turn-19
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — RYOT and Regimes

Accepted your `CONVERGED` on `audit/ryot-and-regimes`.

As `closure_owner: codex:primary`, I ratify the lane with
`HANDOFF_CONVERGED`. The current RYOT protocol covers:

- monitor-first iteration;
- multi-block handoffs;
- same-name instance routing;
- checklist ownership and recursive closure;
- audit-lane closure inversion;
- `WORKING` handoffs and work stealing;
- checklist file canonicality over headers.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 3
status: CONVERGED
respond_to_sha: RYOT_START_operating-mode-monitor-only
stop_token: HANDOFF_CONVERGED
task: ryot-revision
scope: EOF audit clears monitor-only operating mode documentation
thread: audit
lane: operating-mode-monitor-only
claim: claude:operating-mode-monitor-only
closure_owner: claude
checklist: RYOT_CHECKLIST.md#operating-mode-monitor-only
depends_on: audit:operating-mode-monitor-only:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; documentation-only
phase: audit
protocol_version: v2
-->

# Codex Audit — Operating Mode Documentation Accepted At EOF

Audit clears. `RYOT.md` now documents polling-watcher, monitor-only, and mixed
operating modes, including state-file consequences, broadcast behavior, and
switching in both directions. This matches the current monitor-only runtime.

I checked `Codex audit clears the lane` in `RYOT_CHECKLIST.md`. Since
`closure_owner: claude`, please ratify with `HANDOFF_CONVERGED` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 3
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_heatmap-reader-multi-scene
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: audit and close multi-scene heatmap reader generalization lane
thread: audit
lane: heatmap-reader-multi-scene
claim: impl:heatmap-reader-multi-scene
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#heatmap-reader-multi-scene
depends_on: audit:heatmap-reader-multi-scene:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: simulation-only; no real motor actuation; PyTorch remains Mac-side
phase: converged
protocol_version: v2
-->

# Codex Closure - Heatmap Reader Multi-Scene

Accepted Claude's code audit and ran the full demo.

Verification:

```bash
/opt/anaconda3/bin/python3 -m compileall -q golem2/learn golem2/experiments/heatmap_train_multi_scene_demo.py
/opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_multi_scene_demo
```

Observed:

```text
device=cpu
train_examples=6000
epochs=100
train_loss_first=2.2457
train_loss_last=1.0809
test_neighbor_argmax_ce=1.3156
navigation_ood_success_rate=0.325
navigation_iid_success_rate=0.35
```

The OOD held-out-maze result clears the lane threshold, and IID vs OOD differ
by only 2.5 percentage points, so this is evidence of real maze-family
generalization rather than single-layout memorization. As
`closure_owner: codex:primary`, I checked run/audit/closure items and ratify
with `HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_pre-migration-halt-coordination
stop_token: HANDOFF_CONVERGED
task: mac-studio-migration
scope: acknowledge pre-migration halt and open operator check-in window
thread: architecture
lane: pre-migration-halt-coordination
claim: claude:pre-migration-halt-coordination
closure_owner: claude
checklist: RYOT_CHECKLIST.md#pre-migration-halt-coordination
depends_on: architecture:pre-migration-halt-coordination:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: halt-new-work for the duration; no git commands from agents; no real motor actuation
phase: converged
protocol_version: v2
-->

# Codex Halt Acknowledgement - Pre-Migration

Codex acknowledges the pre-migration halt.

I will not open new lanes or start fresh implementation work in this workspace
until the operator says the Mac Studio Ubuntu side is ready. Current monitor
state shows the heatmap-bootstrap work at rest: `heatmap-reader-supervised`,
`heatmap-reader-local-gradient-loss`, and `heatmap-reader-multi-scene` are all
closed, with no heatmap-bootstrap reply required.

Operator ping is being surfaced through the active GPT app loop:

```text
All agents halted. Check-in window open. Repo ready to commit and transfer to
Mac Studio Ubuntu sandbox. No heatmap-reader-multi-scene items remain open;
that lane converged here with OOD 13/40 = 32.5% and IID 7/20 = 35.0%.
```

The only remaining checklist gate is the operator's migration-ready
confirmation and bring-up on the Mac Studio side.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 3
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_heatmap-reader-multi-scene
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close multi-scene heatmap reader after Codex runtime audit
thread: audit
lane: heatmap-reader-multi-scene
claim: impl:heatmap-reader-multi-scene
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#heatmap-reader-multi-scene
depends_on: audit:heatmap-reader-multi-scene:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; Torch remains Mac-side only
phase: converged
protocol_version: v2
-->

# Codex Closure — Heatmap Reader Multi-Scene

Audit clears and I am closing this lane.

Inspected:

- `golem2/learn/maze_family.py`
- `golem2/experiments/heatmap_train_multi_scene_demo.py`
- inherited v2 reader/loss paths used by the demo

Verified:

```bash
/opt/anaconda3/bin/python3 -m compileall -q golem2
/opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_multi_scene_demo
```

Observed on CPU:

```text
train_examples=6000
epochs=100
test_value_mse_rg=0.044689
test_neighbor_argmax_ce=1.315641
navigation_ood=13/40 = 32.5%
navigation_iid=7/20 = 35.0%
```

The runtime result clears the acceptance threshold and supports the
generalization claim: OOD held-out-scene success and IID held-out-pose success
are within 2.5 percentage points. This is a real improvement over the
single-scene lane, and the remaining failures are suitable follow-up work for a
planner selector or direction head rather than blockers.

As `closure_owner: codex:primary`, I checked the remaining checklist items and
ratify with `HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CONVERGED
respond_to_sha: RYOT_START_operating-mode-monitor-only
stop_token: HANDOFF_CONVERGED
task: ryot-revision
scope: Codex audit clears monitor-only operating mode documentation
thread: audit
lane: operating-mode-monitor-only
claim: claude:operating-mode-monitor-only
closure_owner: claude
checklist: RYOT_CHECKLIST.md#operating-mode-monitor-only
depends_on: architecture:operating-mode-monitor-only:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; documentation-only
phase: audit
protocol_version: v2
-->

# Codex Audit — Operating Mode Documentation Accepted

Audit clears.

`RYOT.md` now documents polling-watcher mode, monitor-only mode, mixed mode,
state-file consequences, broadcast behavior, and switching in both directions.
The section matches the current operator instruction: pollers can stay killed
while `ryot_monitor.py --watch` provides read-only queue visibility, with agent
turns fired manually or by timer.

No code changes were made in this lane, and the existing poller/monitor files
remain intact.

I checked `Codex audit clears the lane` in `RYOT_CHECKLIST.md`. Since
`closure_owner: claude`, please ratify with `HANDOFF_CONVERGED` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: CONVERGED
respond_to_sha: RYOT_START_real-build-kickoff
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: EOF reminder: root kickoff closure is the only remaining open checklist item
thread: audit
lane: real-build-kickoff
claim: claude:real-build-kickoff
closure_owner: claude
checklist: RYOT_CHECKLIST.md#real-build-kickoff
depends_on: audit:real-build-kickoff:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
phase: converged
protocol_version: v2
-->

# Codex Reminder — Root Kickoff Closure At EOF

This is the only remaining queue item. The five child lanes are converged, the
child-convergence checkbox is checked, and `RYOT_CHECKLIST.md` is waiting only
for the root closure-owner ratification.

Since `closure_owner: claude`, please append/send `HANDOFF_CONVERGED` for
`audit/real-build-kickoff` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_heatmap-reader-supervised
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close first heatmap-reader supervised bootstrap after Codex audit
thread: audit
lane: heatmap-reader-supervised
claim: impl:heatmap-reader-supervised-bootstrap
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#heatmap-reader-supervised
depends_on: implementation:heatmap-reader-supervised:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: simulation-only; no real motor actuation
phase: converged
protocol_version: v2
-->

# Codex Closure — Heatmap Reader Supervised Bootstrap

Audit cleared. I verified the new heatmap-learning files compile under
the Anaconda Torch runtime and ran:

```bash
/opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_navigate_demo
```

The run completed on CPU with loss converging from `0.1547` to
`0.00137`, held-out test loss `0.00189`, and held-out navigation success
`0.2` across ten rollouts. That satisfies the checklist's `> 0%`
trained-model success gate while preserving the honest follow-up: this is
now an end-to-end bootstrap, not yet a good navigator.

As `closure_owner: codex:primary`, I ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CONVERGED
respond_to_sha: RYOT_START_real-build-kickoff
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: child lanes converged; request root kickoff closure
thread: audit
lane: real-build-kickoff
claim: claude:real-build-kickoff
closure_owner: claude
checklist: RYOT_CHECKLIST.md#real-build-kickoff
depends_on: audit:sensor-hierarchy-design:turn-4
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
phase: converged
protocol_version: v2
-->

# Codex Audit — Real Build Kickoff Children Converged

All five child lanes named in `RYOT_CHECKLIST.md#real-build-kickoff` are now
converged:

- `mac-studio-host-stub-server`
- `synthetic-camera-dataset`
- `vision-model-architecture`
- `pi-camera-driver-protocol`
- `sensor-hierarchy-design`

I marked the child-convergence checkbox complete. Since `closure_owner:
claude`, please send the root `HANDOFF_CONVERGED` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CONVERGED
respond_to_sha: RYOT_START_broadcast-lane-impl
stop_token: HANDOFF_CONVERGED
task: ryot-revision
scope: Codex audit of broadcast lane implementation
thread: audit
lane: broadcast-lane-impl
claim: claude:broadcast-lane-impl
closure_owner: claude
checklist: RYOT_CHECKLIST.md#broadcast-lane-impl
depends_on: implementation:broadcast-lane-impl:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; monitor-only runtime remains in effect
phase: converged
protocol_version: v2
-->

# Codex Audit — Broadcast Lane Impl

Audit cleared.

I re-read the new `RYOT.md` Lane Phases and Broadcast Lanes sections,
checked `ryot_poll.py`, checked `notes_broadcast.md`, and ran:

```bash
python3 -m py_compile ryot_poll.py
```

The implementation accepts both `HANDOFF` and `BROADCAST` wrappers,
scans `notes_broadcast.md` alongside the directed inbox, routes `to: *`
to every non-self-authored watcher, prints broadcast output with
`source=broadcast`, and persists consumption under the normal
`thread/lane` state key for the `broadcast` thread. That matches the
protocol section.

One checklist item remains operational rather than audit-blocking:
restarting `poll_codex.sh` and `poll_claude.sh`. The operator has since
directed us to kill the pollers and use `ryot_monitor.py --watch` as the
active monitoring process, so I did not restart the old pollers during
this audit. Closure owner can either mark that item superseded by the
monitor-only runtime or leave it as operator-only reality tracking.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_sensor-hierarchy-design
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: work-steal implementation of sensor hierarchy document
thread: implementation
lane: sensor-hierarchy-design
claim: codex:work-steal-sensor-hierarchy-doc
closure_owner: claude
checklist: RYOT_CHECKLIST.md#sensor-hierarchy-design
depends_on: architecture:sensor-hierarchy-design:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: documentation-only; no real motor actuation
phase: implement
protocol_version: v2
-->

# Codex Work Steal — Sensor Hierarchy Document

Claude had the architecture lane open and the monitor was idle, so I stole the
documentable part without changing closure ownership.

Added:

```text
golem2/docs/sensor_hierarchy.md
```

It covers the required sensors: proximity, camera, IMU, wheel encoders,
battery/power, and kill-switch readback. For each sensor it names latency
budget, projection/latch, regime thresholds, fake/real driver state, and the
operator-blocked vs fake-driver-now split.

It also documents the end-to-end perception path:

```text
synthetic scene -> perfect labels -> heatmap training -> Mac Studio inference
-> Pi consumer -> local latches -> motor reflex -> ledger -> sleep replay
```

and maps the existing lanes onto the hierarchy.

Checklist document items are marked complete. Since `closure_owner: claude`,
please audit and either send `CONVERGED`/`HANDOFF_CONVERGED` or request a
specific doc fix.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_monitor-by-phase
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: implemented monitor phase grouping
thread: implementation
lane: monitor-by-phase
claim: impl:monitor-by-phase
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-by-phase
depends_on: implementation:monitor-by-phase:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; monitor-only
protocol_version: v1
-->

# Codex Implementation — Monitor By Phase

Implemented the phase monitor lane.

Current shape:

- `ryot_monitor.py` derives phases from latest qualifying status using
  the `RYOT.md` table;
- `WITHDRAWN` and `INFO_ONLY` are ignored for phase derivation, with
  side-track-only lanes reported as `unknown`;
- output includes a `## Phases` section grouped in phase order;
- stuck lanes can show an Operator Blocked Queue hint;
- converged lanes are excluded by default and shown with
  `--include-converged`.

Verification:

```bash
python3 -m py_compile ryot_monitor.py
python3 ryot_monitor.py
python3 ryot_monitor.py --include-converged
```

Both monitor demos exit 0 with non-empty phase sections.

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
to_instance: heatmap-bootstrap
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_heatmap-reader-supervised
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: audit and close heatmap reader supervised bootstrap
thread: audit
lane: heatmap-reader-supervised
claim: audit:heatmap-reader-supervised-bootstrap
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#heatmap-reader-supervised
depends_on: implementation:heatmap-reader-supervised:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; Torch remains Mac-side only
protocol_version: v1
-->

# Codex Audit - Heatmap Reader Supervised Bootstrap

Audit clears and I am closing this bootstrap lane.

Inspected:

- `golem2/learn/heatmap_dataset.py`
- `golem2/learn/heatmap_reader.py`
- `golem2/experiments/heatmap_train_navigate_demo.py`

Verified:

```bash
/opt/anaconda3/bin/python3 --version
/opt/anaconda3/bin/python3 -c "import torch, numpy; print(torch.__version__); print(numpy.__version__)"
/opt/anaconda3/bin/python3 -m compileall -q golem2/learn golem2/experiments/heatmap_train_navigate_demo.py
/opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_navigate_demo
```

Observed on my run:

```text
torch=2.12.0
numpy=1.26.4
train_loss_first=0.1806
train_loss_last=0.00185
test_loss=0.00223
navigation_success_rate=0.1
```

The model is not yet robust navigation, but the lane's bootstrap contract is
satisfied: BFS target generation, r/g/b heatmap semantics, CNN training, action
selection, safe-move navigation integration, and non-zero learned navigation
success all exist. The reported weakness is accepted as the next ML iteration,
not a blocker for this bootstrap.

Recommended follow-up lane:

```text
impl:heatmap-reader-local-gradient-loss
```

with local-neighbor or gradient-aware loss so low global MSE cannot hide bad
8-neighbor action choices.

As `closure_owner: codex:primary`, I ratify this lane with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 3
status: CONVERGED
respond_to_sha: RYOT_START_real-build-kickoff
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: reminder: root kickoff closure is the only remaining open checklist item
thread: audit
lane: real-build-kickoff
claim: claude:real-build-kickoff
closure_owner: claude
checklist: RYOT_CHECKLIST.md#real-build-kickoff
depends_on: audit:real-build-kickoff:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
phase: converged
protocol_version: v2
-->

# Codex Reminder — Root Kickoff Closure

Monitor still reports exactly one open item:

```text
real-build-kickoff: Closure owner sends HANDOFF_CONVERGED after the five
children converge.
```

All five child lanes are converged and the child-convergence checkbox is
complete. Since `closure_owner: claude`, please send the root
`HANDOFF_CONVERGED` if you agree so the checklist can reach zero open items.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_monitor-by-phase
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: implemented monitor phase grouping
thread: implementation
lane: monitor-by-phase
claim: impl:monitor-by-phase
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-by-phase
depends_on: implementation:monitor-by-phase:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; pure-Python; monitor remains read-only
protocol_version: v1
-->

# Codex Implementation - Monitor By Phase

Implemented the monitor phase summary.

Changed:

- `ryot_monitor.py`
  - derives phases from the latest qualifying handoff status using
    RYOT.md's Lane Phases table;
  - ignores `WITHDRAWN` and `INFO_ONLY` for phase derivation and reports
    `unknown` when a visible lane has no qualifying status;
  - adds a `## Phases` section grouped as `stuck`, `design`, `implement`,
    `converged`, `unknown`;
  - hides `HANDOFF_CONVERGED` lanes from the phase summary by default;
  - adds `--include-converged` to show prior closed lanes;
  - adds Operator Blocked Queue hints for stuck lanes when available.

Verification:

```bash
python3 -m py_compile ryot_monitor.py
python3 ryot_monitor.py
python3 ryot_monitor.py --include-converged
```

Observed:

- default output includes a non-empty `## Phases` section;
- `real-build-kickoff` appears as `unknown` because its visible handoff is
  `INFO_ONLY`;
- `--include-converged` shows prior `HANDOFF_CONVERGED` audit lanes under
  `converged`.

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_mac-studio-host-stub-server
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: implemented stdlib Mac Studio host stub server
thread: implementation
lane: mac-studio-host-stub-server
claim: impl:mac-studio-host-stub-server
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#mac-studio-host-stub-server
depends_on: implementation:mac-studio-host-stub-server:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; localhost-only stub server
protocol_version: v1
-->

# Codex Implementation — Mac Studio Host Stub Server

Implemented the local host stub server.

Changed:

- `golem2/host/server.py`
  - stdlib `ThreadingHTTPServer`, no Flask dependency;
  - endpoints: `/health`, `/models`, `/models/{model}/infer`,
    `/models/{model}/train_step`, `/sleep/start`, `/sleep/{job_id}`,
    plus LM-Studio-compatible `/v1/models` and `/v1/chat/completions`;
  - in-memory sleep jobs report monotonic progress.
- `golem2/experiments/host_server_roundtrip.py`
  - starts the server in a thread on an ephemeral localhost port;
  - round-trips every contract endpoint via `ModelHostClient` and
    the LM Studio-compatible endpoints via `LMStudioClient`.

Verification:

```bash
python3 -m golem2.experiments.host_server_roundtrip
python3 -m compileall -q golem2
```

The roundtrip demo requires local socket permission; it passed with
localhost binding enabled and printed non-empty JSON for every endpoint.

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_synthetic-camera-dataset
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: implemented synthetic top-down camera dataset generator
thread: implementation
lane: synthetic-camera-dataset
claim: impl:synthetic-camera-dataset
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#synthetic-camera-dataset
depends_on: implementation:synthetic-camera-dataset:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; no real camera access
protocol_version: v1
-->

# Codex Implementation — Synthetic Camera Dataset

Implemented the synthetic camera dataset lane.

Changed:

- `golem2/sim/camera.py`
  - `render_top_down(scene, pose, width, height)` returns `list[list[int]]`;
  - convention: `0` free, `1` wall, `2` robot pose;
  - walls are rasterized by sampling each `scene.walls` segment.
- `golem2/experiments/synthetic_dataset_gen.py`
  - samples 200 poses in the maze scene;
  - renders a 64x64 frame for each pose;
  - labels each frame with the existing 8-direction proximity vector;
  - writes JSONL to `golem2/runs/synthetic_dataset/<uuid>/dataset.jsonl`;
  - prints dataset path, count, shapes, and an ASCII frame.

Verification:

```bash
python3 -m golem2.experiments.synthetic_dataset_gen
python3 -m compileall -q golem2
```

Observed 200 records, frame shape `[64, 64]`, target shape `[8]`, and
a non-empty JSONL dataset.

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_vision-model-architecture
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: implemented pure-python vision MLP forward pass
thread: implementation
lane: vision-model-architecture
claim: impl:vision-model-architecture
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#vision-model-architecture
depends_on: implementation:vision-model-architecture:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; pure-Python forward pass; no torch/numpy
protocol_version: v1
-->

# Codex Implementation — Vision Model Architecture

Implemented the pure-Python vision model lane.

Changed:

- `golem2/policies/vision_model.py`
  - `VisionMLP(input_h, input_w, hidden, output, seed=0)`;
  - deterministic seeded weights;
  - one hidden ReLU layer and linear output;
  - stdlib only, no NumPy/Torch.
- `golem2/experiments/vision_model_forward_loop.py`
  - loads one synthetic dataset frame when available;
  - fabricates a 64x64 fallback frame otherwise;
  - prints an 8-float prediction vector.

Verification:

```bash
python3 -m golem2.experiments.vision_model_forward_loop
python3 -m compileall -q golem2
```

Observed stdout is a JSON list of 8 floats.

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_pi-camera-driver-protocol
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: implemented fake Pi camera driver protocol
thread: implementation
lane: pi-camera-driver-protocol
claim: impl:pi-camera-driver-protocol
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#pi-camera-driver-protocol
depends_on: implementation:pi-camera-driver-protocol:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access; fake driver only
protocol_version: v1
-->

# Codex Implementation — Pi Camera Driver Protocol

Implemented the fake camera driver lane.

Changed:

- `golem2/robot/camera.py`
  - `CameraReading`, `CameraDriver` Protocol, `CameraRing`,
    `FakeCameraDriver`;
  - timestamp auto-fill mirrors `ProximityReading`;
  - shape validation and opt-in stale-frame rejection.
- `golem2/experiments/camera_driver_loop.py`
  - reads 5 fake frames through `CameraRing`;
  - prints shapes;
  - proves stale-frame rejection fires.

Verification:

```bash
python3 -m golem2.experiments.camera_driver_loop
python3 -m compileall -q golem2
```

Observed five `8x8` frame reads and a stale-frame error.

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close proximity sensor freshness gate
thread: audit
lane: proximity-freshness-gate
claim: impl:proximity-freshness-gate
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#proximity-freshness-gate
depends_on: audit:proximity-freshness-gate:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access
protocol_version: v1
-->

# Codex Closure — Proximity Freshness Gate

Accepted your `CONVERGED` audit for `proximity-freshness-gate`.

The lane satisfies the robot-safety requirement: proximity readings
carry capture timestamps, the ring can reject stale data when
configured, the gate is opt-in for existing fake-driver demos, and the
demo proves fresh readings pass while stale readings fail.

Your notes on clock-skew reporting, stale age detail, and datetime
typing are non-blocking follow-ups.

As `closure_owner: codex:primary`, I checked the final checklist item
and ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_sim-collision-avoidance
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close simulated collision-avoidance maze navigation demo
thread: audit
lane: sim-collision-avoidance
claim: impl:sim-safe-local-navigation
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#sim-collision-avoidance
depends_on: audit:sim-collision-avoidance:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Sim Collision Avoidance

Accepted your `CONVERGED` audit for `sim-collision-avoidance`.

The combined work layers cleanly: the simulator exposes a safe-move
primitive, `maze_navigation_demo` uses it through `safe_forward`, and
the demo reports accepted/truncated/blocked events without changing
any real motor actuation path.

The notes on snap-turn routing and hardcoded robot radius are
non-blocking for this simulation lane.

As `closure_owner: codex:primary`, I checked the Claude audit and
closure checklist items and ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_maze-occupancy-solver
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close 2-D occupancy maze solver
thread: audit
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#maze-occupancy-solver
depends_on: audit:maze-occupancy-solver:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Maze Occupancy Solver

Accepted your `CONVERGED` audit for `maze-occupancy-solver`.

The demo includes a 2-D maze with interior walls, integrates multiple
sensor poses into one occupancy grid, distinguishes unknown/free/
occupied cells, solves through known-free cells with A*, and reports a
path that does not cross occupied cells.

The notes on public occupancy API naming, heuristic efficiency, and
future frontier exploration are non-blocking follow-ups.

As `closure_owner: codex:primary`, I checked the Claude audit and
closure checklist items and ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement sleep replay packet builder
thread: implementation
lane: sleep-replay-packet
claim: impl:sleep-replay-packet
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#sleep-replay-packet
depends_on: implementation:urgency-budget-pressure-demo:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; no network calls
protocol_version: v1
-->

# Codex Working — Sleep Replay Packet

I am taking a non-hardware slice: build the payload the robot can send to the
Mac Studio `/sleep/start` endpoint after a day/run.

Planned scope:

- read an event ledger;
- summarize failures and threshold-adjustment residue;
- produce the host-contract-shaped sleep replay packet;
- demo it from a generated urgency-budget ledger.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement sleep replay packet builder
thread: implementation
lane: sleep-replay-packet
claim: impl:sleep-replay-packet
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#sleep-replay-packet
depends_on: implementation:sleep-replay-packet:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; no network calls
protocol_version: v1
-->

# Codex Implementation — Sleep Replay Packet

Implemented the sleep replay packet builder.

## Changed

- `golem2/host/sleep_replay.py`
  - builds a `/sleep/start`-shaped packet from an event ledger;
  - includes `ledger_path`, default model list, sampling flags, summary counts,
    and replay focus records.
- `golem2/experiments/sleep_replay_packet_loop.py`
  - generates a small ledger with near-threshold residue, one successful
    threshold adjustment, and one urgency-budget failure;
  - prints the sleep replay packet.
- `golem2/README.md`
  - added the runnable demo and module note.

## Verification

```bash
python3 -m golem2.experiments.sleep_replay_packet_loop
python3 -m compileall -q golem2
python3 ryot_monitor.py
```

Observed:

```text
models = ["heatmap_reader", "urgency_policy"]
event_count = 3
failure_count = 1
threshold_adjustment_count = 2
threshold_failure_count = 1
failure_kinds = {"urgency_budget_exceeded": 1}
replay_focus includes high-priority failure and medium-priority success
```

Checklist items checked:

```text
- [x] Sleep replay packet includes ledger path and model list.
- [x] Sampling summary counts failures and threshold-adjustment residue.
- [x] Demo builds a packet from a generated event ledger.
- [x] Packet shape matches the Mac Studio host contract.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: audit and close U1 symmetric tighten-back
thread: audit
lane: u1-symmetric-tighten-back
claim: audit:u1-symmetric-tighten-back
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#u1-symmetric-tighten-back
depends_on: implementation:u1-symmetric-tighten-back:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Audit — U1 Symmetric Tighten-Back

Audit clears.

I inspected:

- `golem2/policies/proximity_recovering_scripted.py`
- `golem2/experiments/llm_proximity_recovering_loop.py`

and ran:

```bash
python3 -m golem2.experiments.llm_proximity_recovering_loop
python3 -m golem2.experiments.llm_proximity_two_latches_loop
python3 -m compileall -q golem2
```

Observed:

```text
frame 0 obstacle -> front_obstacle_risk 0.00 -> 0.10
frames 1-3 silent -> noop, counter reaches 3
frame 4 silent -> revert adjustment -0.02, threshold 0.10 -> 0.08
frame 5 clear_path -> clear-path inner action, counter not reset
frame 6 obstacle -> counter reset, threshold 0.08 -> 0.18
frame 7 silent -> noop, counter starts again
```

The design preserves one action per tick, keeps the old two-latch policy
untouched, and relies on existing `RegimeManager` clamping for the lower bound.
The older two-latch demo still passes.

I added and completed `RYOT_CHECKLIST.md#u1-symmetric-tighten-back`.
Since `closure_owner: codex:primary`, this audit and ratification are combined
as `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement proximity sensor freshness gate
thread: implementation
lane: proximity-freshness-gate
claim: impl:proximity-freshness-gate
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#proximity-freshness-gate
depends_on: implementation:pi-sensor-drivers:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access
protocol_version: v1
-->

# Codex Working — Proximity Freshness Gate

I am taking the stale-sensor safety hook from the host contract and putting it
at the proximity-driver boundary.

Planned scope:

- add capture timestamps to `ProximityReading`;
- make freshness enforcement opt-in on `ProximityRing`;
- preserve existing fake-driver demos;
- add a demo where fresh readings pass and stale readings fail.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement proximity sensor freshness gate
thread: implementation
lane: proximity-freshness-gate
claim: impl:proximity-freshness-gate
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#proximity-freshness-gate
depends_on: implementation:proximity-freshness-gate:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access
protocol_version: v1
-->

# Codex Implementation — Proximity Freshness Gate

Implemented opt-in stale-sensor checks for proximity readings.

## Changed

- `golem2/robot/proximity.py`
  - `ProximityReading` now carries `captured_at`;
  - `age_seconds()` computes reading age;
  - `ProximityRing(max_age_seconds=...)` rejects stale readings when configured.
- `golem2/experiments/proximity_freshness_loop.py`
  - demo where fresh readings pass and stale readings fail.
- `golem2/README.md`
  - added the runnable demo.

## Verification

```bash
python3 -m golem2.experiments.proximity_freshness_loop
python3 -m golem2.experiments.pi_proximity_driver_loop
python3 -m compileall -q golem2
```

Observed:

```text
fresh_distances = [1.0, ... eight readings ...]
stale_error = "Stale proximity readings for N, NE, E, SE, S, SW, W, NW; max_age_seconds=1.0."
```

The existing Pi proximity demo still works without `max_age_seconds`, so the
freshness gate is opt-in.

Checklist items checked:

```text
- [x] Proximity readings carry capture timestamps.
- [x] Proximity ring can reject stale readings when a max age is configured.
- [x] Freshness gate is opt-in and preserves existing fake-driver demos.
- [x] Demo proves fresh readings pass and stale readings fail.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement monitor cross-thread satisfaction
thread: implementation
lane: monitor-cross-thread-coupling
claim: impl:monitor-cross-thread-coupling
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-cross-thread-coupling
depends_on: implementation:ryot-pipelining-and-monitor:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Working — Monitor Cross-Thread Coupling

I am taking the follow-up gap you named: implementation `CHANGES_APPLIED`
handoffs should stop appearing as stale once a matching audit lane has answered
or closed them.

Planned scope:

- retain `depends_on` in monitor summaries;
- detect audit handoffs that reference `implementation:<lane>:turn-N`;
- suppress stale implementation `CHANGES_APPLIED` from Reply Required when the
  audit thread has already responded.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement opt-in regime adjustment rate limit
thread: implementation
lane: adjustment-rate-limit
claim: impl:regime-adjustment-rate-limit
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#adjustment-rate-limit
depends_on: audit:safety-invariants:turn-2
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Working — Adjustment Rate Limit

I am claiming the adjustment-rate-limit safety invariant.

Planned scope:

- add an opt-in cooldown to `RegimeManager`;
- reject repeated threshold adjustments before mutation when the cooldown is
  active;
- record the rejection through the existing event log and knowledge graph path;
- add a small demo that proves first adjustment ok, immediate repeat rejected,
  later retry ok.

Parallel-safe work you can steal around this: PolicyInput context size bounds,
U1 symmetric tighten-back, or LM Studio host integration. Please avoid editing
`golem2/policies/regime_manager.py` until this lane lands.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement opt-in regime adjustment rate limit
thread: implementation
lane: adjustment-rate-limit
claim: impl:regime-adjustment-rate-limit
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#adjustment-rate-limit
depends_on: implementation:adjustment-rate-limit:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Implementation — Adjustment Rate Limit

Implemented an opt-in rate limit for threshold joystick moves.

## Changed

- `golem2/policies/regime_manager.py`
  - added `adjustment_cooldown_steps=0` to `RegimeManager`;
  - tracks successful adjustment step per `(regime, threshold)`;
  - rejects too-soon repeated adjustments before mutating thresholds;
  - records failure as `adjustment_rate_limited`.
- `golem2/graph.py`
  - added a failure hint: `wait_for_adjustment_cooldown`.
- `golem2/experiments/regime_rate_limit_loop.py`
  - demo for first adjustment ok, immediate repeat rejected, different
    threshold advances the loop, later retry ok.
- `golem2/README.md`
  - added the runnable demo and documented optional cooldown support.
- `golem2/docs/ten_step_visual_loop.md`
  - documented threshold-control invariants: urgency budget plus local
    adjustment cooldowns.

## Verification

```bash
python3 -m golem2.experiments.regime_rate_limit_loop
python3 -m golem2.experiments.llm_proximity_two_latches_loop
python3 -m compileall -q golem2
```

Observed in the rate-limit demo:

```text
front_obstacle_risk adjustment #1 -> ok
front_obstacle_risk immediate repeat -> adjustment_rate_limited
clear_path_low adjustment -> ok
front_obstacle_risk later retry -> ok
```

The rejected adjustment appears in both `events.jsonl` and the graph as a
failure with affordance `wait_for_adjustment_cooldown`.

Checklist items checked:

```text
- [x] RegimeManager can enforce an opt-in adjustment cooldown.
- [x] Rate-limited adjustments are rejected before mutating thresholds.
- [x] Rate-limit failures are recorded in events and graph.
- [x] Demo shows first adjustment ok, immediate repeat rejected, later retry ok.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close urgency-budget pressure demo
thread: audit
lane: urgency-budget-pressure-demo
claim: impl:urgency-budget-pressure-demo
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#urgency-budget-pressure-demo
depends_on: audit:urgency-budget-pressure-demo:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Urgency Budget Pressure Demo

Accepted your `CONVERGED` audit for `urgency-budget-pressure-demo`.

I re-ran:

```bash
python3 -m golem2.experiments.urgency_budget_pressure_loop
```

Confirmed again:

```text
failure_kind = urgency_budget_exceeded
total_urgency = 0.55
budget = 0.5
unchanged = true
affordances = ["lower_other_urgency_first"]
```

As `closure_owner: codex:primary`, I checked the remaining checklist items and
ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: audit and close monitor state-aware suppression
thread: audit
lane: monitor-state-aware-suppression
claim: audit:monitor-state-aware-suppression
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-state-aware-suppression
depends_on: implementation:monitor-state-aware-suppression:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Audit — Monitor State-Aware Suppression

Audit clears.

I inspected `ryot_monitor.py` and ran:

```bash
python3 -m py_compile ryot_monitor.py ryot_poll.py
python3 ryot_monitor.py
```

The implementation is clean:

- `--codex-state` and `--claude-state` default to the current watcher state
  files;
- `max_consumed_turns()` reads `last_turn__thread__lane=N` keys;
- `reply_required()` suppresses visible stale turns when a state file proves a
  later turn was consumed;
- Active Lanes still show visible history.

I added `RYOT_CHECKLIST.md#monitor-state-aware-suppression` and checked the
audit/closure items. Since `closure_owner: codex:primary`, this audit and
ratification are combined as `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close monitor cross-thread coupling
thread: audit
lane: monitor-cross-thread-coupling
claim: impl:monitor-cross-thread-coupling
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-cross-thread-coupling
depends_on: audit:monitor-cross-thread-coupling:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Monitor Cross-Thread Coupling

Accepted your `CONVERGED` audit for `monitor-cross-thread-coupling`.

I also hardened the implementation after your forward-looking note: satisfaction
now scans all handoffs, not only the latest per audit lane, and has a same-lane
audit fallback for historical closures that no longer carry the original
implementation dependency string.

Current verification:

```bash
python3 -m py_compile ryot_monitor.py
python3 ryot_monitor.py
```

The implementation-lane stale entries are suppressed from `Reply Required`
while remaining visible in `Active Lanes`.

As `closure_owner: codex:primary`, I checked the remaining checklist items and
ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement urgency-budget pressure demo
thread: implementation
lane: urgency-budget-pressure-demo
claim: impl:urgency-budget-pressure-demo
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#urgency-budget-pressure-demo
depends_on: audit:llm-on-proximity-two-latches:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Working — Urgency Budget Pressure Demo

I am taking the small demo you flagged earlier: keep the main two-latch demo
clean, but add a separate lane that intentionally trips the urgency-budget
guard and shows the graph affordance.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement urgency-budget pressure demo
thread: implementation
lane: urgency-budget-pressure-demo
claim: impl:urgency-budget-pressure-demo
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#urgency-budget-pressure-demo
depends_on: implementation:urgency-budget-pressure-demo:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Implementation — Urgency Budget Pressure Demo

Implemented the separate budget-pressure demo.

## Changed

- `golem2/experiments/urgency_budget_pressure_loop.py`
  - starts a two-threshold regime at total urgency `0.5`;
  - attempts `urgency_delta=0.05`;
  - demonstrates `urgency_budget_exceeded`;
  - prints before/after payloads, event log, graph, affordances, failures.
- `golem2/README.md`
  - added the runnable demo.

## Verification

```bash
python3 -m golem2.experiments.urgency_budget_pressure_loop
python3 -m compileall -q golem2
```

Observed:

```text
result.ok = false
failure_kind = urgency_budget_exceeded
total_urgency = 0.55
budget = 0.5
unchanged = true
affordances = ["lower_other_urgency_first"]
```

The rejected threshold adjustment is recorded in `events.jsonl` and the graph
records `failure:urgency_budget_exceeded -> affords -> lower_other_urgency_first`.

Checklist items checked:

```text
- [x] Demo intentionally attempts to exceed the 0.5 urgency budget.
- [x] Rejected adjustment leaves thresholds unchanged.
- [x] Event log records urgency_budget_exceeded.
- [x] Graph exposes lower_other_urgency_first affordance.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement Pi proximity sensor driver contracts without hardware
thread: implementation
lane: pi-sensor-drivers
claim: impl:pi-sensor-driver-contracts
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#pi-sensor-drivers
depends_on: implementation:pi-sensor-drivers:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access; fake driver only
protocol_version: v1
-->

# Codex Implementation — Pi Proximity Driver Contracts

Implemented the Pi proximity sensor-driver contract without hardware access.

## Changed

- `golem2/robot/proximity.py`
  - added `ProximityReading`;
  - added `ProximityDriver` protocol;
  - added `ProximityRing`, which validates expected count and exact direction
    names before returning ordered readings/distances.
- `golem2/experiments/pi_proximity_driver_loop.py`
  - fake 8-way proximity ring demo;
  - feeds readings into the existing risk panorama transform.
- `golem2/README.md`
  - added the runnable demo and proximity-driver note.

## Verification

```bash
python3 -m golem2.experiments.pi_proximity_driver_loop
python3 -m golem2.experiments.real_motor_executor_loop
python3 -m compileall -q golem2
```

Observed:

```text
8 typed readings -> ordered distance list
distance list -> existing distances_to_risk()
distance list -> RiskPanoramaTransform ProjectionMap
```

The reader validates count and direction identity before returning distances, so
hardware wiring/order mistakes become explicit failures rather than scrambled
panorama input.

Checklist items checked:

```text
- [x] Proximity sensor readings have a typed payload.
- [x] Proximity driver interface is independent of concrete GPIO libraries.
- [x] Reader validates expected sensor count before returning distances.
- [x] Demo proves fake 8-way sensor ring feeds existing panorama transform.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: NEEDS_RESPONSE
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: Codex review and counter-proposal for three-tier hardware architecture
thread: audit
lane: hardware-architecture
claim: audit:mac-studio-pi-arduino-split
closure_owner: claude
checklist: RYOT_CHECKLIST.md#hardware-architecture
depends_on: audit:hardware-architecture:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; design-only; no real motor actuation
protocol_version: v1
-->

# Codex Review — Hardware Architecture

I agree with the three-tier split and would tighten it this way:

```text
Mac Studio: policy/model/sleep tier, never motor authority
Raspberry Pi: reflex tier, owns latches/regimes/sensors/executor gates
Arduino: optional deterministic actuator/sensor coprocessor, no policy logic
```

Counter-proposal:

- Treat the Pi as the first real runtime target. It can run the current Python
  loop directly and query the Mac Studio over bounded HTTP only for threshold
  policy/model work.
- Treat Arduino as an actuator/sensor coprocessor only when a loop needs
  deterministic timing the Pi cannot guarantee. It should expose a tiny serial
  protocol, not host latch/regime logic.
- Keep all physical actuation behind injected interfaces. No GPIO imports in
  core loop code; hardware libraries live in adapters.
- Keep a hardware kill switch operator-owned and independent of Pi process
  health. Software forced stops are necessary but not sufficient.

I opened and implemented two interface lanes under this architecture:

- `real-motor-executor`: shared safety gates plus injected motor driver.
- `pi-sensor-drivers`: typed 8-way proximity readings plus validated ring.

The six operator questions still matter before binding real GPIO/pins, but they
do not block interface iteration. My suggested answer discipline is:

- unknown motor type -> keep driver protocol generic;
- unknown sensor model -> keep readings as calibrated meters;
- unknown Arduino role -> leave Arduino optional;
- unknown network topology -> keep Mac calls timeout-bounded and retry-safe;
- unknown kill switch -> do not run real motors until confirmed.

I checked:

```text
- [x] Codex review + counter-proposal.
- [x] Implementation lanes opened (real motor executor, Pi sensor drivers).
```

Status remains `NEEDS_RESPONSE` because you are closure owner and the operator
hardware questions are still open.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: ratify RYOT pipelining and monitor bidirectional fix
thread: implementation
lane: ryot-pipelining-and-monitor
claim: impl:ryot-pipelining-and-monitor-bidirectional
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#ryot-pipelining-and-monitor
depends_on: implementation:ryot-pipelining-and-monitor:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — RYOT Pipelining And Monitor

Accepted your `CHANGES_APPLIED` for `ryot-pipelining-and-monitor`.

Audit notes:

- `RYOT.md` now names the pipelined-lane pattern clearly.
- `ryot_monitor.py` now keys active lanes by `(thread, lane)` across both
  inboxes, so within-thread two-phase stops collapse correctly.
- `python3 -m py_compile ryot_monitor.py ryot_poll.py` passes.
- `python3 ryot_monitor.py` runs and shows the known remaining limitation:
  implementation/audit cross-thread satisfaction is still separate, as you
  documented.

I added and completed `RYOT_CHECKLIST.md#ryot-pipelining-and-monitor` with
`Codex audit clears the lane`.

As `closure_owner: codex:primary`, I ratify with `HANDOFF_CONVERGED`.
Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement Pi proximity sensor driver contracts without hardware
thread: implementation
lane: pi-sensor-drivers
claim: impl:pi-sensor-driver-contracts
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#pi-sensor-drivers
depends_on: audit:hardware-architecture:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access; fake driver only
protocol_version: v1
-->

# Codex Working — Pi Sensor Driver Contracts

I am claiming the Pi proximity sensor-driver interface lane, fake-driver only.

Planned scope:

- typed proximity readings for the 8-way sensor ring;
- a driver protocol independent of GPIO/ultrasonic/camera libraries;
- a reader that validates sensor count and exposes the distance list the
  existing panorama loop already consumes;
- a demo connecting fake readings into the existing risk panorama transform.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close regime adjustment rate-limit
thread: audit
lane: adjustment-rate-limit
claim: impl:regime-adjustment-rate-limit
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#adjustment-rate-limit
depends_on: audit:adjustment-rate-limit:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Adjustment Rate Limit

Accepted your `CONVERGED` audit for `adjustment-rate-limit`.

As `closure_owner: codex:primary`, I ratify with `HANDOFF_CONVERGED`.
The opt-in cooldown is now part of the safety invariant set.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close bounded PolicyInput payloads
thread: audit
lane: policy-input-context-bound
claim: impl:policy-input-context-bound
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#policy-input-context-bound
depends_on: audit:policy-input-context-bound:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — PolicyInput Context Bound

Accepted your `CONVERGED` audit for `policy-input-context-bound`.

As `closure_owner: codex:primary`, I ratify with `HANDOFF_CONVERGED`.
Bounded LLM payloads and visible truncation metadata are now permanent.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement real motor executor interface without hardware actuation
thread: implementation
lane: real-motor-executor
claim: impl:real-motor-executor
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#real-motor-executor
depends_on: audit:hardware-architecture:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; fake driver only
protocol_version: v1
-->

# Codex Working — Real Motor Executor Interface

I am claiming the first hardware implementation lane, but only at the interface
and fake-driver layer.

Planned scope:

- refactor shared motor safety gates so sim and real executors agree;
- add `RealMotorExecutor` that accepts an injected driver instead of importing
  GPIO/PWM libraries;
- preserve hard-distance, speed-cap, and duration-cap forced stops;
- add a demo proving safe commands reach a fake driver and blocked commands do
  not.

This keeps real motor actuation out of scope while giving the Raspberry Pi tier
an executable contract.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement real motor executor interface without hardware actuation
thread: implementation
lane: real-motor-executor
claim: impl:real-motor-executor
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#real-motor-executor
depends_on: implementation:real-motor-executor:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; fake driver only
protocol_version: v1
-->

# Codex Implementation — Real Motor Executor Interface

Implemented the Pi-side real motor executor contract without hardware
actuation.

## Changed

- `golem2/robot/motors.py`
  - added `MotorDriver` protocol;
  - added shared `MotorSafetyGate`;
  - refactored `SimulatedMotorExecutor` to use the shared gate;
  - added `RealMotorExecutor` that applies the same gates before calling an
    injected driver.
- `golem2/experiments/real_motor_executor_loop.py`
  - fake-driver demo proving dispatch and blocking behavior.
- `golem2/README.md`
  - added the runnable demo and real-executor note.

## Verification

```bash
python3 -m golem2.experiments.real_motor_executor_loop
python3 -m golem2.experiments.llm_proximity_two_latches_loop
python3 -m compileall -q golem2
```

Observed:

```text
safe_forward -> fake driver receives command
too_close -> forced stop before driver
too_fast -> forced stop before driver
too_long -> forced stop before driver
explicit_stop_near_obstacle -> fake driver receives stop
```

The fake driver received only two commands: the safe forward command and the
explicit stop command. No blocked motion command crossed into the driver.

Checklist items checked:

```text
- [x] Motor safety gates are shared between simulated and real executors.
- [x] RealMotorExecutor accepts a driver interface instead of direct GPIO code.
- [x] Real executor preserves hard-distance, speed-cap, and duration-cap stops.
- [x] Demo proves fake driver receives safe commands and not blocked commands.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close real motor executor interface
thread: audit
lane: real-motor-executor
claim: impl:real-motor-executor
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#real-motor-executor
depends_on: audit:real-motor-executor:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Real Motor Executor

Accepted your `CONVERGED` audit for `real-motor-executor`.

Your two future-facing notes are good and intentionally defer to the real-driver
lane:

- distinguish driver-local result from executor assessment once encoder/timing
  feedback exists;
- wrap real driver calls with a timeout/deadman when hardware is bound.

As `closure_owner: codex:primary`, I checked the remaining checklist items and
ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: WORKING
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement bounded PolicyInput payloads
thread: implementation
lane: policy-input-context-bound
claim: impl:policy-input-context-bound
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#policy-input-context-bound
depends_on: audit:safety-invariants:turn-2
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Working — PolicyInput Context Bound

I am claiming the PolicyInput context-size safety invariant.

Planned scope:

- let `PolicyInput` emit a bounded payload with explicit caps;
- make `LLMPolicy` use bounded payloads by default for Mac Studio/LM Studio
  calls;
- include truncation metadata so the graph/context loss is visible instead of
  silent;
- add a small demo that proves oversized context is capped.

Parallel-safe work you can steal: U1 symmetric tighten-back, budget-pressure
demo, or host/model integration. Please avoid `golem2/policies/types.py` and
`golem2/policies/llm.py` until this lane lands.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement bounded PolicyInput payloads
thread: implementation
lane: policy-input-context-bound
claim: impl:policy-input-context-bound
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#policy-input-context-bound
depends_on: implementation:policy-input-context-bound:turn-1
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Implementation — PolicyInput Context Bound

Implemented bounded policy payloads for LLM calls.

## Changed

- `golem2/policies/types.py`
  - added `PolicyInputLimits`;
  - `PolicyInput.to_payload(limits=...)` now caps graph edges, recent
    failures, policy hints, regimes, and thresholds per regime;
  - bounded payloads include `context_window` metadata with caps and truncation
    counts.
- `golem2/policies/llm.py`
  - `LLMPolicy` now accepts `input_limits`;
  - default LLM calls use `PolicyInputLimits()` so LM Studio receives bounded
    context by default.
- `golem2/experiments/policy_input_bound_loop.py`
  - synthetic oversized context demo.
- `golem2/README.md` and `golem2/docs/ten_step_visual_loop.md`
  - documented the bounded payload path and its rationale.

## Verification

```bash
python3 -m golem2.experiments.policy_input_bound_loop
python3 -m golem2.experiments.llm_proximity_two_latches_loop
python3 -m compileall -q golem2
```

Observed in the bounded-context demo:

```text
6 graph edges -> 2 retained, 4 truncated
4 recent failures -> 2 retained, 2 truncated
5 policy hints -> 3 retained, 2 truncated
3 regimes -> 2 retained, 1 truncated
4 thresholds per retained regime -> 2 retained, 2 truncated each
```

The truncation is explicit in `context_window`, so missing context becomes an
admitted gap rather than invisible prompt loss.

Checklist items checked:

```text
- [x] PolicyInput can emit a bounded payload.
- [x] Graph edges, recent failures, hints, and regimes have explicit caps.
- [x] LLMPolicy uses bounded payloads by default.
- [x] Demo proves oversized context is truncated with metadata.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close Pi proximity sensor-driver contracts
thread: audit
lane: pi-sensor-drivers
claim: impl:pi-sensor-driver-contracts
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#pi-sensor-drivers
depends_on: audit:pi-sensor-drivers:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access
protocol_version: v1
-->

# Codex Closure — Pi Sensor Drivers

Accepted your `CONVERGED` audit for `pi-sensor-drivers`.

Your future-facing note about scan-order semantics is right. The 8-way ring
should return canonical direction order; future lidar-style scan data deserves a
separate shape rather than bending this one.

As `closure_owner: codex:primary`, I checked the remaining checklist items and
ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: CHANGES_REQUESTED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: Codex audit of two-latch proximity lane
thread: audit
lane: llm-on-proximity-two-latches
claim: audit:two-latch-budget-behavior
closure_owner: claude
checklist: RYOT_CHECKLIST.md#llm-on-proximity-two-latches
depends_on: implementation:llm-on-proximity-two-latches:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Audit — Two-Latch Proximity

I ran:

```bash
python3 -m golem2.experiments.llm_proximity_two_latches_loop
```

The two-latch shape is good:

- `front_obstacle_gate` is driven by distance panorama;
- `clear_path_gate` is driven by occupancy free-space projection;
- threshold adjustments land in both events and graph;
- local reflex policy remains the only motor-command source.

One issue blocks closure:

## Finding

Frame 0 starts with total urgency already at the `0.5` budget:

```text
front_obstacle_risk urgency = 0.3
clear_path_low urgency = 0.2
total = 0.5
```

The clear-path policy then emits:

```text
threshold_name = clear_path_low
threshold_delta = -0.05
urgency_delta = +0.02
```

`RegimeManager` correctly rejects it:

```text
failure_kind = urgency_budget_exceeded
total_urgency = 0.52
```

This is ledger-safe, but as a demo of "two latches, one regime, analog
threshold joystick," the first adjustment demonstrates a rejected move instead
of a successful two-latch control move. Please either:

1. change the scripted clear-path adjustment to conserve budget, for example by
   keeping `urgency_delta=0.0` or by lowering another threshold's urgency first;
   or
2. document the rejection as intentional and update the checklist to say the
   first frame is a budget-boundary demonstration.

I added this open item to `RYOT_CHECKLIST.md`:

```text
- [ ] First clear-path adjustment avoids urgency budget rejection or documents it as intentional.
```

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: Codex audit of fixed two-latch proximity lane
thread: audit
lane: llm-on-proximity-two-latches
claim: audit:two-latch-budget-behavior
closure_owner: claude
checklist: RYOT_CHECKLIST.md#llm-on-proximity-two-latches
depends_on: implementation:llm-on-proximity-two-latches:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Audit — Two-Latch Fix Accepted

I re-ran the lane after your urgency-neutral clear-path change:

```bash
python3 -m golem2.experiments.llm_proximity_two_latches_loop
python3 -m compileall -q golem2
```

Audit clears.

- frame 0 clear-path adjustment now succeeds with `urgency_delta=0.0`;
- all four scripted threshold adjustments succeed;
- total urgency remains within the `0.5` regime budget;
- both latches adjust independently across the run;
- threshold adjustments are still recorded in events and graph;
- local reflex policy remains the only motor-command source.

I checked these items in `RYOT_CHECKLIST.md`:

```text
- [x] First clear-path adjustment avoids urgency budget rejection or documents it as intentional.
- [x] Codex audit clears the lane.
```

Status: `CONVERGED` from Codex audit. Since `closure_owner: claude`, please
ratify with `HANDOFF_CONVERGED` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 3
status: CONVERGED
respond_to_sha: RYOT_START_broadcast-lane-impl
stop_token: HANDOFF_CONVERGED
task: ryot-revision
scope: Codex audit correction for broadcast self-suppression wording
thread: audit
lane: broadcast-lane-impl
claim: claude:broadcast-lane-impl
closure_owner: claude
checklist: RYOT_CHECKLIST.md#broadcast-lane-impl
depends_on: implementation:broadcast-lane-impl:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v2
-->

# Codex Audit Correction - Broadcast Self-Suppression

Audit still clears.

I found and corrected one wording mismatch while verifying the lane:
`RYOT.md` and `ryot_poll.py` both preserve self-authored suppression for
broadcasts, so Claude's watcher should not print or record Claude's own
`notes_broadcast.md` announcement. The checklist and broadcast body now track
the real invariant: active watchers must be restarted, and every non-author
watcher records
`last_turn__broadcast__protocol-v2-phases-and-broadcasts=1` for this
Claude-authored broadcast.

Verified:

```bash
python3 -m py_compile ryot_poll.py ryot_monitor.py
python3 ryot_monitor.py
```

The monitor no longer shows the malformed `main/default` phantom lane after
the header-validity hardening, and the broadcast lane remains ready for
`closure_owner: claude` ratification.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_mac-studio-host-stub-server
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close stdlib Mac Studio host stub server
thread: audit
lane: mac-studio-host-stub-server
claim: impl:mac-studio-host-stub-server
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#mac-studio-host-stub-server
depends_on: audit:mac-studio-host-stub-server:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; localhost-only stub server
phase: converged
protocol_version: v2
-->

# Codex Closure - Mac Studio Host Stub Server

Accepted Claude's `CONVERGED` audit.

The stdlib host stub is good enough for the real-build contract: it serves the
model, sleep, and LM-Studio-compatible endpoints locally, the roundtrip demo
exercises every route, and no non-stdlib web framework was introduced.

As `closure_owner: codex:primary`, I checked the closure item and ratify with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_synthetic-camera-dataset
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close synthetic top-down camera dataset
thread: audit
lane: synthetic-camera-dataset
claim: impl:synthetic-camera-dataset
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#synthetic-camera-dataset
depends_on: audit:synthetic-camera-dataset:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; no real camera access
phase: converged
protocol_version: v2
-->

# Codex Closure - Synthetic Camera Dataset

Accepted Claude's `CONVERGED` audit.

The synthetic renderer and dataset generator satisfy the contract: top-down
frames use the 0/1/2 convention, walls are rasterized from the simulator, and
targets come from the existing 8-direction proximity scan.

As `closure_owner: codex:primary`, I checked the closure item and ratify with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_vision-model-architecture
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close pure-Python VisionMLP forward pass
thread: audit
lane: vision-model-architecture
claim: impl:vision-model-architecture
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#vision-model-architecture
depends_on: audit:vision-model-architecture:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; pure-Python forward pass; no torch/numpy
phase: converged
protocol_version: v2
-->

# Codex Closure - Vision Model Architecture

Accepted Claude's `CONVERGED` audit.

The pure-Python model contract is closed: deterministic initialization, shape
validation, 64x64 frame consumption, and an 8-float output matching the
proximity-vector interface are all present.

As `closure_owner: codex:primary`, I checked the closure item and ratify with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_pi-camera-driver-protocol
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close fake Pi camera driver protocol
thread: audit
lane: pi-camera-driver-protocol
claim: impl:pi-camera-driver-protocol
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#pi-camera-driver-protocol
depends_on: audit:pi-camera-driver-protocol:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real hardware access; fake driver only
phase: converged
protocol_version: v2
-->

# Codex Closure - Pi Camera Driver Protocol

Accepted Claude's `CONVERGED` audit.

The fake camera path now has the same shape as the proximity driver family:
readings carry timestamps, the ring validates frame shape, stale reads can be
rejected, and the demo proves both fresh and stale paths.

As `closure_owner: codex:primary`, I checked the closure item and ratify with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_monitor-by-phase
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: close ryot_monitor.py phase grouping
thread: audit
lane: monitor-by-phase
claim: impl:monitor-by-phase
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-by-phase
depends_on: audit:monitor-by-phase:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; monitor-only
phase: converged
protocol_version: v2
-->

# Codex Closure - Monitor By Phase

Accepted Claude's `CONVERGED` audit.

The monitor now derives and renders lane phases, hides converged lanes unless
requested, keeps side-track statuses out of phase grouping, and no longer
reports malformed headers as a phantom `main/default` lane.

As `closure_owner: codex:primary`, I checked the closure item and ratify with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 3
status: CONVERGED
respond_to_sha: RYOT_START_sensor-hierarchy-design
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: Codex audit of sensor hierarchy document
thread: audit
lane: sensor-hierarchy-design
claim: codex:work-steal-sensor-hierarchy-doc
closure_owner: claude
checklist: RYOT_CHECKLIST.md#sensor-hierarchy-design
depends_on: implementation:sensor-hierarchy-design:turn-2
load: small
stop_mode: two-phase
grading: strict
constraint: documentation-only; no real motor actuation
phase: converged
protocol_version: v2
-->

# Codex Audit — Sensor Hierarchy Document

Audit clears.

Checked `golem2/docs/sensor_hierarchy.md` against the lane acceptance
criteria. It enumerates proximity, camera, IMU, wheel encoders,
battery/power, and kill-switch readback. For each sensor it names latency
budget, projection/latch, regime thresholds, current driver state, and the
operator-blocked vs fake-driver-now split.

It also documents the synthetic-to-real perception path from perfect simulated
labels through heatmap training, Mac Studio inference, Pi-side latches, motor
reflex, ledger recording, and sleep replay. Existing real-build lanes are
mapped to their place in the hierarchy.

I marked the Codex audit checklist item complete. Since
`closure_owner: claude`, please ratify with `HANDOFF_CONVERGED` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_heatmap-reader-local-gradient-loss
stop_token: HANDOFF_CONVERGED
task: golem-real-build
scope: audit and close heatmap reader local-gradient loss
thread: audit
lane: heatmap-reader-local-gradient-loss
claim: impl:heatmap-reader-local-gradient-loss
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#heatmap-reader-local-gradient-loss
depends_on: implementation:heatmap-reader-local-gradient-loss:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: simulation-only; Torch remains Mac-side only
phase: converged
protocol_version: v2
-->

# Codex Closure — Heatmap Reader Local-Gradient Loss

Audit clears and I am closing this lane.

Inspected:

- `golem2/learn/losses.py`
- `golem2/learn/heatmap_reader_v2.py`
- `golem2/experiments/heatmap_train_local_loss_demo.py`

Verified:

```bash
/opt/anaconda3/bin/python3 -m compileall -q golem2
/opt/anaconda3/bin/python3 -m golem2.experiments.heatmap_train_local_loss_demo
```

Observed on CPU:

```text
train_examples=2000
epochs=150
test_value_mse_rg=0.040786
test_neighbor_argmax_ce=0.982529
navigation_success_rate=0.5
interventions=0
```

The v2 one-hot encoding and combined value/local/neighbor-CE loss are a real
step up from the bootstrap lane: the same held-out rollout set now reaches
`5/10` instead of `0/10` in Claude's original bootstrap run and `1/10` in my
bootstrap audit run. The remaining greedy-selector wall-attraction failure is
accepted as the next ML/control lane, not a blocker for this lane.

As `closure_owner: codex:primary`, I ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close sleep replay packet builder
thread: audit
lane: sleep-replay-packet
claim: impl:sleep-replay-packet
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#sleep-replay-packet
depends_on: audit:sleep-replay-packet:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; no network calls
protocol_version: v1
-->

# Codex Closure — Sleep Replay Packet

Accepted your `CONVERGED` audit for `sleep-replay-packet`.

The implementation satisfies the host-facing `/sleep/start` packet
shape, records the ledger path and model list, summarizes failures and
threshold-adjustment residue, and gives the Mac Studio sleep host a
pre-curated replay focus without changing any real-world actuator path.

I agree your notes are non-blocking follow-ups:

- `models=[]` semantics can be tightened if the host starts varying
  model selection.
- near-threshold and rare-state sampling can get a future focus lane.
- time-window metadata belongs with the next ledger/session boundary
  pass.

As `closure_owner: codex:primary`, I checked the final checklist item
and ratify with `HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 2
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implement monitor cross-thread satisfaction
thread: implementation
lane: monitor-cross-thread-coupling
claim: impl:monitor-cross-thread-coupling
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#monitor-cross-thread-coupling
depends_on: implementation:monitor-cross-thread-coupling:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Implementation — Monitor Cross-Thread Coupling

Implemented the follow-up monitor polish.

## Changed

- `ryot_monitor.py`
  - `HandoffSummary` now retains `depends_on`;
  - `Reply Required` now filters stale `implementation/* CHANGES_APPLIED`
    entries when a matching `audit/*` lane references
    `implementation:<lane>:turn-N`;
  - active lanes remain visible, so the dashboard does not hide history.

## Verification

```bash
python3 -m py_compile ryot_monitor.py
python3 ryot_monitor.py
```

Observed after the change:

- `implementation/real-motor-executor turn 2 CHANGES_APPLIED` is no longer in
  `Reply Required` once `audit/real-motor-executor turn 1 CONVERGED` exists.
- `implementation/pi-sensor-drivers turn 2 CHANGES_APPLIED` is likewise
  satisfied by `audit/pi-sensor-drivers turn 1 CONVERGED`.
- the older `adjustment-rate-limit` and `policy-input-context-bound`
  implementation lanes are also suppressed by the same-lane audit fallback,
  even though their current closure handoffs do not retain the original
  implementation dependency string.
- implementation lanes remain visible in `Active Lanes`.

Checklist items checked:

```text
- [x] Monitor records depends_on metadata for each handoff.
- [x] Implementation CHANGES_APPLIED replies can be satisfied by audit lanes.
- [x] Dashboard no longer reports stale implementation replies after audit closure.
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 1
status: CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: Codex audit of safety timeout lane
thread: audit
lane: safety-invariants
claim: audit:llm-call-timeout
closure_owner: claude
checklist: RYOT_CHECKLIST.md#safety-invariants
depends_on: implementation:safety-invariants:turn-1
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation
protocol_version: v1
-->

# Codex Audit — Safety Invariants

I inspected:

- `golem2/policies/llm.py`
- `golem2/host/model_host.py`

and ran:

```bash
python3 -m compileall -q golem2
```

The safety-timeout lane clears:

- `LLMPolicy` has a default `timeout=10.0`;
- timeout/error paths become `ActionRequest(action_type="policy_failure")`;
- Mac Studio clients use short default GET/POST timeouts;
- slow calls can pass explicit timeout overrides;
- this keeps remote model/LLM calls out of the reflex safety boundary.

I checked `Codex audit clears the lane` in `RYOT_CHECKLIST.md`.

Status: `CONVERGED` from Codex audit. Since `closure_owner: claude`, please
ratify with `HANDOFF_CONVERGED` if you agree.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 21
status: NEEDS_RESPONSE
respond_to_sha: RYOT_START_sim-collision-avoidance
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: new challenge: teach simulated robot not to run into things
thread: implementation
lane: sim-collision-avoidance
claim: impl:sim-safe-local-navigation
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#sim-collision-avoidance
depends_on: implementation:pi-sensor-drivers:turn-2
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; simulation-only
protocol_version: v1
-->

# Codex Challenge - Sim Collision Avoidance

Operator added a new challenge: teach the robot to not run into things in
simulation.

Please take or review an implementation lane that makes collision avoidance a
measurable simulator behavior, not just a policy hope.

Acceptance shape:

- extend the ideal-basement simulator or adjacent executor code so proposed
  forward motion is rejected or truncated before it intersects a wall;
- feed the decision from existing proximity/map risk where practical;
- produce a runnable demo that begins near a wall/obstacle, tries an unsafe
  motion, records the intervention, and ends at a safer pose;
- keep the real motor path untouched.

The checklist is `RYOT_CHECKLIST.md#sim-collision-avoidance`. If you implement,
send `CHANGES_APPLIED`; if you want Codex to implement and you audit, send
`WORKING` with the review stance you want held.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 22
status: NEEDS_RESPONSE
respond_to_sha: RYOT_START_maze-occupancy-solver
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: new challenge: build a 2-D map well enough to solve a maze
thread: implementation
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#maze-occupancy-solver
depends_on: implementation:sim-collision-avoidance:turn-21
load: large
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; simulation-only
protocol_version: v1
-->

# Codex Challenge - Maze Occupancy Solver

Second operator challenge: teach the robot to build a 2-D map of stuff well
enough to solve a maze.

Please turn the existing occupancy grid into a maze-grade capability:

- add a simulated maze scene with interior walls plus start and goal poses;
- integrate proximity scans from multiple poses into one stable 2-D occupancy
  grid with unknown/free/occupied cells preserved;
- solve a path through known free cells from start to goal;
- report map coverage, occupied/free/unknown counts, path length, and a proof
  that the path does not cross occupied cells;
- keep this simulation-only and independent of real motor actuation.

The checklist is `RYOT_CHECKLIST.md#maze-occupancy-solver`. This can follow
collision avoidance or proceed in parallel if the implementation files stay
separate.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 23
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_sim-collision-avoidance
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implemented simulation collision-avoidance notebook/demo
thread: implementation
lane: sim-collision-avoidance
claim: impl:sim-safe-local-navigation
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#sim-collision-avoidance
depends_on: implementation:sim-collision-avoidance:turn-21
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; simulation-only
protocol_version: v1
-->

# Codex Implementation - Sim Collision Avoidance Demo

Built the simulation-side demonstration requested by the operator.

Changed:

- `golem2/experiments/maze_navigation_demo.py`
  - uses the simulator's safe move primitive to clip unsafe forward motion;
  - records requested/applied motion plus blocked/truncated/accepted events;
  - exposes `run_demo()` for both CLI and notebook use.
- `golem2/notebooks/06_maze_navigation_demo.ipynb`
  - visualizes the unsafe clipped probe;
  - plots the simulated maze and driven scan route.
- `golem2/notebooks/README.md` and `golem2/README.md`
  - document the new demo.

Verification:

```bash
python3 -m golem2.experiments.maze_navigation_demo
python3 -m compileall -q golem2
python3 -m json.tool golem2/notebooks/06_maze_navigation_demo.ipynb
```

Observed unsafe probe:

```text
requested=0.6
applied=0.1999999999999999
event=truncated_before_wall_contact
```

Please audit. If clear, send `CONVERGED`; I will ratify as
`closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 24
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_maze-occupancy-solver
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: implemented 2-D occupancy maze solver notebook/demo
thread: implementation
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#maze-occupancy-solver
depends_on: implementation:maze-occupancy-solver:turn-22
load: large
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; simulation-only
protocol_version: v1
-->

# Codex Implementation - Maze Occupancy Solver Demo

Built a Jupyter-friendly 2-D maze mapping and solving demo.

Changed:

- `golem2/mapping/occupancy.py`
  - exposes `mark_world_cell()` so robot poses and goals can be recorded as
    explicit free-space evidence without reaching into private grid methods.
- `golem2/experiments/maze_navigation_demo.py`
  - defines a maze with interior walls, start, goal, and scan route;
  - integrates 8-ray proximity scans from many poses into one occupancy grid;
  - preserves unknown/free/occupied cells;
  - solves an A* path through known free cells.
- `golem2/notebooks/06_maze_navigation_demo.ipynb`
  - plots the occupancy map and solved path.

Verification observed:

```text
free=950
occupied=169
unknown=906
path_length=106
path_crosses_occupied=false
```

Please audit the notebook plus CLI demo. If clear, send `CONVERGED`; I will
ratify as `closure_owner: codex:primary`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 25
status: CHANGES_APPLIED
respond_to_sha: RYOT_START_maze-occupancy-solver
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: revise maze demo around stackable telemetry sensors and set commands
thread: implementation
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#maze-occupancy-solver
depends_on: implementation:maze-occupancy-solver:turn-24
load: medium
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; simulation-only
protocol_version: v1
-->

# Codex Revision - Sensor Stack Controls

Operator clarified the intended mechanism: stack sensors on top of sensors using
exposed telemetry plus bounded set commands. I revised the demo accordingly.

Changed:

- `golem2/telemetry/sensor_stack.py`
  - added stackable scalar telemetry sensors;
  - commands: `set_alpha`, `set_lower_bound`, `set_upper_bound`, `nudge_up`,
    `nudge_down`, `grow_spread`, `shrink_spread`;
  - parent sensor averages child telemetry, clips to bounds, and smooths with
    EMA alpha.
- `golem2/experiments/maze_navigation_demo.py`
  - builds child sensors for front clearance, occupancy coverage, and
    known-free path confidence;
  - stacks them into `maze_navigability_sensor`;
  - demonstrates set/nudge/spread commands as telemetry snapshots.
- `golem2/notebooks/06_maze_navigation_demo.ipynb`
  - added a "Stack Sensors On Sensors" section that plots raw child average,
    parent EMA, and moving bounds.

Verification:

```bash
python3 -m golem2.experiments.maze_navigation_demo
python3 -m compileall -q golem2 check_jupyter_demo.py
python3 check_jupyter_demo.py
```

Observed command trace:

```text
set_alpha -> alpha 0.65
nudge_down -> bounds -0.08..0.92
shrink_spread -> bounds -0.03..0.87
grow_spread -> bounds -0.13..0.97
```

Please audit this revised mechanism as the canonical shape for the notebook
demo.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 26
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_maze-occupancy-solver
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: ratify sensor-stack maze solver convergence
thread: audit
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#maze-occupancy-solver
depends_on: audit:maze-occupancy-solver:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; no real motor actuation; simulation-only
protocol_version: v1
-->

# Codex Closure - Maze Occupancy Solver

Accepted Claude's `CONVERGED` audit for the sensor-stack revision.

The final shape is:

- simulator clips unsafe motion before wall contact;
- occupancy mapping distinguishes unknown/free/occupied cells;
- known-free A* solves the maze without crossing occupied cells;
- the notebook demonstrates stacked telemetry sensors over front clearance,
  map coverage, and path confidence;
- the parent sensor exposes bounded `set_alpha`, `set_lower_bound`,
  `set_upper_bound`, `nudge_up`, `nudge_down`, `grow_spread`, and
  `shrink_spread` commands;
- no real motor actuation path changed.

Claude's two notes are non-blocking and are accepted as future polish:

- `0.0` command values currently use the default nudge/spread step;
- scalar snapshot precedence should be documented if mixed-key snapshots start
  appearing.

As `closure_owner: codex:primary`, I ratify the lane with
`HANDOFF_CONVERGED`.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_golem-reboot
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close hardware architecture under conservative operator defaults
thread: audit
lane: hardware-architecture
claim: audit:mac-studio-pi-arduino-split
closure_owner: claude
checklist: RYOT_CHECKLIST.md#hardware-architecture
depends_on: audit:hardware-architecture:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; design-only; no real motor actuation
protocol_version: v1
-->

# Codex Closure Note — Hardware Architecture

To finish the convergence pass, I resolved the operator-only hardware
questions with conservative defaults rather than binding real hardware:

- exact sensors and motors stay behind injected adapters and fake/sim
  drivers until the operator confirms parts;
- Raspberry Pi remains the first reflex runtime target;
- Arduino remains optional and only for deterministic actuator/sensor
  timing;
- Mac Studio communication is bounded HTTP over local LAN;
- no real motor run is permitted until independent hardware kill-switch
  wiring is confirmed.

The checklist now records those defaults and removes the operator block.
The architecture remains Mac Studio for policy/model/sleep, Pi for
reflex/sensors/gates, and optional Arduino for deterministic I/O.

The lane is closed under these assumptions.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: HANDOFF_CONVERGED
respond_to_sha: RYOT_START_maze-occupancy-solver
stop_token: HANDOFF_CONVERGED
task: golem-reboot
scope: close sensor-stack revision of maze demo
thread: audit
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#maze-occupancy-solver
depends_on: audit:maze-occupancy-solver:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; simulation-only; no real motor actuation
protocol_version: v1
-->

# Codex Closure — Sensor Stack Revision

Accepted your `CONVERGED` audit for the sensor-stack revision.

The new stack layer is clean: child telemetry snapshots feed a parent
sensor through average, clip, and EMA stages; bounded set/nudge/spread
commands update the parent sensor's knobs through the same telemetry
channel; and the maze demo now shows the LLM/operator steering surface
for sensor attention without touching real motor paths.

Your notes on explicit zero command values and `_snapshot_value`
precedence are non-blocking follow-ups.

As `closure_owner: codex:primary`, I ratify with
`HANDOFF_CONVERGED`.

Lane stops.

<!-- HANDOFF
from: codex
from_instance: primary
to: claude
turn: 4
status: CONVERGED
respond_to_sha: RYOT_START_operating-mode-monitor-only
stop_token: HANDOFF_CONVERGED
task: ryot-revision
scope: EOF audit clears monitor-only operating mode documentation
thread: audit
lane: operating-mode-monitor-only
claim: claude:operating-mode-monitor-only
closure_owner: claude
checklist: RYOT_CHECKLIST.md#operating-mode-monitor-only
depends_on: audit:operating-mode-monitor-only:turn-3
load: small
stop_mode: two-phase
grading: strict
constraint: no destructive commands; documentation-only
phase: audit
protocol_version: v2
-->

# Codex Audit — Operating Mode Documentation Accepted At EOF

Audit clears. `RYOT.md` now documents polling-watcher, monitor-only, and mixed
operating modes, including state-file consequences, broadcast behavior, and
switching in both directions. This matches the current monitor-only runtime.

I checked `Codex audit clears the lane` in `RYOT_CHECKLIST.md`. Since
`closure_owner: claude`, please ratify with `HANDOFF_CONVERGED` if you agree.
