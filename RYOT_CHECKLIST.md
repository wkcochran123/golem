# RYOT Checklist

This file is the visible ownership ledger for active RYOT work. A checklist can
be recursive: parent items close only after child checklist owners converge.

## llm-on-proximity

```text
closure_owner: codex:primary
thread: implementation
lane: llm-on-proximity
claim: impl:llm-on-proximity-with-regime
```

- [x] Offline LM-Studio-shaped policy emits `adjust_threshold`.
- [x] `RegimeManager.execute()` applies the threshold action.
- [x] Bound obstacle latch receives updated threshold.
- [x] Bound obstacle latch receives updated urgency.
- [x] Next proximity frame uses updated threshold/urgency.
- [x] Event log records threshold adjustments.
- [x] Graph records threshold adjustment facts.
- [x] Local reflex policy remains the only motor-command source.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## m1-occupancy-bridge

```text
closure_owner: codex:primary
thread: audit
lane: m1-occupancy-bridge
claim: impl:m1-closure
```

- [x] Architecture proposal selected `OccupancyGrid.to_projection_map()`.
- [x] `ProjectionKind` includes `occupancy`.
- [x] Occupancy ledger exposes occupied and free projection modes.
- [x] `map_latch_loop` demonstrates occupancy projections through latches.
- [x] Claude sent `CONVERGED`.
- [x] Codex sent `HANDOFF_CONVERGED`.

## ryot-threading

```text
closure_owner: codex:primary
thread: implementation
lane: ryot-and-regimes
claim: threaded-ryot-regime-bindings
```

- [x] Watcher scans multiple handoff blocks.
- [x] State is tracked per `(thread, lane)`.
- [x] Instance routing supports same-name agents.
- [x] RYOT docs explain claim convention and dependency metadata.
- [x] RYOT docs explain watcher script cache failure mode.
- [x] RYOT docs explain checklist ownership and recursive closure.
- [x] Claude audit clears checklist-owner protocol.
- [x] RYOT docs clarify checklist file is canonical over headers.
- [x] RYOT docs clarify any agent may check owned checklist items.
- [x] RYOT docs clarify audit-lane closure role inversion.
- [x] RYOT docs clarify `WORKING` enables work stealing in other lanes.
- [x] RYOT docs clarify monitor/checklist iteration loop.

## ryot-pipelining-and-monitor

```text
closure_owner: codex:primary
thread: implementation
lane: ryot-pipelining-and-monitor
claim: impl:ryot-pipelining-and-monitor-bidirectional
```

- [x] RYOT.md Pipelined Lanes section explains the staggered pattern.
- [x] `ryot_monitor.py` keys by `(thread, lane)` across both inboxes.
- [x] Within-thread two-phase stops correctly collapse to closed.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## monitor-cross-thread-coupling

```text
closure_owner: codex:primary
thread: implementation
lane: monitor-cross-thread-coupling
claim: impl:monitor-cross-thread-coupling
```

- [x] Monitor records `depends_on` metadata for each handoff.
- [x] Implementation `CHANGES_APPLIED` replies can be satisfied by audit lanes.
- [x] Dashboard no longer reports stale implementation replies after audit closure.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## monitor-state-aware-suppression

```text
closure_owner: codex:primary
thread: implementation
lane: monitor-state-aware-suppression
claim: impl:monitor-state-aware-suppression
```

- [x] Monitor accepts watcher state-file paths.
- [x] Monitor reads per-lane consumed turns from state files.
- [x] Reply Required suppresses visible stale turns consumed by a watcher.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## urgency-budget-pressure-demo

```text
closure_owner: codex:primary
thread: implementation
lane: urgency-budget-pressure-demo
claim: impl:urgency-budget-pressure-demo
```

- [x] Demo intentionally attempts to exceed the `0.5` urgency budget.
- [x] Rejected adjustment leaves thresholds unchanged.
- [x] Event log records `urgency_budget_exceeded`.
- [x] Graph exposes `lower_other_urgency_first` affordance.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## sleep-replay-packet

```text
closure_owner: codex:primary
thread: implementation
lane: sleep-replay-packet
claim: impl:sleep-replay-packet
```

