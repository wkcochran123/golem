# Mac Studio Host Contract

The robot should stay small. The Mac Studio is the in-house intelligence host.
It has two roles:

- LM Studio hosts local LLMs for policy selection, exception review, and graph
  interpretation;
- a PyTorch service stores visual/control models, runs inference on demand,
  accepts online training updates, and runs sleep-mode replay over the day's
  ledger.

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
the robot executor. The host may suggest policies or train models; the robot
executor still enforces hard stops, speed caps, stale-sensor checks, and
timeouts. This keeps experimentation total-inhouse without putting remote
inference inside the reflex safety boundary.
