# Component Telemetry REST Contract

Every `golem2` component should expose a common JSON surface for visualization,
monitoring, replay, notebooks, and exceptional-case LLM context.

Minimum endpoints:

```text
GET /health
GET /telemetry/current
GET /telemetry/history?limit=100
GET /telemetry/schema
```

`/telemetry/current` returns:

```json
{
  "id": "snapshot-id",
  "timestamp": "2026-05-25T00:00:00Z",
  "component": "front_obstacle_gate",
  "kind": "projection_latch",
  "payload": {
    "threshold": 0.0625,
    "urgency": 0.5,
    "sample_score": 1.0,
    "trial_score": 0.5,
    "velocity": 0.0625,
    "latched": true
  }
}
```

The endpoint is a ledger surface. It should report what the component has
admitted as a mark, not an unverifiable story about the world.

Common payload fields when available:

- `calibration`
- `threshold`
- `urgency`
- `sample`
- `trial`
- `score`
- `velocity`
- `latched`
- `failure_kind`
- `policy_hints`
- `slip_opportunities`