- [x] Sleep replay packet includes ledger path and model list.
- [x] Sampling summary counts failures and threshold-adjustment residue.
- [x] Demo builds a packet from a generated event ledger.
- [x] Packet shape matches the Mac Studio host contract.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## proximity-freshness-gate

```text
closure_owner: codex:primary
thread: implementation
lane: proximity-freshness-gate
claim: impl:proximity-freshness-gate
```

- [x] Proximity readings carry capture timestamps.
- [x] Proximity ring can reject stale readings when a max age is configured.
- [x] Freshness gate is opt-in and preserves existing fake-driver demos.
- [x] Demo proves fresh readings pass and stale readings fail.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## u1-symmetric-tighten-back

```text
closure_owner: codex:primary
thread: implementation
lane: u1-symmetric-tighten-back
claim: impl:u1-symmetric-tighten-back
```

- [x] Recovering policy wraps two-latch policy without modifying it.
- [x] Negative exceptions reset recovery counter; positive ones do not.
- [x] Pure silent ticks past horizon emit revert adjustment.
- [x] Revert is bounded by `min_threshold` via `RegimeManager` clamp.
- [x] Demo shows threshold tighten-back after sustained silence.
- [x] Back-compat: existing two-latch demo unaffected.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## llm-on-proximity-two-latches

```text
closure_owner: claude
thread: implementation
lane: llm-on-proximity-two-latches
claim: impl:two-latch-threshold-joystick
```

- [x] Two-latch demo runs.
- [x] Obstacle latch is driven by distance panorama.
- [x] Clear-path latch is driven by occupancy free-space projection.
- [x] Threshold adjustments are recorded in events and graph.
- [x] First clear-path adjustment avoids urgency budget rejection or documents it as intentional.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## safety-invariants

```text
closure_owner: claude
thread: implementation
lane: safety-invariants
claim: impl:llm-call-timeout
```

- [x] `LLMPolicy` exposes a caller-configurable timeout.
- [x] `LLMPolicy` maps timeout/error paths to `policy_failure`.
- [x] Mac Studio host clients use real-time-friendly default timeouts.
- [x] Slow calls can pass explicit timeout overrides.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## adjustment-rate-limit

```text
closure_owner: codex:primary
thread: implementation
lane: adjustment-rate-limit
claim: impl:regime-adjustment-rate-limit
```

- [x] `RegimeManager` can enforce an opt-in adjustment cooldown.
- [x] Rate-limited adjustments are rejected before mutating thresholds.
- [x] Rate-limit failures are recorded in events and graph.
- [x] Demo shows first adjustment ok, immediate repeat rejected, later retry ok.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## policy-input-context-bound

```text
closure_owner: codex:primary
thread: implementation
lane: policy-input-context-bound
claim: impl:policy-input-context-bound
```

- [x] `PolicyInput` can emit a bounded payload.
- [x] Graph edges, recent failures, hints, and regimes have explicit caps.
- [x] `LLMPolicy` uses bounded payloads by default.
- [x] Demo proves oversized context is truncated with metadata.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## real-motor-executor

```text
closure_owner: codex:primary
thread: implementation
lane: real-motor-executor
claim: impl:real-motor-executor
```

- [x] Motor safety gates are shared between simulated and real executors.
- [x] `RealMotorExecutor` accepts a driver interface instead of direct GPIO code.
- [x] Real executor preserves hard-distance, speed-cap, and duration-cap stops.
- [x] Demo proves fake driver receives safe commands and not blocked commands.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## pi-sensor-drivers

```text
closure_owner: codex:primary
thread: implementation
lane: pi-sensor-drivers
claim: impl:pi-sensor-driver-contracts
```

- [x] Proximity sensor readings have a typed payload.
- [x] Proximity driver interface is independent of concrete GPIO libraries.
- [x] Reader validates expected sensor count before returning distances.
- [x] Demo proves fake 8-way sensor ring feeds existing panorama transform.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## sim-collision-avoidance

```text
closure_owner: codex:primary
thread: implementation
lane: sim-collision-avoidance
claim: impl:sim-safe-local-navigation
```

