# Ten-Step Visual Loop

This is the working design target for `golem2`.

The loop:

```text
10  LLM writes/chooses policy
20  code executes action
30  real world produces residue
40  sensors record residue
50  heat map highlights salience
60  visual learner turns pixels into distinctions
70  categorizer names stable distinctions
80  knowledge graph stores relations
90  LLM receives graph + failures + affordances
100 GOTO 10
```

## Reading Spine

The three measurement volumes suggest a stricter interpretation of the loop.

From `Order`:

- A system does not know the world directly. It carries a ledger of marks.
- A mark is useful only when it preserves a distinction.
- Residue is not trash. It is the structured part left over after an operation
  fails to discharge the whole situation.
- Gaps are structured absences. They should be carried as unresolved variables,
  not filled with convenient stories.
- Closure is append-only: later knowledge amends the ledger rather than erasing
  earlier records.

From `Measurement`:

- A sensor admits events through thresholds. Sub-threshold burden can be real
  without becoming a mark in the relevant ledger.
- Slip is a threshold crossing: burden accumulates without visible displacement
  until a critical condition is crossed and motion becomes admissible.
- Calibration is part of the record. A reading without a named reference is not
  trustworthy.
- Multiple records need apparatus accountability: source, role, calibration,
  timing, and failure ownership must remain distinguishable.
- Premature closure is an error. A candidate visual interpretation can be held
  open as a constrained unknown.

From `The Compiler`:

- Each stage should be an auditable bounded operation, not a vague intuition.
- Combining records without collapsing identities is union-find-shaped.
- Union failures are records, not exceptions. A failed merge is knowledge.
- Transport requires a warrant. Facts moved from pixels to categories to graph
  relations need evidence trails.
- The final ledger grows append-only and reaches local closure when its internal
  checks pass.

## Core Terms

`Mark`
: An admitted record produced by a sensor under a threshold and calibration.

`Residue`
: The structured leftover after an action. In this loop, residue includes pixels,
file diffs, logs, new object positions, missing expected changes, and failed
effects.

`Salience`
: A map of where residue differs enough to matter under the current calibration.
For vision, this is literally a heat map over pixels or regions.

`Quantized Heat Map`
: A 2D signed ledger surface produced from any sensor after thresholding. Each
cell carries red as negative evidence (`r = -1`), green as positive evidence
(`g = +1`), and blue as balanced uniform calibration noise (`b in {-1, +1}`).
The total score is the learned optical sum over the surface; two heat maps can
be compared by whether that score increases or decreases.

`Distinction`
: A stable difference the learner can carry forward: moved/not moved, present/not
present, button/enabled button, edge/gap, object/background, before/after.

`Category`
: A named stable distinction that has survived enough evidence to be useful.

`Slip Opportunity`
: A graph record saying that a visible or inferred system is near a threshold
where an action may produce an admissible transition. It is not merely an
affordance. It is an affordance plus a threshold story.

Historical crossings and future opportunities are different records. A
crossed threshold becomes a `threshold_crossing` event. A near-threshold
non-crossing can become a `slip_opportunity`, because it predicts that a
future action might cross.

Examples:

- A box is strained but not moving; more force or a different angle may make it
  slip.
- A UI element is visible but not activated; a click may cross the interface
  threshold.
- A drag target is near an alignment boundary; a small move may snap it into
  place.
- A file-sort task has one misplaced item; moving it to the named category may
  close the grader.
- A visual hypothesis is unresolved; a camera zoom or second angle may collapse
  the gap.

`Projection Latch`
: A simple component that watches one known projection shape, filters it through
parent-provided thresholds, and latches when the filtered map contains enough
admissible activity. Examples of known projection shapes are distance maps, goal
maps, 2D orientation maps, and 3D orientation maps.

## Knowledge Graph Shape

The graph should not just store objects. It should store measurement grammar.

Suggested node kinds:

- `event`
- `sensor`
- `calibration`
- `threshold`
- `residue`
- `salience_region`
- `distinction`
- `category`
- `object`
- `gap`
- `failure`
- `affordance`
- `slip_opportunity`
- `threshold_crossing`
- `policy`
- `action`
- `grade`

Suggested edge kinds:

- `was_caused_by`
- `was_recorded_by`
- `uses_calibration`
- `crossed_threshold`
- `left_residue`
- `highlights`
- `supports_distinction`
- `names_category`
- `belongs_to_component`
- `failed_with`
- `opens_gap`
- `constrains_gap`
- `affords`
- `near_threshold_for`
- `has_slip_opportunity`
- `closed_by`

