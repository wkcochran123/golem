# Welcome to the Goal Oriented Logic and Environment Manipulator.

This environment helps explore what happens when a large language
model convinces itself to do something in real life.

Even if you are very familiar with LLMs, this little algorithm can
feel rather spooky.

golem is two separate systems, a robot and a heavily modified LLM
host.  The robot without the modified LLM host will still iterate
and solve problems, but it cannot learn how to get better.

The heavily modified LLM host is a bit of a tangle and getting that
started might take a bit of a lift.  However, the robot can get
started very easily.

## Quickstart for the golem robot

For those eager to watch a robot build a tool and use it, golem comes somewhat
ready to go out of the package, all you need is access to an LLM
host that can interact with the OpenAI /v1/chat/completions API.

From the `python/` directory, execute the following three commands
to start the golem:

1. `python golem.py --reset` This will create all the databases and
directories necessary to run the robot.  This is handy to reset
the golem should it become stuck.  This wipes memories, state,
and all prefs _except_ the location of the /v1/chat/completions.
It will interactively ask for all prefs it needs.  Only the URL
for the endpoint is missing an intelligent default.  Pressing
enter will get something working.

2. `python golem.py --prompt "seed prompt"`  This step isn't
technially necessary to get started, but this is one method of
interacting with the robot.  This will queue your prompt for
processing.

3. `python golem.py --start`  Finally, start the golem up. This
has fairly chatty output so you can watch it do some things.

4. `python ctrl.py` (optional) In another terminal, you can
start a primitive command and control flask application.
