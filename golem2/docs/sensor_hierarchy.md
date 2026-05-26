# Sensor Hierarchy For The Basement Robot

This document is the first real-build hierarchy for the threshold-control robot.
It keeps the AI host above the reflex loop: AI services may propose normalized
thresholds in `[0.0, 1.0]`, while the Ubuntu robot runtime owns fresh sensor
reads, latch updates, validation, and motor safety.

## Runtime Layers

```text
Mac Studio
  RYOT, Codex, Claude, operator console
  AI REST proxy
  MLX/Transformers selector host
  PyTorch/vision model host
  sleep replay over event ledgers

Ubuntu VM
  Linux robot builds and tests
  robot services
  sensor data aggregation
  threshold authority and validation
  local logs and event ledgers

Raspberry Pi
  optional physical sensor/actuator bridge
  freshness gates close to hardware
  projection latches close to hardware
  reflex motor executor if deployed off the VM
  telemetry REST surfaces

Optional Arduino
  deterministic sensor/actuator timing
  kill-switch readback
  encoder pulse counting

Robot body
  proximity sensors
  camera
  IMU
  wheel encoders
  battery/power monitor
  independent kill switch
```

The Ubuntu robot runtime, and any Pi or Arduino tier below it, must be able to
continue a safe reflex loop if the Mac Studio AI proxy is slow, unavailable, or
training. The Mac can improve models and propose threshold changes; it is not
the safety boundary.

The Mac Studio GPU is not treated as a native Ubuntu VM device. If a runtime
needs Apple GPU acceleration, expose it as a Mac-hosted service and call it
from Ubuntu over the AI proxy instead of relying on VM GPU passthrough.

## AI Threshold Contract

AI output is advisory and limited to threshold proposals:

```text
Ubuntu gathers reality.
Mac Studio interprets reality.
Ubuntu validates and acts.
```

Validation lives on Ubuntu in a threshold authority module:

- threshold names must be allowlisted;
- threshold values must be floats in `[0.0, 1.0]`;
- proposals must respect max delta, cooldown, and TTL;
- stale or malformed proposals are ignored;
- every accepted or rejected proposal is logged;
- AI-originated actuator commands are invalid by construction.

Hardware commands come only from local robot logic after validation. AI may
move thresholds; it cannot control motors, relays, GPIO, serial devices, or
power.

## Sensor Table

| Sensor | Latency Budget | Projection/Latch | Regime Threshold It Modifies | Driver State | Blocked vs Implementable |
| --- | --- | --- | --- | --- | --- |
| Eight proximity sensors | 20-50 ms for reflex avoidance | distance panorama, nearest-obstacle latch, sector clearance latch | `min_clearance`, `front_stop`, `turn_preference`, obstacle urgency | fake/sim driver exists in `golem2/robot/proximity.py`; real adapter pending parts | real hardware pinout/operator parts blocked; fake driver implementable now |
| Camera | 100-250 ms for visual salience, not hard stop | 2D image heatmap, goal/category salience, motion/velocity latch | `visual_catness`, `motion_salience`, `goal_visibility`, exploration urgency | fake camera driver exists in `golem2/robot/camera.py`; synthetic renderer exists in `golem2/sim/camera.py` | real camera device choice and mounting blocked; fake/synthetic pipeline implementable now |
| IMU | 20-100 ms for orientation sanity | 2D/3D orientation map, tilt latch, rotation-rate latch | `max_tilt`, `turn_rate_limit`, stuck/impact suspicion | no concrete driver yet | fake IMU driver implementable now; real part and calibration operator-blocked |
| Wheel encoders | 5-20 ms for odometry/reflex | displacement map, velocity latch, slip latch | `expected_motion`, `wheel_slip`, `odometry_confidence`, stuck threshold | no concrete driver yet | fake encoder driver implementable now; real encoder hardware/motor mount operator-blocked |
| Battery/power monitor | 0.5-2 s for policy, faster if brownout line exists | power health latch, voltage sag latch | `low_power_hold`, `return_home`, `sleep_allowed`, model-host usage | no concrete driver yet | fake power driver implementable now; real monitor interface operator-blocked |
| Kill-switch readback | 5-20 ms for hard safety | hard-stop latch, motion authorization latch | `motion_enabled` only; no LLM override | no concrete driver yet | real wiring/operator confirmation blocked; fake readback implementable for tests only |

## Latch Pattern

Each sensor should expose two values:

- `sample`: the current quantized reading.
- `trial`: an EMA of recent readings under the current urgency.