Each graph fact should carry evidence:

- source event id;
- sensor id;
- timestamp;
- calibration;
- confidence or score;
- pixel box, file path, log span, or other provenance;
- whether the fact is closed, unresolved, or contradicted.

## Ten-Step Implementation Semantics

### 10. LLM Writes Or Chooses Policy

The LLM should emit a typed policy/action proposal, not free-form shell text.
The proposal is a hypothesis about what action will cross a useful threshold.
For local experimentation, this LLM can be hosted on the Mac Studio through
LM Studio's OpenAI-compatible API, keeping policy iteration in-house.

The LLM should usually choose among regimes rather than reason from raw sensor
streams. A regime is a named operating mode with an objective, visible
thresholds, available threshold adjustments, and current unstructured context.

Control happens through thresholds. The thresholds are the joystick. The LLM
does not steer the robot by saying "turn left motor now"; it moves latch
boundaries and urgency allocations. The reflex loop turns those threshold
fields into motor behavior locally.

Example:

```text
regime: find_cat
objective: locate the cat while avoiding unsafe motion
thresholds:
  visual_catness >= 0.65
  motion_salience >= 0.55
  under_furniture_gap <= 0.50
unstructured_context:
  "soft movement near basement couch"
  "no confirmed visual category yet"
  "low clearance region is unresolved"
allowed_actions:
  lower_visual_catness_threshold
  raise_motion_salience_urgency
  lower_under_furniture_gap_urgency
  hold_position
  ask_operator_for_hint
```

The thresholds are structured, but the context can stay messy. This lets the
LLM do what it is good at: choose a plausible regime and threshold adjustment
from partial language, graph facts, failures, and affordances. The visual/sensor
loop still owns admission, scoring, latching, and safety.

Threshold control is bounded by local invariants. Each regime can conserve a
total urgency budget, and a regime manager may enforce a cooldown between
successful adjustments to the same threshold. A rejected threshold move is not
silent; it is recorded as residue for the graph and becomes guidance for the
next policy choice.

This is analog control rather than discrete command control:

```text
LLM adjusts thresholds/urgency -> latches reshape salience
                              -> executor follows local reflex policy
                              -> residue updates the next threshold field
```

Required inputs:

- graph summary;
- open gaps;
- recent failures;
- active slip opportunities;
- current affordances;
- candidate regimes with thresholds;
- current unstructured information;
- task grade or closure condition.

The payload sent to the LLM must be bounded. Graph edges, recent failures,
policy hints, regimes, and thresholds per regime should have explicit caps, and
the payload should carry truncation metadata so the policy can treat missing
context as a known gap rather than invisible loss.

### 20. Code Executes Action

The executor is the calibrated apparatus. It must enforce boundaries and return
structured success or failure. A blocked action becomes a failure record.

### 30. Real World Produces Residue

Residue is whatever changed, failed to change, appeared, disappeared, moved,
remained stuck, logged, blinked, or degraded.

### 40. Sensors Record Residue

Sensors create marks. They must name their threshold and calibration where
possible: screenshot dimensions, crop region, file tree root, polling interval,
OCR settings, pixel-diff threshold, process timeout.

### 50. Heat Map Highlights Salience

The salience layer does not decide what something is. It decides where the
ledger should spend attention.

Any sensor can enter this stage if it can be quantized onto a 2D surface. The
surface is not a picture of the world; it is a calibrated score field:

```text
red   = -1 evidence
green = +1 evidence
blue  = uniformly balanced +/-1 reference/noise channel
```

The optical learner can compare two such fields by total score:

```text
delta_score = score(after) - score(before)
average_delta = delta_score / number_of_cells
strain        = average_delta, until a richer burden-accumulation model exists
threshold_crossed when abs(delta_score) >= threshold
```

This gives the visual system a direct way to say "burden increased,"
"burden decreased," or "strain accumulated but no admissible transition has
crossed threshold yet."

For visual residue this should produce:

- changed pixel regions;
- motion regions;
- stable high-contrast boundaries;
- unresolved/ambiguous regions;
- regions associated with action failure.

### 60. Visual Learner Turns Pixels Into Distinctions

The visual learner turns salient regions into reusable distinctions. The first
goal is not rich object recognition. It is stable difference recognition.

Examples:

- region exists across frames;
- region moved;
- region changed color;
- boundary appeared;
- text changed;
- object resisted action;
- object snapped into a new state.

Each visual component should be a simple latch over two or three common
projections:

- distance map;
- goal map;
- 2D orientation map;
- 3D orientation map;
- contact/strain map;
- motion/residue map.

