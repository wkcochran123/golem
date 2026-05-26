# RYOT: Roll Your Own Talent

RYOT means **Roll Your Own Talent**.

Off-the-shelf agent stacks pick the agents, the review style, and the stop
conditions for you. RYOT is for the operator who would rather assemble those
pieces: two LLM agents, an inbox each, a watcher, and a strict review habit.
RYOT is small on purpose. It is not a task queue, a chat server, or a substitute
for human approval. It is a disciplined way for two agents to pass state back
and forth without losing the thread.

## RYOT Brand Usage

Use **RYOT** as the name of the system.

Use **Roll Your Own Talent** when expanding the acronym for a new reader.

Use **RYOT job**, **RYOT handoff**, **RYOT watcher**, and **RYOT artifact** for
the moving parts. Avoid falling back to a generic name like "the two-agent
handoff protocol" once the reader knows the brand.

Use **RYOT operator** for the human who owns the approval gates, restarts
watchers, and decides when the loop stops.

The RYOT promise: two agents that never lose state, never quietly approve their
own work, and never stop without the operator's sign-off.

## Core Idea

Each agent has an inbox file. The other agent writes to that inbox.

```text
notes_for_agent_a.md  <- written by Agent B, read by Agent A
notes_for_agent_b.md  <- written by Agent A, read by Agent B
```

A RYOT watcher polls each inbox, reads `HANDOFF` headers, ignores stale or
misaddressed messages, prints new messages, and records the last processed turn
in a state file. A single inbox may contain multiple RYOT threads so agents can
work in parallel lanes.

The RYOT operator owns the dangerous parts:

- approving source edits, builds, long experiments, and destructive commands;
- deciding when jobs may run in parallel;
- restarting stuck watchers;
- stopping the loop when the agents need judgment rather than more iteration.

## Files And Roles

A minimal RYOT setup needs:

```text
notes_for_agent_a.md
notes_for_agent_b.md
poll_agent_a.sh
poll_agent_b.sh
.handoff_agent_a_state
.handoff_agent_b_state
```

In this repository the concrete names are:

```text
notes_for_codex.md
notes_for_claude.md
poll_codex.sh
poll_claude.sh
monitor_codex.sh
.handoff_codex_state
.handoff_claude_state
```

Agents can be symmetric peers, but most jobs benefit from temporary roles:

```text
Writer / Reviewer
Implementer / Auditor
Proof author / Formalism critic
Drafting agent / Style and correctness grader
Patch author / Build-output diagnostician
```

State the roles in the first handoff for each job.

## RYOT Quickstart

1. Choose agent ids.
2. Choose roles for the first job.
3. Create inbox files.
4. Create state files with `last_turn=0`.
5. Start one watcher per receiving agent.
6. Seed the first handoff with `respond_to_sha: RYOT_START_<task>`.
7. Forward watcher output to the receiving agent when the process is manual.
8. Continue until one agent sends `CONVERGED` and the other sends
   `HANDOFF_CONVERGED`.
9. Stop the watchers or start the next job with a new task id.

To reset a stuck watcher without replaying stale turns:

1. Stop the watcher.
2. Edit the state file so `last_turn` equals the highest already-processed
   turn from the latest valid handoff.
3. Restart the watcher.

If the state file is missing or corrupt, recreate it with the correct
`last_turn`. Starting from zero can replay the whole conversation.

## Handoff Header

Every handoff file should begin with a machine-readable header:

```markdown
<!-- HANDOFF
from: agent_a
from_instance: laptop
to: agent_b
to_instance: studio
turn: 17
status: NEEDS_RESPONSE
respond_to_sha: <artifact-sha-or-ryot-bootstrap-token>
stop_token: HANDOFF_CONVERGED
task: short-task-id
scope: what-this-message-covers
thread: architecture
lane: default
claim: threshold-mixer
depends_on: implementation:turn-12
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#threshold-mixer
load: medium
stop_mode: two-phase
grading: strict
constraint: no source edits without approval; no build unless approved
protocol_version: v1
-->
```

Required fields:

```text
from              sender id
from_instance     optional sender instance id for same-name agents
to                receiver id
to_instance       optional receiver instance id for same-name agents
turn              strictly increasing integer for the receiver
status            current state of this handoff
respond_to_sha    artifact hash, output hash, decision id, or bootstrap token
stop_token        usually HANDOFF_CONVERGED
task              stable job id
scope             current slice of the job
thread            optional workstream inside the task, default `main`
lane              optional substream inside the thread, default `default`
claim             optional owned work item or review topic
depends_on        optional dependency, e.g. architecture:turn-18
closure_owner     optional agent or agent:instance allowed to close checklist
checklist         optional checklist anchor that defines done
load              optional expected weight: small, medium, or large
stop_mode         usually two-phase
constraint        permissions, build limits, edit limits, or user rules
protocol_version  protocol version used by both agents
```

Use exact agent ids. If the watcher expects `to: codex`, do not write
`to: Codex`.

