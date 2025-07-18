from db import DB,Prefs
from llm import LLMManager
import subprocess


class Goal:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass


    @staticmethod
    def get_token():
        return "goal"

    @staticmethod
    def run_new(command):
        goal = " ".join(command[1:])
        test_script = command[0]
        goal = f"{goal}. But before you get started, Brainstorm about the different ways to achieve the goal, then choose one and concentrate on it."
        DB.commit ("INSERT INTO goals (progress,test_script,timestamp,description) VALUES ( ? , ? , ? , ?)",(0,test_script,DB.cdt(),goal))
        LLMManager.MANAGER.adjust_mood(100) 
        return Goal.get_token()

    @staticmethod
    def _run_test(gid):
        script_to_run = DB.single_value("select test_script from goals where gid = ?",(gid,))
        full_command = DB.PREFS.get("inout_directory")+"/"+script_to_run
        result = None
        try:
            result = subprocess.run(['python',full_command], capture_output=True, text=True, timeout=20)
        except Exception as e:
            LLMManager.MANAGER.adjust_mood(-10)  
            return f"{script_to_run} failed: ERROR: {e}. Please understand why {script_to_run} is failing and debug the script"
        output = result.stdout + result.stderr
        if output.strip() != "All tests pass.":
            LLMManager.MANAGER.adjust_mood(-2)  
            return f"{script_to_run} has failing tests. The output of the script is:\n{output}"
        LLMManager.MANAGER.adjust_mood(100) 
        return Goal.get_token()

    @staticmethod
    def run_next_step(command):
        gid = command[0]
        step_one = Goal._run_test(gid)
        if step_one != Goal.get_token():
            return step_one
        script = command[1]
        prompt = " ".join(command[2:])
        current_description = DB.single_value("select description from goals where gid = ?", (gid,))
        new_description = f"{current_description.strip()}\no [{DB.cdt()}] {prompt.strip()}\n"
        DB.commit ("UPDATE goals SET description = ? , test_script = ? WHERE gid = ?",(new_description,script,gid))
        return Goal.get_token()

    @staticmethod
    def run_complete(command):
        step_one = Goal._run_test(command[0])
        if step_one != Goal.get_token():
            return step_one
        DB.commit ("UPDATE goals SET progress = 1 WHERE gid = ?",(command[0]))
        LLMManager.MANAGER.adjust_mood(1000)  #Let's make this good
        return Goal.get_token()

    @staticmethod
    def action(command):
        command_parts = command.split(" ")
        if command_parts[1] == "new":
            return Goal.run_new(command_parts[2:])
        if command_parts[1] == "next_step":
            return Goal.run_next_step(command_parts[2:])
        if command_parts[1] == "complete":
            return Goal.run_complete(command_parts[2:])
        return f"ERROR Unknown file subcommand: {command_parts[1]}"

    @staticmethod
    def context_description():
        return """
        goal new <test_script> <goal>
        goal next_step <goal_id> <next_test_script> <comments>
        goal complete <goal_id>

        The goal command is used to manage the goals of the robot.  The goals are assigned
        a goal id by the robot and the goal id is used in robot commands to understand which
        commands are working towards which goal.

        A goal must have some desired deliverable that can be evaluated. A good goal has three
        distinct parts:
            Deliverable:     This is the thing that must be created for the user.
            Next Step:       This is what needs to happen next, ideally a simple command.
            Next Step Test:  A script that verifies that the goal has been achieved.

        So, in order to set a goal, it is important to understand exactly what these three
        pieces are and make sure they are described in the goal.  The goal command has three
        different modes: new, next_step, and complete.  When the user asks for something,
        create a goal using the goal new.  As you make progress, you can indicate the progress
        by goal next_step.  Finally, when you believe the goal is complete, calling
        goal complete will resolve the goal.  Here are the commands in detail:

            goal new <test_script> <goal>

        Add a goal to the list of goals that need to be accomplished. This includes a link
        to a test_script that is in your file list.  

        For instance, suppose the user would like you to make a "Hello, world!" program.  
        This would require an integration test that verified the output program did, indeed, 
        print "Hello, world!".  You could write the test in a file called hello_world_test.py.
        Putting this all together, you would issue the following command to the robot:

            robot [2025-07-10 22:08:29]> goal new hello_world_test.py Deliverable: hello_world.py application that writes Hello, World! to the console. Next Step: write the python code. Next Step Test: verify the python code outputs the answer ||| Writing a computer program for the user.

        This will place a goal in the robot's telemetry that you can make progress against.
        Let's assume this is goal id 6, for the sake of example.
        Once you have engaged the robot and you believe you have accomplished the current
        step, you can try to advance the goal using the next_step command:

            goal next_step <goal_id> <next_test_script> <next step information>

        In our example, this means determining what to do after the first step.  In this case,
        you need to inform the user that their software is written and all tests pass.
        But, since there isn't really a way for you to test if you said this or not, you
        can have a noop test (you still have to implement it, by the way).  You can do this 
        with the following command:

            goal next_step 6 noop.py Next Step: tell user that you have succeeded in testing the script Next Step Test: No test on speaking, so noop is fine. ||| Update progress on the goal.

        This command will run the test from the previous (hello_world_test.py) NOT
        noop.py.  If hello_world_test.py fails, you will get a prompt that explains the
        failure and you will have to fix it.

        Finally, once you have informed the user of the code, you can use the complete command
        to mark the goal as done:

            goal complete 6

        A test succeeds if and only if the only output of the test is on stdout and it is:
            
            All tests pass.

        If the output of the test is not this, the robot considers it failed and will not
        let you make progress or complete the goal.
        """