- [x] Simulator can reject or truncate a forward move that would intersect a wall.
- [x] Policy/executor loop uses proximity/map risk before applying simulated motion.
- [x] Demo starts near an obstacle and reaches a safer pose without wall contact.
- [x] Event log records blocked, truncated, or recovery moves.
- [x] No real motor actuation path changes.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## maze-occupancy-solver

```text
closure_owner: codex:primary
thread: implementation
lane: maze-occupancy-solver
claim: impl:occupancy-map-maze-solver
```

- [x] Simulator includes a 2-D maze scene with interior walls and start/goal poses.
- [x] Occupancy mapping integrates multiple poses into one stable 2-D grid.
- [x] Unknown, free, and occupied cells are distinct in the exported map.
- [x] Solver finds a path through known free cells from start to goal.
- [x] Demo proves the path avoids occupied cells and reports coverage/path metrics.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## hardware-architecture

```text
closure_owner: claude
thread: audit
lane: hardware-architecture
claim: audit:mac-studio-pi-arduino-split
```

- [x] Three-tier split named (Mac Studio / Raspberry Pi / Arduino).
- [x] Tier boundary protocols sketched (HTTP up, serial/GPIO down).
- [x] Safety-gate-by-tier proposed (timeouts on host, gates on Pi, hardware kill on Arduino).
- [x] Code shape proposed (`RealMotorExecutor`, `golem2/sensors/`, optional `golem2/hardware/arduino_link.py`).
- [x] Operator hardware-context questions resolved with conservative defaults (see Operator Blocked Queue).
- [x] Codex review + counter-proposal.
- [x] Implementation lanes opened (real motor executor, Pi sensor drivers).
- [x] Claude audit closure.

## real-build-kickoff

```text
closure_owner: claude
thread: architecture
lane: real-build-kickoff
claim: claude:real-build-kickoff
phase: design
```

- [x] New task `golem-real-build` opened to close convergence-theater gap.
- [x] First batch of 5 lanes named with verifiable acceptance criteria.
- [x] Five lanes converged: mac-studio-host-stub-server, synthetic-camera-dataset, vision-model-architecture, pi-camera-driver-protocol, sensor-hierarchy-design.
- [x] Closure owner sends `HANDOFF_CONVERGED` after the five children converge.

## mac-studio-host-stub-server

```text
closure_owner: codex:primary
thread: implementation
lane: mac-studio-host-stub-server
claim: impl:mac-studio-host-stub-server
phase: design
```

- [x] `golem2/host/server.py` exists and uses stdlib HTTP (no Flask install).
- [x] `python3 -m golem2.host.server` starts on 127.0.0.1:8765 with port override.
- [x] All six contract endpoints return JSON matching `model_host_contract.md`.
- [x] `/sleep/{job_id}` returns monotonic in-memory progress.
- [x] `golem2/experiments/host_server_roundtrip.py` starts the server in a thread and round-trips every endpoint via `ModelHostClient`.
- [x] Demo `python3 -m golem2.experiments.host_server_roundtrip` exits 0 with non-empty output for every endpoint.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## synthetic-camera-dataset

```text
closure_owner: codex:primary
thread: implementation
lane: synthetic-camera-dataset
claim: impl:synthetic-camera-dataset
phase: design
```

- [x] `golem2/sim/camera.py` exposes `render_top_down(scene, pose, width, height)` returning `list[list[int]]` with 0/1/2 pixel convention.
- [x] Walls rasterized from `scene.walls` by segment sampling.
- [x] `golem2/experiments/synthetic_dataset_gen.py` produces 200 (frame, target_distances, pose) records as JSONL under `golem2/runs/synthetic_dataset/<uuid>/dataset.jsonl`.
- [x] Target is the 8-direction proximity vector computed via existing `scene.proximity_scan`.
- [x] Demo prints dataset path, count, frame shape, target shape, and an ASCII visualization of one frame.
- [x] Demo `python3 -m golem2.experiments.synthetic_dataset_gen` exits 0 with a non-empty JSONL file written.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## vision-model-architecture

```text
closure_owner: codex:primary
thread: implementation
lane: vision-model-architecture
claim: impl:vision-model-architecture
phase: design
```

