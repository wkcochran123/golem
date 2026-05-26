# golem2

`golem2` is a fresh vertical slice of the loop described by the operator:

```text
LLM/policy chooses action
code executes action
world produces residue
sensors record residue
salience highlights what changed
categorizer names stable distinctions
graph stores relations, failures, affordances
policy receives graph and tries again
```

This first slice uses a local filesystem directory as the world. It avoids the
old free-form command parser and records every stage as append-only JSONL events.

## Run The Slice

```bash
python3 -m golem2.experiments.local_file_loop
python3 -m golem2.experiments.file_sort_loop
python3 -m golem2.experiments.file_sort_recovery_loop
python3 -m golem2.experiments.quantized_heatmap_loop
python3 -m golem2.experiments.projection_latch_loop
python3 -m golem2.experiments.proximity_panorama_loop
python3 -m golem2.experiments.llm_proximity_loop
python3 -m golem2.experiments.llm_proximity_two_latches_loop
python3 -m golem2.experiments.proximity_mapping_loop
python3 -m golem2.experiments.map_latch_loop
python3 -m golem2.experiments.ideal_basement_dataset
python3 -m golem2.experiments.telemetry_snapshot_loop
python3 -m golem2.experiments.regime_threshold_loop
python3 -m golem2.experiments.regime_rate_limit_loop
python3 -m golem2.experiments.policy_input_bound_loop
python3 -m golem2.experiments.real_motor_executor_loop
python3 -m golem2.experiments.pi_proximity_driver_loop
python3 -m golem2.experiments.urgency_budget_pressure_loop
python3 -m golem2.experiments.sleep_replay_packet_loop
python3 -m golem2.experiments.proximity_freshness_loop
python3 -m golem2.experiments.maze_navigation_demo
python3 -m golem2.experiments.host_server_roundtrip
python3 -m golem2.experiments.synthetic_dataset_gen
python3 -m golem2.experiments.vision_model_forward_loop
python3 -m golem2.experiments.camera_driver_loop
```

The run writes artifacts under `golem2/runs/local_file_loop/`:

- `events.jsonl`: append-only event stream
- `graph.sqlite`: observed entities and relations
- `world/`: the small local environment the action mutates

## Current Shape

- `events.py`: typed event envelope and event constructors
- `store.py`: append-only event log
- `actions.py`: constrained local actions
- `sensors.py`: filesystem residue snapshots
- `salience.py`: before/after change extraction
- `categorizer.py`: stable names for salient changes
- `graph.py`: SQLite knowledge graph
- `policies/scripted.py`: deterministic policy stub standing in for an LLM
- `policies/file_sort_scripted.py`: deterministic graded-task policy
- `policies/file_sort_recovery_scripted.py`: deterministic failure-recovery policy
- `policies/llm.py`: OpenAI-compatible adapter that emits the same action schema
- `policies/types.py`: policy/regime payload types with optional context bounds
- `policies/regimes.py`: named operating regimes such as `find_cat`
- `policies/regime_manager.py`: bounded threshold-control executor for regimes
  with optional latch bindings, opt-in adjustment cooldowns, and event/graph
  recording
- `policies/proximity_regime_scripted.py`: offline LM Studio-shaped proximity policy
- `policies/proximity_two_latch_scripted.py`: offline two-threshold proximity policy
- `graders/file_sort.py`: a real score signal for a local sorting task
- `vision/quantized_heatmap.py`: signed 2D heat-map surface for quantized sensors
- `vision/latches.py`: simple latches over known projection maps
- `vision/projection_transforms.py`: shared transforms from sensor values to projection maps
- `mapping/occupancy.py`: 2D occupancy ledger with occupancy/free-space projection maps
- `robot/motors.py`: typed simulated motor commands with safety gates
  and a real-executor interface for injected Pi-side drivers
- `robot/proximity.py`: typed proximity sensor readings and validated Pi-side
  driver contract
- `robot/camera.py`: typed fake camera readings and freshness-checked camera ring
- `sim/ideal_basement.py`: perfect room geometry and perfect proximity sensors
- `sim/camera.py`: top-down integer camera renderer over simulated walls/poses
- `experiments/maze_navigation_demo.py`: simulation-only collision clipping,
  occupancy mapping, and known-free maze solving
- `host/server.py`: stdlib HTTP model-host stub for local contract tests
- `policies/vision_model.py`: deterministic pure-Python MLP forward pass
- `telemetry/snapshot.py`: common component telemetry payloads
- `telemetry/sensor_stack.py`: stackable scalar telemetry sensors with bounded
  set/nudge/spread commands
- `host/model_host.py`: Mac Studio model-host clients with real-time-friendly timeouts
- `host/sleep_replay.py`: sleep-mode replay packet builder for event ledgers
- `runtime/loop.py`: one complete cycle through the loop

The policy stub is deliberately replaceable. To use an OpenAI-compatible local
host, provide `GOLEM2_LLM_BASE_URL`, `GOLEM2_LLM_MODEL`, and optionally
`GOLEM2_LLM_API_KEY`, then pass `LLMPolicy()` into `LocalWorldLoop`.

## Current Robot Slice

The proximity work now has three runnable levels:

- `proximity_panorama_loop`: local reflex loop over eight proximity readings.
- `llm_proximity_loop`: offline LM Studio-shaped policy adjusts one obstacle
  threshold while motor actions remain local.
- `llm_proximity_two_latches_loop`: distance-panorama obstacle latch plus
  occupancy-map clear-path latch in one regime.

The LLM/LM-Studio role is threshold control, not direct motor control.
