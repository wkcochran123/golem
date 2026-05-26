# Welcome to the Goal Oriented Logic and Environment Manipulator.

This environment helps explore what happens when a large language
model convinces itself to do something in real life.

Even if you are very familiar with LLMs, this little algorithm can
feel rather spooky.

golem is two separate systems: a robot runtime and an AI host.  The
robot without the AI host will still iterate and solve problems, but
it cannot learn how to get better.

The current hardware plan keeps the AI infrastructure on the Mac Studio
and runs the Linux robot infrastructure inside an Ubuntu VM.  The Ubuntu
side owns builds, sensor data, logs, local validation, and all actuation.
The Mac Studio side owns RYOT, model hosts, GPU-backed inference, and the
small REST proxy used for AI calls.

The AI boundary is intentionally narrow: AI services may propose normalized
threshold values in the range `[0.0, 1.0]`.  They may not send motor commands
or directly control hardware.  The Ubuntu robot runtime validates threshold
names, ranges, step size, cooldowns, TTL, and rollback before accepting any
proposal.

## Quickstart for the golem robot

For those eager to watch a robot build a tool and use it, golem comes somewhat
ready to go out of the package.  The legacy path only needs access to an LLM
host that can interact with the OpenAI /v1/chat/completions API.

From the `python/` directory, execute the following three commands
to start the golem:

1. `python golem.py --reset` This will create all the databases and
directories necessary to run the robot.  This is handy to reset
the golem should it become stuck.  This wipes memories, state,
and all prefs _except_ the location of the /v1/chat/completions.
It will interactively ask for all prefs it needs.  Only the URL
for the endpoint is missing an intelligent default. The URL should be of the form http://<addr>:<port>. :<port> defaults to 80
Pressing enter will get something working.

2. `python golem.py --prompt "seed prompt"`  This step isn't
technially necessary to get started, but this is one method of
interacting with the robot.  This will queue your prompt for
processing.

3. `python golem.py --start`  Finally, start the golem up. This
has fairly chatty output so you can watch it do some things.

4. `python ctrl.py` (optional) In another terminal, you can
start a primitive command and control flask application.

For the current Mac Studio architecture, prefer an AI host where token or
posit selection can be rewired directly, such as an MLX/`mlx-lm` or
Transformers-based generation loop.  The legacy
[modified llama.cpp host](https://github.com/wkcochran123/golem_llama.cpp)
captures the original experiment, but the active design treats `llama.cpp`
as too rigid and timing-sensitive for selector research unless the operator
explicitly chooses it for a lane.