The difference between sample and trial is velocity. Higher urgency shortens the
EMA and gives finer control, but total focus is conserved. A regime can split a
total urgency budget of `0.5` across its active thresholds.

Common latch shapes:

- Distance map: proximity readings become a signed panorama where near obstacle
  cells contribute red evidence and clear cells contribute green evidence.
- Goal map: camera/model output marks likely target or category cells.
- Orientation map: IMU yaw/pitch/roll or 2D pose deltas become orientation
  evidence.
- Displacement map: wheel encoders and visual odometry estimate expected vs
  observed movement.
- Power map: voltage/current/brownout readings gate allowed energy use.
- Safety map: kill-switch readback gates all motion, independent of policy.

Every latch should publish the common telemetry contract:

```text
GET /health
GET /telemetry/current
GET /telemetry/history?limit=100
GET /telemetry/schema
```

The payload should include calibration, threshold, urgency, sample, trial,
velocity, latched state, and any slip opportunities.

## Perception Pipeline

The first visual-control pipeline should be built in this order:

```text
synthetic scene
  -> perfect proximity/camera frames
  -> target heatmaps from known geometry
  -> heatmap-reader training on Mac Studio
  -> model inference endpoint on Mac Studio
  -> Ubuntu threshold authority
  -> Pi camera/proximity consumer
  -> local projection latches
  -> motor reflex policy
  -> event ledger
  -> sleep replay on Mac Studio
```

The synthetic camera dataset (`golem2/sim/camera.py` and
`golem2/experiments/synthetic_dataset_gen.py`) supplies perfect images and
perfect labels. The heatmap reader bootstrap (`golem2/learn/heatmap_dataset.py`,
`golem2/learn/heatmap_reader.py`, and
`golem2/experiments/heatmap_train_navigate_demo.py`) starts supervised learning
from BFS ground truth. The Mac Studio host (`golem2/host/server.py`) provides
the model and sleep endpoints. The Pi-side fake camera/proximity drivers let the
same consumer code run before real hardware arrives.

## Existing Lane Map

| Lane | Place In Hierarchy |
| --- | --- |
| `pi-sensor-drivers` | Pi proximity driver contract and freshness-ready sensor input. |
| `proximity-freshness-gate` | Rejects stale proximity marks before latches or motors consume them. |
| `pi-camera-driver-protocol` | Camera reading protocol, fake camera, camera ring, stale-frame guard. |
| `synthetic-camera-dataset` | Perfect simulated camera frames and labels for visual training. |
| `vision-model-architecture` | Lightweight model contract for visual inference experiments. |
| `heatmap-reader-supervised` | First Torch training loop from simulated state to heatmap navigation. |
| `mac-studio-host-stub-server` | Local REST host for model inference, train steps, sleep jobs, and LM Studio-compatible calls. |
| `sleep-replay-packet` | Selects failures, near-threshold cases, crossings, and rare states for sleep training. |
| `real-motor-executor` | Motion safety boundary and injected real executor interface. |
| `sim-collision-avoidance` | Simulation-only safe movement and collision clipping. |
| `maze-occupancy-solver` | Occupancy/free-space map and known-free solver over proximity-derived structure. |
| `urgency-budget-pressure-demo` | Conserved urgency budget across regime thresholds. |
| `adjustment-rate-limit` | Cooldown/rate limit for threshold adjustments. |
| `monitor-by-phase` | Operator view of design/implement/converged/stuck lanes. |

## Slip Opportunities

Sensors do not need to tell the LLM everything. They should report exceptional
or near-threshold structure:

- obstacle distance just above `front_stop`;
- repeated motor command with low encoder displacement;
- visual category score just below threshold;
- battery sag during motion;
- tilt or impact near safety threshold;
- stale sensor near a required reflex decision;
- map gap where a second view would collapse uncertainty.

These become graph records such as `slip_opportunity`,
`threshold_crossing`, `failure`, and `affordance`. The AI proxy receives those
records plus bounded regime options, then proposes threshold updates rather
than direct motor commands.

## Next Implementation Slots

The implementable fake-driver slots are:

- fake IMU reading protocol and orientation latch;
- fake wheel encoder protocol and odometry/slip latch;
- fake power monitor protocol and low-power latch;
- fake kill-switch readback protocol with hard motor gate tests;
- REST telemetry adapter for every latch.

The operator-blocked real-hardware slots are:

- exact proximity sensor model and pinout;
- camera device, lens, mounting, and frame rate;
- IMU part and calibration procedure;
- encoder hardware/motor integration;
- battery monitor interface;
- independent kill-switch wiring and verified readback path.
