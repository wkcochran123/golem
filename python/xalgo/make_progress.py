from db import DB
from command import CommandManager
import random

class MakeProgress:

    GOAL_PROGRESS = "Look at the robot console and understand how the robot has responded to your commands.  If you see errors, fix them if they have not already been fixed.  Look at the goals, the console shows progress towards goals.  If the console is not making progress towards the goal, determine which command at your disposal will make progress toward that goal."

    @staticmethod
    def get_token():
        return "make_progress"

    @staticmethod
    def prompt_in (prompt,model,context):
        open_prompts = DB.single_value("select count(*) from stimuli where sid not in (select sid from response)")
        available_cmds = "\nAvailable commands to run on the robot: " + CommandManager.MANAGER.get_commands()
        if open_prompts < 1:
            open_goal_count = DB.single_value("select count(*) from goals where progress < 1.0")
            if open_goal_count > 0:
                DB.queue_prompt(MakeProgress.GOAL_PROGRESS + available_cmds)
            if open_goal_count > 1:
                if random.random() < 0.1:
                    DB.queue_prompt("Choose a different goal to work on for awhile." + available_cmds)
        return (prompt,model,context)


    @staticmethod
    def response_out(prompt,response,context):
        return (prompt,response,context)

    @staticmethod
    def command_out(prompt,response,output,context):
        pass
