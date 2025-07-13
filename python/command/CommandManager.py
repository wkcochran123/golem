from .bash_script import BashScript
from .code import Code
from .concentrate import Concentrate
from .download import Download
from .evaluate import Evaluate
from .file import File
from .goal import Goal
from .iterate import Iterate
from .look import Look
from .move import Move
from .noop import Noop
from .brain_storm import BrainStorm
from .python_script import PythonScript
from .speak import Speak

class CommandManager:
    """
    CommandManager

    """


    def __init__ (self):
        self.SUCCESS = "Command executed successfully."
        self.commands = [
                Noop,
                Goal,
#                File,
#                Look,
#                Speak,
#                Move,
                BashScript,
#                PythonScript,
#                Download,
#                Evaluate,
#                BrainStorm,
#                Concentrate,
#                Iterate,
#                Code,
                ]

    def run_command(self,full_command,goal_id):
        command = full_command.strip().split("|||")[0]
        first_word = command.split(" ")[0]
        for cmd in self.commands:
            print (f"Checking {first_word} against {cmd} and {cmd.get_token()}");
            if cmd.get_token() == first_word:
                print (f"Dispatching");
                return cmd.action(command,goal_id)
        return f"ERROR: Unknown command {first_word}"

    def enable_command(self,command):
        if command not in self.commands:
            self.commands.append(command)

    def disable_command(self,command):
        if command in self.commands:
            self.commands = [cmd for cmd in self.commands if cmd != command]

    def get_instructions(self):
        command_list = ""
        for command in self.commands:
            command_list = f"{command_list}\n{command.context_description()}"
        overall_instructions = """
        Robot commands take the form:
            <command> <param1> <param2> ... ||| <descriptive comment>
        
        The robot can only handle one command at a time. The parser is as forgiving as possible
        and will always try to action on the first word of any command given.  The robot
        understands the following commands:
        """

        return f"{overall_instructions}\n{command_list}"
