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
from .brainstorm import BrainStorm
from .python_script import PythonScript
from .speak import Speak

from db import DB,Prefs

class CommandManager:
    """
    CommandManager

    """


    def __init__ (self):
        self.SUCCESS = "Command executed successfully."
        # This needs to be a file scan.
        self.all_commands = [
                Noop,
                Goal,
                File,
                Look,
                Speak,
                Move,
                BashScript,
                PythonScript,
                Download,
                Evaluate,
                BrainStorm,
                Concentrate,
                Iterate,
                Code,
                ]
        self.commands = []
        cmd_list = [x.get_token() for x in self.all_commands]
        command_list = DB.PREFS.get("command manager list",",".join(cmd_list))
        for x in command_list.split(","):
            self.commands.append(self.find_command(x))

    def find_command(self,command_text):
        for y in self.all_commands:
            if y.get_token() == command_text:
                return y
        return None

    def run_command(self,full_command):
        command = full_command.strip().split("|||")[0]
        first_word = command.split(" ")[0]
        for cmd in self.commands:
            if cmd.get_token() == first_word:
                return cmd.action(command)
        return f"ERROR: Unknown command {first_word}"

    def _write_prefs(self):
        pref_list = []
        for x in self.commands:
            pref_list.append(x.get_token())
        DB.PREFS.set("command manager list",",".join(pref_list))

    def enable_command(self,cmd):
        command = self.find_command(cmd)
        if command not in self.commands:
            self.commands.append(command)
        self._write_prefs()

    def disable_command(self,command):
        self.commands = [cmd for cmd in self.commands if cmd.get_token() != command]
        self._write_prefs()

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
