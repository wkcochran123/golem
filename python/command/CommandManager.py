from .bash_script import BashScript
from .code import Code
from .concentrate import Concentrate
from .download import Download
from .evaluate import Evaluate
from .file import File
from .goal import Goal
from .look import Look
from .move import Move
from .noop import Noop
from .write import Write
from .brainstorm import BrainStorm
from .python_script import PythonScript
from .speak import Speak

from db import DB,Prefs
from llm import LLMManager

class CommandManager:
    """
    CommandManager

    """

    MANAGER = None

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
                Write,
                Code,
                ]
        self.commands = []
        cmd_list = [x.get_token() for x in self.all_commands]
        command_list = DB.PREFS.get("command manager list",",".join(cmd_list))
        for x in command_list.split(","):
            self.commands.append(self.find_command(x))

        CommandManager.MANAGER = self

    def find_command(self,command_text):
        for y in self.all_commands:
            if y.get_token() == command_text:
                return y
        return None

    def get_commands(self):
        answer = ""
        for y in self.commands:
            answer = answer + y.get_token() + "\n"
        return answer.strip()

    def run_command(self,full_command):
        command = full_command.strip().split("|||")[0]
        first_word = command.split(" ")[0]
        for cmd in self.commands:
            if cmd.get_token() == first_word:
                if command.split(" ")[0] not in ["goal","noop","file"]:

                    sql = "select count(*) from goals where progress != 1.0"
                    x= DB.single_value(sql) 
                    if x != 0:
                        result = cmd.action(command)
                    else:
                        result = "ERROR: THERE ARE NO ACTIVE GOALS.  Please set a new goal to accomplist a task:\n\ngoal new <task>If you have nothing to do, simply noop.\n"
                        LLMManager.MANAGER.adjust_mood(-1000)
                else:
                    result = cmd.action(command)
                if result == cmd.get_token():
                    LLMManager.MANAGER.adjust_mood(10)
                print (f"Got result:")
                DB.add_console_line(command,result,DB.cdt())
                return result
        return f"ERROR: Unknown command {first_word}.  Available commands: " + " ".join([x.get_token() for x in self.commands])

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