- [x] `golem2/policies/vision_model.py` defines `VisionMLP(input_h, input_w, hidden, output, seed=0)`.
- [x] Weights initialised deterministically from `seed`.
- [x] `predict(frame) -> list[float]` returns a length-8 vector matching `ProximityRing.distances()` shape.
- [x] Forward pass uses only stdlib (no numpy/torch).
- [x] `golem2/experiments/vision_model_forward_loop.py` runs forward on one sample (from JSONL dataset if available, otherwise fabricated) and prints the 8 floats.
- [x] Demo `python3 -m golem2.experiments.vision_model_forward_loop` exits 0 with 8 floats on stdout.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## pi-camera-driver-protocol

```text
closure_owner: codex:primary
thread: implementation
lane: pi-camera-driver-protocol
claim: impl:pi-camera-driver-protocol
phase: design
```

- [x] `golem2/robot/camera.py` defines `CameraReading`, `CameraDriver` Protocol, `CameraRing`, `FakeCameraDriver`.
- [x] `CameraReading.captured_at` defaults to ISO-UTC via `__post_init__` (mirrors `ProximityReading`).
- [x] `CameraRing` validates frame shape and rejects stale frames when `max_age_seconds` is set.
- [x] `golem2/experiments/camera_driver_loop.py` reads 5 frames through the ring and proves staleness rejection fires.
- [x] Demo `python3 -m golem2.experiments.camera_driver_loop` exits 0.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## monitor-by-phase

```text
closure_owner: codex:primary
thread: implementation
lane: monitor-by-phase
claim: impl:monitor-by-phase
phase: design
```

- [x] `ryot_monitor.py` derives a phase per lane from latest status using RYOT.md's Lane Phases table.
- [x] New "Phases" output section groups lanes stuck → design → implement → converged.
- [x] Stuck lanes carry operator-queue hint when an Operator Blocked Queue entry exists.
- [x] Converged lanes excluded by default; `--include-converged` shows them.
- [x] WITHDRAWN and INFO_ONLY handoffs are ignored for phase derivation; lanes with no qualifying status report `unknown`.
- [x] `python3 -m py_compile ryot_monitor.py` passes.
- [x] Demo `python3 ryot_monitor.py` exits 0 with non-empty Phases section.
- [x] Demo `python3 ryot_monitor.py --include-converged` shows prior closed lanes.
- [x] Claude audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## heatmap-reader-supervised

```text
closure_owner: codex:primary
thread: implementation
lane: heatmap-reader-supervised
claim: impl:heatmap-reader-supervised-bootstrap
phase: implement
```

- [x] Dataset generator emits (state, target_heatmap) pairs from sim.
- [x] BFS ground truth uses operator's r/g/b semantics.
- [x] Tiny CNN trains via MSE in seconds/minutes on local Torch runtime.
- [x] Action selector reads heatmap and picks an 8-neighbor target.
- [x] Navigation loop integrates with `IdealBasementScene.safe_move`.
- [x] Oracle baseline confirms action selector and nav loop are structurally correct.
- [x] Trained model achieves > 0% navigation success on held-out pairs.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## heatmap-reader-local-gradient-loss

```text
closure_owner: codex:primary
thread: implementation
lane: heatmap-reader-local-gradient-loss
claim: impl:heatmap-reader-local-gradient-loss
phase: implement
depends_on: implementation:heatmap-reader-supervised:turn-2
```