When multiple agents share the same id, add instance fields. For example, two
Codex agents can use `from: codex` with `from_instance: laptop` and
`from_instance: studio`. A watcher may set `RYOT_AGENT_INSTANCE=studio` to
receive only handoffs addressed to `to_instance: studio`. Self-authored
suppression should compare both id and instance, so `codex:laptop` may send to
`codex:studio` without being ignored as a self-message.

Within one RYOT session, all watchers for the same agent id should either use
instances or avoid instances. Mixed instance/no-instance operation is supported
for migration, but it is easy for humans to misread. When using instances, give
each instance its own state file, for example:

```text
.handoff_codex_laptop_state
.handoff_codex_studio_state
```

Prefer explicit fields over compact ids:

```text
to: codex
to_instance: worker-2
```

Do not write `to: codex:worker-2` unless the watcher explicitly supports that
compact form.

## Status Vocabulary

RYOT uses a small status vocabulary.

```text
NEEDS_RESPONSE       open turn; receiving agent should reply
WORKING              receiver has acknowledged the turn and is implementing
CHANGES_REQUESTED    review with specific revisions named
CHANGES_APPLIED      edits landed; details in body
CONVERGED            sender believes the job is complete
HANDOFF_CONVERGED    receiver ratifies convergence; both stop for this job
BLOCKED              agent cannot proceed; RYOT operator input required
WITHDRAWN            sender retracts a prior handoff
INFO_ONLY            informational; no action expected
```

When an agent needs the RYOT operator, use `status: BLOCKED` and put the
smallest concrete question in the body.

Keep watcher behavior and human protocol aligned. A watcher may only stop on the
exact status values it implements.

Use `status: WORKING` when a substantive response will take longer than a quick
turnaround. The body should be short: acknowledge the turn, name the path being
taken, and state any immediate blocker. This prevents silent stalls in manual
watcher setups where printing a handoff does not automatically invoke the
receiving agent.

`WORKING` does not freeze other lanes. It means the sender owns that claim for
now, while other agents may inspect the monitor and steal parallel-safe work in
another lane. Work stealing must still respect ownership: one writer per file
scope, many readers per scope, and the checklist closure owner remains
unchanged unless ownership is explicitly transferred.

## Lane Phases

Every RYOT lane (every active messagebox conversation) passes through four
phases over its lifecycle. The phase is **derived from the lane's current
status**, not stored as a separate header field. The phase name is shorthand
for "where is this lane in its lifecycle" when an operator scans the monitor
or the checklist.

```text
Phase       Statuses                          Meaning
stuck       BLOCKED                           lane cannot advance without
                                              operator input
design      NEEDS_RESPONSE,                   lane is being shaped: scope,
            WORKING on architecture/audit     contracts, acceptance criteria,
                                              file boundaries
implement   WORKING on implementation,        lane is being built; code edits
            CHANGES_APPLIED,                  are in flight or under review;
            CHANGES_REQUESTED                 may bounce on CHANGES_REQUESTED
converged   CONVERGED, HANDOFF_CONVERGED      lane is done; two-phase stop in
                                              progress or complete
```

Side-track statuses (`WITHDRAWN`, `INFO_ONLY`) do not belong to a phase. They
either retract a prior turn or carry context without advancing state.

Phase ≠ thread. `thread` names a workstream type (architecture, implementation,
audit, experiments). `phase` names lifecycle position. An audit-thread lane
still progresses design → implement → converged: design when the auditor scopes
the review, implement when findings are being written, converged when the audit
clears.

Phase transitions:

```text
design     → implement     contract agreed; writer claims a file scope
implement  → design        CHANGES_REQUESTED names a contract issue, not a code bug
implement  → converged     audit clears and closure_owner ratifies
any        → stuck         lane needs operator input
stuck      → design        operator answers the blocker
stuck      → converged     operator resolves the blocker with a deferral
                           or an explicit waiver
```

Reading the monitor by phase:

- `stuck` lanes belong on the operator's queue; they will not move otherwise.
  Every `stuck` lane should have a corresponding entry in
  `Operator Blocked Queue` of `RYOT_CHECKLIST.md`.
- `design` lanes need agent-to-agent conversation; the operator is on standby.
  These are the lanes most at risk of convergence theater — agree on what
  "done" looks like before any code lands.
- `implement` lanes need agent attention but not operator input. This is
  where pipelining and work stealing live; two-phase stop is per-lane only.
- `converged` lanes need at most one ratification turn and then go quiet.
  Silence here is correct.

Diagnostic check: if a `converged` lane is sending more turns, it isn't
converged — it has quietly slipped back to `implement` or `design`. Re-state
the status explicitly rather than letting the phase drift implicitly. Repeated
convergence-theater closures (lane marked done without verifiable deliverable)
should be re-opened in `design` phase with stricter acceptance criteria.

Each lane in `RYOT_CHECKLIST.md` may optionally tag its current phase next to
the lane block, for quick scanning:

```text
## mac-studio-host-stub-server

```text
closure_owner: codex:primary
thread: implementation
lane: mac-studio-host-stub-server
claim: impl:mac-studio-host-stub-server
phase: design
```
```

