# Mac Studio Host Contract

The robot should stay small. The Mac Studio is the in-house intelligence host
and RYOT operator plane. Ubuntu runs inside a VM on the Studio as the Linux
robot infrastructure: builds, robot services, sensor data preparation, logs,
and local safety validation live there. Ubuntu calls the Mac Studio over a
small REST boundary for AI work.

The Mac Studio host has three roles:

- RYOT, Codex, Claude, git credentials, and the operator console stay on the
  Mac host;
- selector/model services run on the Mac host so they can use Apple GPU
  acceleration and experimental generation loops;
- a REST proxy exposes only bounded AI calls to the Ubuntu robot runtime.

The experimental selector host should be something the operator can rewire,
for example MLX/`mlx-lm` or a Transformers generation loop with a custom
selector/logits processor. Do not make the robot runtime depend directly on a
`llama.cpp` server for selector research; prior experiments showed timing
stress around data ingress/egress can lock or starve that host.

Minimum AI proxy REST surface:

```text
GET  /health
GET  /models
POST /ai/propose-thresholds
POST /ai/classify-event
POST /ai/summarize-telemetry
POST /models/{model}/infer
POST /models/{model}/train_step
POST /sleep/start
GET  /sleep/{job_id}
```

`POST /ai/propose-thresholds` is the runtime path for threshold adjustment
advice. It returns proposals only; Ubuntu decides whether to apply them.

```json
{
  "state": {
    "sensor_window": {},
    "recent_outcomes": [],
    "current_thresholds": {
      "front_obstacle_risk": 0.65,
      "clear_path_low": 0.55
    }
  },
  "constraints": {
    "allowed_thresholds": ["front_obstacle_risk", "clear_path_low"],
    "range": [0.0, 1.0],
    "max_delta": 0.05,
    "ttl_seconds": 900
  }
}
```

Response:

```json
{
  "proposed_thresholds": {
    "front_obstacle_risk": 0.7
  },
  "confidence": 0.68,
  "ttl_seconds": 900,
  "rationale": "Recent obstacle latch events are clustered near the current boundary."
}
```

Hard invariants:

- every AI-adjustable threshold is a normalized float in `[0.0, 1.0]`;
- unknown threshold keys are rejected by Ubuntu;
- values outside `[0.0, 1.0]` are rejected by Ubuntu;
- Ubuntu enforces max delta, cooldown, TTL, and rollback;
- AI responses never contain actuator commands;
- robot control remains safe when the Mac Studio AI proxy is slow or down.

Minimum PyTorch REST surface:

```text
GET  /health
GET  /models
POST /models/{model}/infer
POST /models/{model}/train_step
POST /sleep/start
GET  /sleep/{job_id}
```

Minimum LM Studio-compatible LLM surface:

```text
GET  /v1/models
POST /v1/chat/completions
```

The exact LM Studio endpoint should remain OpenAI-compatible where possible so
the robot can swap local models without changing its policy protocol. The LLM
receives graph summaries, active failures, slip opportunities, and affordances;
it returns a typed policy/action proposal rather than direct motor control.

`POST /models/{model}/infer` receives heat-map/latch/graph context:

```json
{
  "input": {
    "before_heatmap": "...",
    "after_heatmap": "...",
    "projection": "distance",
    "action": {"command": "turn_left"},
    "graph_context": {}
  }
}
```

`POST /models/{model}/train_step` is the inline backprop path:

```json
{
  "transition": {
    "sample": {},
    "trial": {},
    "prediction": {},
    "observed": {},
    "loss": {}
  }
}
```

`POST /sleep/start` launches semi-informed replay:

```json
{
  "ledger_path": "events.jsonl",
  "models": ["heatmap_reader", "urgency_policy"],
  "sampling": {
    "failures": true,
    "near_threshold": true,
    "successful_crossings": true,
    "rare_sensor_states": true
  }
}
```

The Mac Studio is not the robot's safety gate. Real-time motor safety stays on
the Ubuntu robot runtime and any downstream hardware controller. The host may
suggest normalized thresholds or train models; the robot executor still
enforces hard stops, speed caps, stale-sensor checks, timeouts, and hardware
authorization. This keeps experimentation in-house without putting remote
inference inside the reflex safety boundary.