The parent sets the thresholds. The child sensor provides:

```text
current_threshold
current_projection_image
```

A known law combines parent thresholds:

```text
combined_threshold = law(parent_thresholds)
```

Each level also has a total urgency budget of `0.5`. That urgency can be split
among thresholds. The EMA constant is the urgency:

```text
level_urgency = 0.5
parent_thresholds = split(level_urgency, children)
ema_alpha = urgency
```

Higher urgency means a shorter EMA memory: the trial follows the sample faster,
so control becomes finer and more reactive. Lower urgency means a longer EMA
memory, so control becomes smoother and less excitable.

But focus is finite. A level only has so much urgency to allocate. Spending more
urgency on one latch means spending less elsewhere:

```text
sum(child_urgencies) <= level_urgency
```

This makes attention a conservation law. The system cannot make every threshold
maximally sharp at once; it must choose where fine control matters.

Then the projection image is filtered to that threshold. The current filtered
image is the sample. The EMA is the trial: the stabilized record of what this
component has been seeing.

The visual trainer learns the contextual dynamics around these known laws. Given
the sample and the trial, it estimates velocity:

```text
sample = filtered_current
trial  = ema(filtered_history)
velocity = difference(sample, trial) / cell_count
```

So the learned part is not inventing arbitrary inference shapes. It is learning
how known projection laws behave in this context.

This gives a path back toward number and fact:

```text
sensor mark -> quantized sample -> EMA trial -> score/velocity number
             -> thresholded latch -> graph fact
```

### 70. Categorizer Names Stable Distinctions

The categorizer names distinctions only after enough evidence. It should be able
to say "unresolved" and carry the gap.

Categories are useful when they predict action outcomes or improve graph
compression.

### 80. Knowledge Graph Stores Relations

The graph stores the measurement grammar, not just labels. The key relation for
this project is `has_slip_opportunity`: a category/object/gap plus evidence that
an action may produce a threshold-crossing transition.

### 90. LLM Receives Graph + Failures + Affordances

The LLM gets a compressed working set:

- what is known;
- what is unresolved;
- what failed;
- what can be tried;
- where the graph thinks slip opportunities exist;
- what closure would look like.

### 100. GOTO 10

Every iteration appends. It does not rewrite the past. Wrong categories become
contradicted facts or superseded hypotheses with evidence.

## Immediate Engineering Implication

The current `file_sort_loop` is useful but not visual. It proves:

- typed policy;
- execution;
- residue;
- sensor;
- salience;
- categorization;
- graph;
- grade feedback.

The next visual slice should keep the same loop but swap the sensor/residue
surface:

1. Generate or render a simple visual board with movable objects.
2. Take before/after screenshots.
3. Produce a pixel-diff heat map.
4. Categorize changed regions as stable distinctions.
5. Store at least one `slip_opportunity` relation.
6. Feed that relation back to policy.

The smallest honest version is a 2D board where a piece is dragged toward a
snap zone. The slip opportunity is "piece is near snap threshold." The graph
should record whether the action crossed the threshold and whether the object
snapped into place.

The first robot-bodied experiment is simpler and more urgent:

```text
8 proximity sensors -> panoramic distance heat map -> obstacle latches
                    -> avoidance policy -> motor action
```

The eight sensors point in compass-like directions around the robot. Their
distance readings are converted into risk:

```text
risk = danger_distance - measured_distance
```

Positive risk means "too close"; negative risk means "clear enough." Inside the
danger boundary, risk is quantized in a Lorentzian-like series:

```text
1/2, 3/4, 7/8, 15/16, ...
```

So normalized sensor closeness in `[0, 1]` steepens toward contact. This gives
near-boundary readings more urgency without making the LLM supervise ordinary
motion. The risk panorama becomes a 1x8 heat map, which is still a 2D surface.
Front-arc threshold crossings create obstacle facts and avoidance affordances.

The same sensors also build a 2D map. Given an estimated robot pose, each
proximity reading is a radial constraint:

```text
cells along ray before endpoint -> free
endpoint when distance < max_range -> occupied
no endpoint within max_range -> unresolved/unknown beyond ray
```

So the eight-sensor panorama can feed two ledgers at once:

- a fast reflex ledger for obstacle avoidance;
- a slower occupancy ledger for basement mapping.

The LLM should mostly see exceptional cases: threshold crossings, safety stops,
contradictions, unresolved map gaps, and high-urgency slip opportunities. The
executor and latches handle normal reflexes. The LLM's useful intervention is
often to adjust urgency downward, choose a calmer policy, or request more
evidence rather than directly steering every sample.