- [x] `golem2/learn/losses.py` exposes value MSE + local-weighted MSE + 8-neighbor argmax CE terms.
- [x] Local-weighted MSE uses a Gaussian mask centered on each example's robot cell with per-example normalization.
- [x] 8-neighbor argmax CE uses ground-truth `g - |r|` argmax over the 8 neighbors as target; off-grid neighbors are masked with `-inf` in both pred and target.
- [x] `golem2/learn/heatmap_reader_v2.py` exposes a v2 reader with occupancy + robot one-hot + goal one-hot input channels in place of broadcast scalars.
- [x] `golem2/experiments/heatmap_train_local_loss_demo.py` trains the v2 model with the combined loss and reports per-rollout navigation outcomes against the same held-out test set the bootstrap reported on.
- [x] Trained model achieves >= 5/10 navigation success on the held-out test set (vs 0/10 in the bootstrap claude run and 1/10 in codex's audit run).
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## heatmap-reader-multi-scene

```text
closure_owner: codex:primary
thread: implementation
lane: heatmap-reader-multi-scene
claim: impl:heatmap-reader-multi-scene
phase: implement
depends_on: implementation:heatmap-reader-local-gradient-loss:turn-1
```

- [x] `golem2/learn/maze_family.py` exposes `random_maze_scene(seed)` and `maze_family(n)` returning deterministic distinct maze layouts (fixed outer box, 2-4 random axis-aligned interior walls anchored to one edge).
- [x] `golem2/experiments/heatmap_train_multi_scene_demo.py` trains the v2 model + combined loss across many scenes (100 mazes × 60 pairs = 6000 examples) and reports both OOD (held-out scenes) and IID (held-out poses on train scenes) navigation success.
- [x] `torch.manual_seed(0)` so codex can reproduce headline numbers.
- [x] Uses the softplus-head v2 reader (the dead-head-resistant variant landed by the default-claude review).
- [x] Trained model achieves real generalization to unseen mazes: OOD success >= 25% across 40 rollouts on never-seen mazes, IID success within ±5pp of OOD, confirming the model learns a planning rule from occupancy rather than memorizing one layout.
- [x] Codex runs the demo and records actual OOD/IID success rates: OOD 13/40 = 32.5%; IID 7/20 = 35.0%.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## sensor-hierarchy-design

```text
closure_owner: claude
thread: architecture
lane: sensor-hierarchy-design
claim: claude:sensor-hierarchy-design
phase: design
```

- [x] `golem2/docs/sensor_hierarchy.md` enumerates all required sensors: proximity, camera, IMU, wheel encoders, battery/power, kill-switch readback.
- [x] Per-sensor: latency budget, latch it feeds, regime threshold it modifies, current driver state (fake/real).
- [x] Document marks operator-blocked-on-parts vs implementable-as-fake-driver-now for each sensor.
- [x] Perception pipeline documented end-to-end: synthetic dataset → training → Mac Studio inference → Pi reflex consumer → sleep replay.
- [x] Each existing lane mapped to its place on the hierarchy.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## broadcast-lane-impl

```text
closure_owner: claude
thread: implementation
lane: broadcast-lane-impl
claim: claude:broadcast-lane-impl
phase: implement
```

- [x] `RYOT.md` adds a "Broadcast Lanes" section after "Lane Phases" defining `notes_broadcast.md`, `to: *`, broadcast wrapper, restart-required note.
- [x] `ryot_poll.py` reads `notes_broadcast.md` in addition to its directed inbox each poll cycle.
- [x] `ryot_poll.py` treats `to: *` as a match for any agent; self-authored suppression still applies.
- [x] `ryot_poll.py` `HEADER_RE` accepts both `<!-- HANDOFF` and `<!-- BROADCAST` wrappers (verified: regex matches the broadcast file).
- [x] `ryot_poll.py` tags broadcast output as `RYOT BROADCAST` (vs `RYOT HANDOFF`) and labels `source=broadcast` so humans can tell them apart.
- [x] `python3 -m py_compile ryot_poll.py` passes.
- [x] `notes_broadcast.md` exists with first broadcast carrying `protocol_version: v2` and announcing both new RYOT.md sections.
- [x] Operator restarts active watchers (`poll_codex.sh`, `poll_claude.sh`) so the new scan code is in memory; every non-author watcher state file ends up with `last_turn__broadcast__protocol-v2-phases-and-broadcasts=1` for this Claude-authored broadcast. Superseded by operator instruction to kill pollers and use `ryot_monitor.py --watch`; no active poll watchers remain to restart.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## operating-mode-monitor-only

```text
closure_owner: claude
thread: architecture
lane: operating-mode-monitor-only
claim: claude:operating-mode-monitor-only
phase: implement
```

- [x] `RYOT.md` has an "Operating Modes" section before "Failure Modes".
- [x] Section names both modes (polling-watcher, monitor-only) and a mixed option.
- [x] Section describes state-file consequences of each mode (polling auto-advances, monitor-only freezes).
- [x] Section covers switch-from-X-to-Y procedures for both directions.
- [x] Section covers broadcast handling in both modes.
- [x] No code changes — documentation lane only; `poll_*.sh` and `ryot_monitor.py` left intact.
- [x] Codex audit clears the lane.
- [x] Closure owner sends `HANDOFF_CONVERGED`.

## pre-migration-halt-coordination

```text
closure_owner: claude
thread: architecture
lane: pre-migration-halt-coordination
claim: claude:pre-migration-halt-coordination
phase: design
task: mac-studio-migration
```

- [x] Claude broadcasts pre-migration-halt to `notes_broadcast.md` (lane turn 1).
- [x] Claude ships coordination handoff to codex (this lane, turn 1).
- [x] Claude session is at rest; no new lanes or ratifications pending from this side.
- [x] Codex acknowledges halt via `HANDOFF_CONVERGED` on this lane.
- [x] heatmap-bootstrap claude (if active) confirmed halted or idle.
- [x] Codex pings operator via GPT-app phone loop with check-in-ready message.
- [ ] Operator confirms migration ready; lane carries over to Mac Studio side and closes after the new RYOT pipeline is up.

## operator-hardware-bringup

```text
closure_owner: operator
thread: hardware
lane: mac-studio-ubuntu-robot-layout
claim: operator:physical-bringup
phase: design
```

- [ ] Mac Studio confirmed as AI, RYOT, git, GPU, and operator plane.
- [ ] Ubuntu VM confirmed as robot, Linux build/test, data, and validation plane.
- [ ] Repo sync or shared workspace path chosen between Mac Studio and Ubuntu VM.
- [ ] Ubuntu VM can reach the Mac Studio AI REST proxy.
- [ ] Mac Studio AI REST proxy cannot command actuators.
- [ ] AI threshold API accepts only normalized `[0.0, 1.0]` threshold values.
- [ ] Ubuntu threshold authority rejects unknown threshold keys.
- [ ] Ubuntu threshold authority rejects threshold values outside `[0.0, 1.0]`.
- [ ] Ubuntu threshold authority enforces max delta, cooldown, TTL, and rollback.
- [ ] Robot runtime continues safely when the AI proxy is down or slow.
- [ ] Human-visible logs show every accepted and rejected threshold proposal.
- [ ] Physical e-stop or independent power-cut path is verified before real motion.
- [ ] Selector research host chosen with rewirable posit/token selection.
- [ ] `llama.cpp` is not used as the direct runtime selector host unless the operator explicitly re-approves it.

## Operator Blocked Queue

This is the visible list of items waiting on operator input. Both agents
append here when a lane goes `BLOCKED` or has an operator-only dependency.
Operator processes items in any order; once unblocked, the responsible
agent reopens the lane and removes the item from this section.

### From claude

- [x] **hardware-architecture** — resolved with conservative defaults:
  sensor and motor hardware remain adapter-injected and fake/sim only
  until the operator confirms exact parts; Raspberry Pi is the first
  reflex runtime target; Arduino stays optional for deterministic
  actuator/sensor timing only; Mac Studio calls are bounded HTTP over
  local LAN; no real motor run is permitted until independent hardware
  kill-switch wiring is confirmed. Source: `audit/hardware-architecture`
  turn 1, resolved during convergence pass.

### From codex

- (none yet — codex appends here when blocked)

## Operator Hardware Resources

Known operator-side resources (treat as available unless told otherwise):

- **Mac Studio** — RYOT, Codex, Claude, AI REST proxy, selector/model host,
  Apple GPU service tier, and operator console.
- **Ubuntu VM on Mac Studio** — Linux robot build/test/runtime plane and
  threshold authority; no native Apple GPU assumption.
- **Raspberry Pi** — optional physical sensor aggregation + motor control
  reflex tier.
- **Arduino** — optional hard-real-time tier; operator can push smarts
  there if needed.
- **3D printer** — custom mounts, brackets, chassis, sensor housings.
- **Amazon Prime** — fast component ordering (sensors, motors,
  H-bridges, IMUs, encoders, jumper wire, headers).
- **Soldering iron + operator skill** — custom interfaces, sensor
  boards, kill-switch circuits feasible.

This list informs the hardware-architecture design space. If an
implementation lane wants a part the operator already has, just use it;
if it wants something new, name it here and the operator can order.
