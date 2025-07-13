import noop
import goal
import file
import speak
import move
import bash_script
import python_script
import download
import evaluate
import concentrate
import iterate
import code
import refactor

class CommandManager:
    """
    CommandManager

    """


    def __init__ (self):
        self.SUCCESS = "Command executed successfully."
        self.commands = [
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
                Create,
                Iterate,
                Code,
                Refactor,
                ]

    def run_command(self,full_command,goal_id):
        command = full_command.split("|||")[0]
        first_word = command.split(" ")[0]
        for cmd in self.commands:
            if cmd.get_token == first_word:
                return cmd.action(command_parts[0],goal_id)

    def enable_command(self.command):
        if command not in commands:
            commands.append(command)

    def disable_command(command):
        if command in commands:
            commands = [cmd for cmd in commands if cmd != command]

    def get_instructions():
        command_list = ""
        for command in commands:
            command_list = f"{command_list}\n{command.context_description()}"
        overall_instructions = """
        Robot commands take the form:
            <command> <param1> <param2> ... ||| <descriptive comment>
        
        The robot can only handle one command at a time. The parser is as forgiving as possible
        and will always try to action on the first word of any command given.  The robot
        understands the following commands:
        """

        return f"{overall_instructions}\n{command_list}"