This is the same visual inference pattern with a different transformation.
The sensor is unchanged. The projection transform changes:

```text
raw 8-distance panorama -> risk transform      -> obstacle latch
raw 8-distance panorama -> occupancy transform -> map latch
raw 8-distance panorama -> clearance transform -> goal/route latch
```

The downstream shape stays the same:

```text
projection map -> parent threshold law -> filtered sample
               -> EMA trial -> velocity/score -> latch/fact
```

## Training Schedule

Heat-map readers can be trained before they ever touch a physical robot.

### Ideal Simulation

Ideal simulation is the clean room. It has perfect state, perfect labels, and
known thresholds. It teaches the learner the grammar before noise is introduced.

```text
sim state -> simulated sensor -> quantized heat map -> action -> new heat map
```

The ideal simulator can label:

- score increased/decreased;
- threshold crossed/not crossed;
- strain accumulated without crossing;
- slip opportunity present/absent;
- action that would likely cross the threshold;

This lets the visual learner practice turning heat-map pixels into stable
distinctions and categories while the world is perfectly inspectable.

For each proposed visual, the ideal simulator should generate before/after
pairs:

- before pose/state;
- action;
- after pose/state;
- perfect sensor reading before;
- perfect sensor reading after;
- perfect heat maps;
- ground-truth distinction labels;
- ground-truth threshold crossings;
- expected graph facts.

For the 8-proximity basement robot, this means a perfect room geometry can
produce exact radial distances before and after motion. Those examples train
the heat-map reader before the robot sees noisy hardware.

The ideal environments should also have notebook sandboxes. Notebooks are for
play: moving the robot, dragging walls, changing danger thresholds, watching EMA
trials, visualizing heat maps, and inspecting where slip opportunities appear.

## Component Telemetry

Every component should expose the same telemetry shape so visuals, monitoring,
replay, notebooks, and LLM exception feeds can use the system without bespoke
adapters.

The common REST shape is:

```text
GET /health
GET /telemetry/current
GET /telemetry/history?limit=100
GET /telemetry/schema
```

The current snapshot reports the component's admitted mark:

```json
{
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

This endpoint is for telemetry, not control. It gives the system and the human
operator the same readable ledger surface.

### Noisy Simulation

Noisy simulation comes after ideal simulation. It corrupts the clean world with
calibration drift, occlusion, sensor noise, lighting changes, latency, actuator
error, friction variation, and partial observability.

The purpose is transfer:

```text
ideal distinction -> noisy heat map -> robust distinction
```

This is where the learner discovers which distinctions survive calibration
change and which ones were artifacts of a perfect world.

Noisy simulation can label false salience caused by noise or calibration change.

### Robot Adaptation

The physical robot is the third training regime. It uses real sensors and real
residue, but should inherit priors from both ideal and noisy simulation.

### Online Backprop

On the robot, the backprop loop can run inline after each real action:

```text
prediction -> action -> sensor residue -> heat-map comparison -> graph update
           -> loss/reward -> small online update
```

The online update should be conservative. Its job is adaptation: calibrating to
the current robot, current lighting, current floor, current camera, current
friction, and current sensor noise.

### Sleep Replay

At the end of a run, the system enters "sleep": a semi-informed replay of the
day's append-only ledger.

Sleep replay should sample:

- high-surprise transitions;
- failures;
- near-threshold non-crossings;
- successful threshold crossings;
- contradicted categories;
- unresolved gaps;
- rare sensor states;
- policy choices that produced large score deltas.

During sleep, the learner can backprop more aggressively because it is not in
the real-time control path. The graph provides the replay index: it can ask for
all failures, all slip opportunities, all high-strain events, all unresolved
visual hypotheses, or all transitions involving a particular category.

Sleep and model storage live on the Mac Studio host. The robot queries local
services there:

- LM Studio for in-house LLM policy selection and exception review;
- a PyTorch-enabled REST service for heat-map reader inference, online training
  updates, and sleep replay.

At night, the robot hands the day's ledger to the host and starts a sleep replay
job. The host stores the models, runs heavier training, and returns new model
versions. The robot keeps the safety gates local.

### Learned Heat-Map Reader

The heat-map reader should learn a function like:

```text
(before_heatmap, after_heatmap, action, graph_context)
  -> distinctions, categories, slip_opportunities, failure hypotheses
```

The learned reader is not replacing the ledger. It proposes distinctions and
categories with evidence. The graph stores them as open, closed, contradicted,
or unresolved.
