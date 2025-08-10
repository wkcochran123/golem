from db import DB,Prefs
from llm import LLMManager
from context import ContextManager
import subprocess
import os


class Goal:
    """
    GOAL

    The goal management system for the robot.  This implements a test-based step-based iteration to move
    the goal to completion.
    """

    def __init__(self):
        pass


    @staticmethod
    def get_token():
        return "goal"

    @staticmethod
    def run_new(command):
        goal = " ".join(command[0:])
        goal = f"{goal}. But before you get started, Brainstorm about the different ways to achieve the goal, then choose one and concentrate on it."
        DB.commit ("INSERT INTO goals (progress,timestamp,description) VALUES ( ? , ? , ?)",(0,DB.cdt(),goal))
        LLMManager.MANAGER.adjust_mood(100) 
        return Goal.get_token()

    @staticmethod
    def _run_test(gid,script_to_run):
#        dir_cache = os.getcwd();
#        full_command = DB.PREFS.get("inout directory")+"/"+script_to_run
#        result = None
#        try:
#            result = subprocess.run(['python',full_command], capture_output=True, text=True, timeout=20)
#        except Exception as e:
#            LLMManager.MANAGER.adjust_mood(-10)  
#            os.chdir(dir_cache);
#            return f"{script_to_run} failed: ERROR: {e}. Please understand why {script_to_run} is failing and debug the script"
#        output = result.stdout + result.stderr
#        if output.strip() != "All tests pass.":
#            LLMManager.MANAGER.adjust_mood(-2)  
#            os.chdir(dir_cache);
#            return f"{script_to_run} has failing tests. The output of the script is:\n{output}"
#        LLMManager.MANAGER.adjust_mood(100) 
#        os.chdir(dir_cache);
        return Goal.get_token()

    @staticmethod
    def run_next_step(command):
        gid = command[0]
        test_script = command[1]
        step_one = Goal._run_test(gid,test_script)
        if step_one != Goal.get_token():
            return step_one
        prompt = " ".join(command[2:])

        current_description = DB.single_value("SELECT description FROM goals WHERE gid = ?",(gid,))
        full_command = DB.PREFS.get("inout directory")+"/"+test_script
        try:
            with open(full_command, "r", encoding="utf-8") as f:
                script_text = f.read()
        except Exception as e:
            LLMManager.MANAGER.adjust_mood(-20)
            return f"ERROR: Failed to open {full_command}\n {e}"

        oneshot_prompt = f"Does the following:\n{script_text}\n demonstrate the accompilshment of the next step in the goal:\n{current_description}\n\nPlease start your response with yes or no followed by a numeric grade from 0-100 followed by your reasoning."
        response = LLMManager.MANAGER.send_prompt(oneshot_prompt,LLMManager.DEFAULT_MODEL,ContextManager.MANAGER.BLANK_CONTEXT).strip()
        words = response.split(" ")
        if words[0].upper() == "YES":
            LLMManager.MANAGER.adjust_mood(1000)
            progress = DB.single_value("select progress from goals where gid = ?", (gid,))
            description = DB.single_value("select description from goals where gid = ?", (gid,))


            DB.commit("update goals set progress = ? where gid = ?", (progress + 0.001 , gid))
            DB.commit("update goals set description = ? where gid = ?", (f"{description}\n{prompt}", gid))
            return Goal.get_token()

        LLMManager.MANAGER.adjust_mood(-20)
        result = " ".join(words[2:])
        return result

    @staticmethod
    def run_complete(command):
        gid = command[0]
        test_script = command[1]
        step_one = Goal._run_test(gid,test_script)
        if step_one != Goal.get_token():
            return step_one
        prompt = " ".join(command[2:])

        current_description = DB.single_value("SELECT description FROM goals WHERE gid = ?",(gid,))
        full_command = DB.PREFS.get("inout directory")+"/"+test_script
        try:
            with open(full_command, "r", encoding="utf-8") as f:
                script_text = f.read()
        except Exception as e:
            return f"ERROR: Failed to open {full_command}\n {e}"

        oneshot_prompt = f"Does the following:\n{script_text}\n demonstrate the accompilshment of the next step in the goal:\n{current_description}\n\nPlease start your response with yes or no followed by a numeric grade from 0-100 followed by your reasoning."
        response = LLMManager.MANAGER.send_prompt(oneshot_prompt,LLMManager.DEFAULT_MODEL,ContextManager.MANAGER.BLANK_CONTEXT).strip()
        words = response.strip().split(" ")
        print(words)
        if words[0].upper() == "YES":
#            LLMManager.MANAGER.adjust_mood(1000*float(words[1])**(1.1))
            DB.commit("update goals set progress = 1.0 where gid = ?", (gid,))
            return Goal.get_token()

        LLMManager.MANAGER.adjust_mood(-20)
        result = " ".join(words[2:])
        return result

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
        goal new <goal>
        goal next_step <goal_id> <test_script.py> <comments>
        goal complete <goal_id> <test_script.py> 

        The goal command is used to manage the goals of the robot.  The goals are assigned
        a goal id by the robot and the goal id is used in robot commands to understand which
        commands are working towards which goal.

        A goal must have some desired deliverable that can be evaluated. A good goal has two
        distinct parts:
            Deliverable:     This is the thing that must be created for the user.
            Next Step:       This is what needs to happen next, ideally a simple command.

        So, in order to set a goal, it is important to understand exactly what these
        pieces are and make sure they are described in the goal.  The goal command has three
        different modes: new, next_step, and complete.  When the user asks for something,
        create a goal using the goal new.  As you make progress, you can indicate the progress
        by goal next_step.  Finally, when you believe the goal is complete, calling
        goal complete will resolve the goal.  Here are the commands in detail:

            goal new <goal>

        Add a goal to the list of goals that need to be accomplished. 

        Once you have engaged the robot and you believe you have accomplished the current
        step, you can try to advance the goal using the next_step command:

            goal next_step <goal_id> <text file with proof> <complete description of next step>

        To advance the goal, simply provide a text file that demonstrates that you have accomplished
        the current step and a description of the next step that must be accomplished. 


        Finally, once you have informed the user of the code, you can use the complete command
        to mark the goal as done:

            goal complete 6 <text file with proof>
        """