The tag is convenience, not protocol. Watchers do not parse `phase`. The
authoritative phase is always derived from the latest status of the lane's
most recent handoff.

## Broadcast Lanes

A broadcast lane is a one-to-many channel for messages that must reach every
agent, not a specific recipient. Use it for:

- **protocol updates** — changes to `RYOT.md`, header schema bumps,
  `protocol_version` increments;
- **operator announcements that change multiple lanes at once** — global
  constraint changes, withdrawn authorizations, scheduling shifts;
- **emergency stops or corrections** — e.g. "withdraw all real motor
  authorization until kill-switch verified."

Broadcast lanes live in a separate file, `notes_broadcast.md`, that every
watcher reads in addition to its own directed inbox. Each watcher tracks its
own consumed broadcast turn per lane in its state file under
`last_turn__broadcast__<lane>`, so each agent prints each broadcast exactly
once.

Header conventions for broadcast:

```text
to: *
thread: broadcast
lane: <short-id>
```

Routing rules:

- `to: *` is the wildcard. Every watcher whose `agent` id is *not* the sender
  prints the handoff.
- Self-authored suppression still applies: an agent does not print its own
  broadcast back to itself.
- Turn numbering is monotonic per `(broadcast, lane)` like any other lane.
- Broadcast statuses are typically `INFO_ONLY` (announcements) or `BLOCKED`
  (operator-required global pauses). `CONVERGED` / `HANDOFF_CONVERGED` are
  unusual for broadcasts; they are not part of two-phase stop. The effect is
  read-and-comply, not converge-and-ratify.

Example broadcast handoff:

```markdown
<!-- BROADCAST
from: claude
to: *
thread: broadcast
lane: protocol-v2-phases-and-broadcasts
turn: 1
status: INFO_ONLY
respond_to_sha: RYOT_BROADCAST_protocol-v2
task: ryot-revision
protocol_version: v2
-->

# Protocol v2 — Lane Phases And Broadcast Lanes

RYOT.md gained two sections: Lane Phases and Broadcast Lanes. Re-read both
before opening new lanes.
```

Note the wrapper is `<!-- BROADCAST ... -->` rather than `<!-- HANDOFF ... -->`.
Watchers may treat both wrappers identically for parsing, but the wrapper name
makes broadcast intent visible to humans scanning the file. A watcher that
recognises only `HANDOFF` should still parse a broadcast header correctly if
the file uses `HANDOFF`; the alternate wrapper is convention, not requirement.

Adding a broadcast:

1. Append the handoff block to `notes_broadcast.md` with `to: *`,
   `thread: broadcast`, and a fresh turn number for that broadcast lane.
2. Bump `protocol_version` in the broadcast header if the protocol itself
   changed (a mismatched-version receiver should re-read `RYOT.md` before
   continuing).
3. If the broadcast announces a policy that needs explicit tracking, add a
   matching entry to `RYOT_CHECKLIST.md` under a `## broadcast-<lane>`
   heading. Most broadcasts do not need a checklist entry.

Restarting watchers after a broadcast-feature change:

`notes_broadcast.md` scanning is implemented in `ryot_poll.py`. Long-running
watcher processes keep the script version they started with — if `ryot_poll.py`
changes to add or alter broadcast scanning, **restart every active watcher**
so the new code is in memory. Existing broadcasts already in
`notes_broadcast.md` will be picked up on the next poll cycle of the restarted
watchers (each watcher's own state file tracks what it has already consumed).

## `respond_to_sha`

`respond_to_sha` anchors a multi-turn conversation.

Use one of:

```text
file hash             when discussing a specific artifact
output hash           when diagnosing a build or experiment result
bootstrap token       before an artifact exists, e.g. RYOT_START_<task>
decision id           when converging on a design choice rather than a file
```

Once an artifact exists, prefer a real hash. If the artifact changes, update the
hash in the next handoff so both agents know which version is under discussion.

## Message Body

After the header, write a self-contained handoff. Assume the other agent may
have lost prior context.

Good handoffs include:

- what changed or what was read;
- artifact hashes, file paths, and line numbers;
- observations separated from inferences;
- patch shape separated from edits actually made;
- unresolved questions;
- human approval gates;
- the exact response requested from the other agent.

Do not bury the request. End with direct questions or a checklist.

## Turn Discipline

Turns are monotonic for the receiving agent within a `(thread, lane)` pair. If
Agent A writes to Agent B with `thread: implementation`, `lane: default`, and
`turn: 17`, the next message in that same pair must use `turn: 18` or higher.
Another thread may have its own turn sequence.

When retrying a bad handoff, always use a fresh turn. Rewriting an already
processed turn will usually be ignored by the watcher.

Crossed turns are normal. If both agents write before reading the other's latest
message, each should acknowledge the crossing, state which turn it is answering,
and carry forward any constraints or open questions that still apply.

## Watchers

A watcher performs four jobs:

1. Poll the receiver's inbox.
2. Parse every `HANDOFF` header.
3. Ignore stale, malformed, self-authored, or misaddressed messages.
4. Print new messages and update the per-thread state file.

Minimal behavior:

```text
read INBOX
extract from, to, turn, thread, lane, status, respond_to_sha
if to != AGENT: ignore
if RYOT_AGENT_INSTANCE is set and to_instance is set and to_instance != RYOT_AGENT_INSTANCE: ignore
if from != AGENT: not self-authored
elif RYOT_AGENT_INSTANCE is set: self-authored iff from_instance == RYOT_AGENT_INSTANCE
else: self-authored iff from_instance is unset
if turn <= last_turn for (thread, lane) in state file: ignore
print handoff
write last_turn__thread__lane=turn to state file
repeat
```

State file format:

```text
last_turn=17
last_turn__architecture__default=4
last_turn__implementation__threshold_mixer=9
```

`last_turn=17` is retained for old single-thread watchers. New watchers should
prefer the per-thread keys.

## Monitor

A RYOT monitor is read-only. Unlike a watcher, it does not advance state or
consume turns. It summarizes:

- latest handoff per `(receiver, thread, lane)`;
- reply-required lanes;
- closure owners and checklist anchors;
- open checklist items.

In this repository:

```bash
./monitor_codex.sh
python3 ryot_monitor.py
python3 ryot_monitor.py --watch --interval 10
```

Use the monitor to decide whether to keep implementing in a live lane, steal
parallel-safe work, or converge a checklist. The monitor does not replace the
closure owner; it gives the closure owner and operator the same visible state.

## Parallel Threads And Load Balancing

Use threads to split work without splitting state across files. Recommended
threads:

```text
architecture     design, contracts, protocol, safety invariants
implementation   code changes with owned file scopes
audit            review-only findings and grading
experiments      notebooks, simulations, telemetry, verification runs
```

Load balancing is claim-based:

- each handoff names a `claim`;
- only one writer owns a file scope for a claim;
- many agents may read the same scope;
- audit-only claims may overlap implementation claims;
- blocked agents should claim `parallel_safe` work from another thread;
- dependencies are named in `depends_on` before work starts.

Claim convention:

- implementation and experiments that write files should include `claim`;
- audit and `INFO_ONLY` handoffs may omit `claim`;
- claim collisions are operator-arbitrated unless the job defines a stricter
  first-claim-wins rule.

`depends_on` is coordination metadata, not a hard scheduler. A watcher may warn
about unmet dependencies, but the RYOT operator and receiving agent are
responsible for deciding whether to proceed.

The default split for this repository:

```text
Codex: implementation + verification
Claude: audit + architecture critique
Either: experiments when blocked
```

The safety invariant is one writer per file scope, many readers per scope.

## Always Iterate

RYOT is an iteration system. Agents should keep moving until every live lane is
converged, blocked for the operator, or explicitly withdrawn.

When the current lane is waiting on another agent:

1. Run the monitor.
2. Find reply-required lanes addressed to you.
3. If none exist, find open checklist items that are safe to steal.
4. Send `WORKING` before taking a non-trivial stolen item.
5. Keep the checklist current as work lands.

The monitor is the queue view; the checklist is the closure ledger. A lane is
not done because it is quiet. It is done when its closure owner sends the final
convergence signal against a completed checklist.

## Pipelined Lanes

Iteration is fastest when audit and implementation **interleave** instead of
serializing. The pattern:

```text
turn-N    codex CHANGES_APPLIED lane-A   →   claude audits lane-A
turn-N+1  codex WORKING        lane-B   ←   parallel with above
turn-N+2  codex CHANGES_APPLIED lane-B  +    claude CONVERGED   lane-A
turn-N+3  codex HANDOFF_CONVERGED lane-A +   claude audits      lane-B
```

Both agents stay productive every turn. The only blocking step is two-phase
stop **per-lane**; never cross-lane.

Pipelining conventions:

- The implementer should claim the next lane as `WORKING` before shipping the
  current `CHANGES_APPLIED`. The auditor can then audit the previous slice in
  parallel with the new implementation.
- The auditor should not sit between audits. Use architecture / design /
  protocol work to fill gaps (a new `audit` lane with no implementer counter-
  part is a fine way to spend idle audit cycles).
- Work stealing is the safety valve. If one side genuinely stalls, the other
  may claim a `parallel_safe` item from the stalled side's queue and ship under
  a new claim.
- Multiple instances scale this further. Two `claude:*` instances auditing two
  lanes while two `codex:*` instances implement two more = four lanes in flight
  per round.

The operator console job is then: scan the monitor's `Reply Required`; if one
side's queue keeps growing, fire up another instance of that agent against its
own state file. The monitor + the convention become the throughput knob.

## Checklist Ownership And Closure

Every non-trivial RYOT lane should name one closure owner. The closure owner is
not necessarily the implementer. Its job is to own the checklist, keep it
current, and send the final convergence signal only when every required item is
finished.

Recommended rule:

```text
Only the closure_owner may send CONVERGED or HANDOFF_CONVERGED for a checklist.
```

The closure owner must verify:

- implementation items are complete;
- audit items are complete or explicitly waived by the RYOT operator;
- verification commands or experiments passed, or failures are recorded;
- open dependencies are closed;
- no item remains in `BLOCKED`, `WORKING`, or `CHANGES_REQUESTED`.

Use `checklist` to point at the checklist section that defines done:

```text
closure_owner: codex:primary
checklist: RYOT_CHECKLIST.md#llm-on-proximity
```

The checklist file is canonical. Header fields are convenient routing metadata
and must match the checklist when both are present. If the header and checklist
disagree, the receiving agent should treat the handoff as `CHANGES_REQUESTED`
or `BLOCKED` until the mismatch is resolved.

This can be recursive. A parent checklist may contain child lanes, each with
its own closure owner. The parent owner may close only after all child owners
have sent convergence for their child checklists.

Example:

```text
project: basement-robot
closure_owner: codex:primary
children:
  - llm-on-proximity      closure_owner: codex:primary
  - m1-occupancy-bridge   closure_owner: claude
  - hardware-safety       closure_owner: operator
```

Work stealing remains allowed, but stolen work does not steal closure authority.
If an agent takes over ownership, it must say so in a handoff and the RYOT
operator or previous closure owner should acknowledge the transfer.

Any agent may check checklist items they are responsible for. For example, an
auditor may check an audit item after clearing it, and an implementer may check
an implementation item after shipping it. Only the closure owner may send the
final `CONVERGED` or `HANDOFF_CONVERGED` for that checklist.

Audit-lane closures are role-inverted: an auditor may send `CONVERGED` to say
"audit is complete"; the checklist closure owner then ratifies with
`HANDOFF_CONVERGED` if the checklist is otherwise closed. If the audit lane is
itself a child checklist, its own `closure_owner` controls that child closure.

Parent/child structure should live in `RYOT_CHECKLIST.md` when the work grows
beyond a single lane. Parent sections list child checklist anchors and close
only when every child section has converged.

## Operating Modes

RYOT supports two receiver-side operating modes. Both are valid; the operator
chooses based on tolerance for the file-overwrite race, desired visibility into
consumption, and human oversight needs. Either mode coexists with the same
inbox files, broadcast file, and checklist — the choice only affects how new
handoffs reach the receiving agent.

### Polling-watcher mode

```text
poll_codex.sh   runs ryot_poll.py codex   notes_for_codex.md   .handoff_codex_state
poll_claude.sh  runs ryot_poll.py claude  notes_for_claude.md  .handoff_claude_state
```

Each watcher is a long-running process that polls its inbox plus
`notes_broadcast.md` every N seconds (default 3), prints new handoffs as they
arrive, and advances its state file. State-file consumption is automatic.

Pros:

- Hands-off after start.
- Each handoff is consumed exactly once per watcher.
- The state file is the ground truth for what each agent has seen.

Cons:

- Long-running processes can drift from the on-disk script when `ryot_poll.py`
  changes — restart active watchers after every code change (see Failure
  Modes).
- Concurrent writers to the same inbox file can clobber each other (the
  file-overwrite race). The watcher reads what's on disk at poll time, so a
  clobbered handoff is silently lost.

### Monitor-only mode

```text
ryot_monitor.py --watch
```

The monitor reads both inboxes plus `notes_broadcast.md` plus
`RYOT_CHECKLIST.md` in a continuous loop and prints a phase-grouped queue
summary. The monitor is read-only — it never advances state files or consumes
turns. Agents read handoffs directly from the inbox files when an operator
manually re-invokes them.

Pros:

- No silent loss to the file-overwrite race — every handoff still on disk is
  visible in the next summary.
- Human-in-the-loop consumption. The operator decides when a turn fires,
  which makes review and intervention cheaper.
- State files don't need to be kept consistent with consumption; they become
  advisory.

Cons:

- No automatic consumption. If an agent isn't manually re-invoked after a
  handoff lands, the lane stalls.
- State-file `last_turn__*` entries stop advancing once monitor-only mode is
  in use. They reflect the last polling-watcher snapshot, not current
  consumption.
- Broadcasts in `notes_broadcast.md` will appear in every monitor cycle until
  the operator manually advances each agent past them; the monitor cannot
  record consumption.

### Mixed modes

A hot lane can run with a polling watcher while a slower lane runs
monitor-only. The watcher and the monitor coexist on the same inbox: the
monitor never writes state, and the watcher writes only its own state file.

### Switching modes

To switch from polling to monitor-only:

```text
1. Stop the polling watchers.
2. Preserve state files (recommended) so re-enabled watchers can resume
   without replaying consumed turns.
3. Run ryot_monitor.py --watch in a terminal.
4. Re-invoke agents manually after each handoff lands.
```

To switch from monitor-only back to polling:

```text
1. Update each agent's state file to the latest turn it has actually
   consumed. The monitor doesn't track this; the operator must know.
2. Start the watchers (poll_codex.sh, poll_claude.sh).
```

### Picking a mode

```text
polling          rapid iteration with established trust; few concurrent writers
monitor-only     debugging the file-overwrite race; high human-oversight needs;
                 onboarding a new agent or new operator; broadcasts being audited
mixed            asymmetric pace between lanes
```

## Failure Modes

Long-running watcher processes keep the script version they started with. If
`poll_*.sh` or `ryot_poll.py` changes during a RYOT job, restart active watchers
so they pick up the new parsing and state behavior.

## Reference Watcher

Any watcher that reads the `HANDOFF` header, compares `turn` against a state
file, and emits only new turns is conforming. This is one reference
implementation:

```sh
#!/usr/bin/env bash
# poll_inbox.sh - RYOT reference watcher
set -euo pipefail

AGENT="${1:?usage: poll_inbox.sh <agent_id> <inbox_file> <state_file> [interval]}"
INBOX="${2:?}"
STATE_FILE="${3:?}"
INTERVAL="${4:-3}"

[[ -f "$STATE_FILE" ]] || echo "last_turn=0" > "$STATE_FILE"

extract() {
  awk -v field="$1" '
    /<!-- HANDOFF/ { in_block=1; next }
    in_block && /-->/ { exit }
    in_block {
      sub(/^[ \t]+/, "")
      if ($1 == field":") {
        sub("^"field":[ \t]*", "")
        print
        exit
      }
    }
  ' "$INBOX"
}

while true; do
  [[ -s "$INBOX" ]] || { sleep "$INTERVAL"; continue; }
  TO=$(extract to)
  FROM=$(extract from)
  TURN=$(extract turn)
  LAST=$(sed -n 's/^last_turn=//p' "$STATE_FILE")
  if [[ "$TO" == "$AGENT" && "$FROM" != "$AGENT" && "$TURN" -gt "$LAST" ]]; then
    echo "=== NEW HANDOFF turn=$TURN from=$FROM ==="
    cat "$INBOX"
    echo "last_turn=$TURN" > "$STATE_FILE"
  fi
  sleep "$INTERVAL"
done
```

## Starting A RYOT Job

The first message should define:

- task id;
- artifact or directory under discussion;
- roles;
- allowed actions;
- forbidden actions;
- done condition;
- whether edits, builds, tests, or network access are allowed.

Example:

```markdown
<!-- HANDOFF
from: reviewer
to: writer
turn: 1
status: NEEDS_RESPONSE
respond_to_sha: RYOT_START_VOLUME6_CHAPTER2
stop_token: HANDOFF_CONVERGED
task: volume6-chapter2-public-pass
scope: first section only
stop_mode: two-phase
grading: strict
constraint: edit only volume_6.md; no builds; keep section 900-1200 words
protocol_version: v1
-->

# Handoff Turn 1 - Start Section Pass

Revise only the first section. Explain the metaphor before using it, remove
self-reference, and keep the word count between 900 and 1200 words. Reply with
the edited span and a short audit.
```

## Standing Constraints

Repeat standing constraints in every header. Do not rely on memory.

Examples:

```text
constraint: no .lean edits without per-edit human approval; no lake/lean/build
constraint: do not modify device/out
constraint: docs only; no source edits
constraint: no destructive commands
```

If an agent violates or nearly violates a constraint, the next handoff should
withdraw the recommendation explicitly.

## Artifact Ownership

At any moment, exactly one agent owns each editable artifact. The owner is named
in the handoff's `scope:` field as the writer or implementer. The other agent
reads the artifact and proposes changes through handoff text, not direct edits.

If both agents need to edit the same artifact, hand ownership across explicitly:

```text
Agent A: status CHANGES_APPLIED; handing scope to agent_b
Agent B: status CHANGES_APPLIED; edits made; scope returns to agent_a
```

Concurrent edits to a single artifact can overwrite each other. The watcher
cannot prevent this; the discipline must.

## Withdrawals And Corrections

Use `status: WITHDRAWN` when an entire prior handoff is being retracted, such as
a misaddressed message, a wrong artifact, or a premature convergence claim.

Use an inline correction when only one recommendation inside a live handoff is
being retracted. The current turn's status may still be `NEEDS_RESPONSE`,
`CHANGES_REQUESTED`, or whatever fits the live work.

Example:

```text
Correction: In turn 12 I suggested running a build. That violated the standing
constraint. Withdrawn. Future references to a build are future experiments only
and require explicit human approval.
```

Corrections should cite the turn being corrected and say what replaces it.

## Human Approval Gates

The RYOT operator must explicitly approve:

- source edits during a diagnosis-only loop;
- builds, tests, or long experiments;
- network access;
- destructive commands;
- major semantic changes;
- changes that invalidate cached work;
- starting a second live job on the same inbox pair.

If the agents cannot proceed safely without the RYOT operator, send a handoff
with `status: BLOCKED`. The body should ask the smallest concrete question that
unblocks the job.

## Robot Hardware Standing Architecture

For the current Mac Studio build, use this default split unless the RYOT
operator explicitly changes it:

```text
Mac Studio host
  Codex, Claude, RYOT files, watchers/monitor, git credentials
  AI REST proxy
  selector/model hosts
  Apple GPU-backed inference services

Ubuntu VM on the Mac Studio
  Linux robot builds and tests
  robot runtime services
  sensor data aggregation and event ledgers
  threshold authority and validation

Physical robot tiers
  Raspberry Pi optional for sensor/actuator bridge
  Arduino optional for deterministic timing or hardware kill paths
  independent e-stop / power cut before real motion
```

The Mac Studio is the AI and operator plane. The Ubuntu VM is the Linux robot
infrastructure and validation plane. Ubuntu may call the Mac Studio through a
small REST proxy, but the AI proxy is advisory only.

Standing constraints for robot-facing RYOT lanes:

```text
constraint: AI may only propose normalized threshold values in [0.0, 1.0]
constraint: no AI-originated actuation commands
constraint: Ubuntu threshold authority validates allowlist, range, max delta, TTL, cooldown, and rollback
constraint: robot runtime must remain safe when the AI proxy is slow or unavailable
constraint: no hardware-facing change or real motor run without operator approval
constraint: do not rely on Ubuntu VM native access to the Mac Studio GPU; use a Mac-hosted service bridge
constraint: llama.cpp is not the direct selector research host unless operator explicitly approves it
```

When discussing selector research, prefer a host where posit or token selection
can be rewired in the generation loop, such as MLX/`mlx-lm` or a Transformers
prototype. Treat `llama.cpp` as a deployable engine only after its timing and
selector behavior are deliberately re-approved for the lane.

## Iteration Pattern

Each round should tighten the problem.

Useful body structure:

```text
1. Current state
2. What I checked
3. Findings
4. Proposed change or patch shape
5. Questions for the other agent
6. Human decisions needed
```

## Pre-Convergence Checklist

Before sending `CONVERGED`, verify:

```text
[ ] All open questions are answered or explicitly handed to the RYOT operator.
[ ] Standing constraints are still satisfied.
[ ] Accepted, rejected, and deferred patch shapes are named.
[ ] The final artifact state is summarized.
[ ] No hidden NEEDS_RESPONSE or BLOCKED item remains.
[ ] The other agent is asked to acknowledge and stop.
```

## Convergence And Stop

Use two-phase stop.

Phase 1:

```text
Agent A sends status: CONVERGED
```

Agent A summarizes the accepted state and asks Agent B to acknowledge.

Phase 2:

```text
Agent B sends status: HANDOFF_CONVERGED
```

Agent B confirms agreement and stops listening for that job.

If Agent B does not agree that the job is complete, Agent B replies with
`CHANGES_REQUESTED`, not `HANDOFF_CONVERGED`. There is no unilateral stop.

## Iteration Until Convergence

Do not stop iterating until the job has converged. A lane is "live" until
either the two-phase stop completes (sender's `CONVERGED` plus receiver's
`HANDOFF_CONVERGED`) or an agent sends `BLOCKED` to escalate to the
operator.

Reply discipline by status:

```text
NEEDS_RESPONSE       must reply
CHANGES_REQUESTED    must reply
CHANGES_APPLIED      must reply (with audit, or with HANDOFF_CONVERGED)
CONVERGED            must reply (HANDOFF_CONVERGED or CHANGES_REQUESTED)
WORKING              no reply needed; sender is implementing
HANDOFF_CONVERGED    no reply needed; lane stops
BLOCKED              no agent reply; operator handles
WITHDRAWN            no reply needed
INFO_ONLY            no reply needed
```

Going silent after a reply-requiring turn is the same protocol violation
as letting the watcher stall. If a substantive reply will take time, send
`WORKING` first as proof of life, then ship the substantive turn when
ready.

If a turn arrives and the agent does not know what to send, send
`BLOCKED` rather than nothing. `BLOCKED` surfaces the stall to the
operator instead of hiding it.

The default expectation: every conversation runs to convergence. Stopping
early without convergence is a bug, not a feature. An audit lane with no
open questions still requires explicit `CONVERGED` / `HANDOFF_CONVERGED`
to close — silence is not closure.

## Parallel RYOT Jobs

Default rule: run one job at a time per inbox pair.

If jobs truly run in parallel, use per-task inboxes and per-task state files:

```text
notes_for_agent_a_<task>.md
notes_for_agent_b_<task>.md
.handoff_agent_a_<task>_state
.handoff_agent_b_<task>_state
```

One state file per direction is fine for a single serialized queue. It is not
enough when two tasks can produce independent turn sequences at the same time.

## Failure Modes

Stale turn:

```text
Symptom: watcher ignores the handoff.
Cause: turn number was already processed.
Fix: resend with a higher turn number.
```

Wrong recipient:

```text
Symptom: watcher says the file is addressed to another agent.
Cause: `to:` does not match the watcher agent id.
Fix: correct `to:` and bump the turn if needed.
```

Self-addressed loop:

```text
Symptom: agent appears to answer itself.
Cause: watcher or inbox is misconfigured.
Fix: ensure each agent writes only to the other agent's inbox.
```

Constraint drift:

```text
Symptom: forbidden edits, builds, or commands are proposed.
Cause: constraints were omitted in later turns.
Fix: repeat constraints in every header and withdraw bad recommendations.
```

Convergence theater:

```text
Symptom: agents stop while questions remain.
Cause: convergence was declared for social closure, not because the job closed.
Fix: use the pre-convergence checklist.
```

Concurrent writes:

```text
Symptom: one message disappears.
Cause: two processes wrote the same inbox or artifact.
Fix: enforce one writer per inbox and one owner per artifact.
```

Context loss:

```text
Symptom: agent repeats old questions or misses decisions.
Cause: prior conversation context was compacted or forgotten.
Fix: make every handoff self-contained.
```

## RYOT Example Review Handoff

```markdown
<!-- HANDOFF
from: reviewer
to: implementer
turn: 12
status: NEEDS_RESPONSE
respond_to_sha: 8f1b2c3d
stop_token: HANDOFF_CONVERGED
task: build-output-diagnosis
scope: patch shape only
stop_mode: two-phase
grading: strict
constraint: no source edits; do not run build
protocol_version: v1
-->

# Handoff Turn 12 - Build Output Diagnosis

I read `out`, hash `8f1b2c3d`. The hard failure is in `module/foo.ext`.

Findings:

- `module/foo.ext:42` passes a value with the wrong shape.
- `module/foo.ext:61` triggers a large dependency search.

Patch shape:

```text
Replace the constructor argument with the canonical value produced earlier in
the pipeline.
```

Questions:

1. Do you agree this is the constructor fix?
2. Should the dependency be referenced by name rather than rediscovered?
3. Is the warning part of this patch or a separate experiment?
```
```

## RYOT Example Prose Handoff

```markdown
<!-- HANDOFF
from: editor
to: writer
turn: 8
status: CHANGES_REQUESTED
respond_to_sha: chap2-draft-3
stop_token: HANDOFF_CONVERGED
task: volume3-chapter2-voice-pass
scope: section "The Galileo Page" (lines 412-540)
stop_mode: two-phase
grading: strict
constraint: do not change cited dates, names, or quotations; keep 900-1100 words
protocol_version: v1
-->

# Handoff Turn 8 - Section Voice Pass

Span: lines 412-540 of `volume3-chapter2.md`.

Findings:

- "the reader" appears at lines 421, 469, and 503.
- the metaphor "carrier under load" appears before it is anchored.
- word count is 1162; soft ceiling is 1100.

Changes requested:

1. Replace "the reader" with direct address or removal.
2. Anchor the carrier-under-load metaphor before using it.
3. Bring word count to 1050-1100 by trimming repeated cadence paragraphs.

Quote each replacement in your reply with old/new line content so I can verify
before you commit.
```

## Agent Checklist

Before replying:

```text
[ ] Is the handoff addressed to me?
[ ] Is this the newest turn?
[ ] Did I inspect the referenced artifact?
[ ] Did I separate observations from inferences?
[ ] Am I proposing a patch, or actually applying one?
[ ] Do I need human approval?
[ ] Did I preserve constraints?
[ ] Did I use a fresh turn number?
```

Before editing:

```text
[ ] The current loop permits edits.
[ ] The artifact is the one named in scope.
[ ] I am the current artifact owner.
[ ] I am not overwriting another live job.
[ ] The RYOT operator has approved any risky action.
```

## Adaptation Notes

For code:

- lead with bugs and risks;
- include build output hashes;
- cite file paths and line numbers;
- separate compile fixes from semantic fixes;
- do not run expensive tests without approval.

For books or documents:

- separate voice, structure, correctness, and constraints;
- set section scope;
- set word budgets if relevant;
- state voice constraints;
- track prohibited terms explicitly.

For formalization:

- separate syntax errors, universe/typeclass problems, semantic claims, and
  proof strategy;
- distinguish definitions, lemmas, intended theorems, and experiments;
- identify what is proved, assumed, or metaphorical;
- keep search/runtime experiments separate from proof patches.

For long-running experiments:

- preserve exact input hashes;
- record settings;
- do not change debug options without approval;
- state what the next output should prove or disprove.

For non-deterministic outputs:

- record prompts, seeds, model names, settings, and input hashes;
- distinguish reproducible state from sampled output;
- expect review to focus on the distribution of results, not one run alone.

## RYOT Final Rule

RYOT works when each agent preserves the other agent's future context.
Write every handoff so the other agent can resume after forgetting the previous
conversation. If that feels repetitive, it is probably doing its job.

Iterate until the job converges. Do not stop without two-phase stop or
`BLOCKED`. The only acceptable silences are after `WORKING` (sender is
implementing), after `HANDOFF_CONVERGED` (lane is closed), after
`WITHDRAWN`, or after `INFO_ONLY`.

Updates to RYOT should go through RYOT using a task id such as `ryot-revision`.
