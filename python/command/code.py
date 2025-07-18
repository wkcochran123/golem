from llm import LLMManager
from context import ContextManager
from db import DB

class Code:
    """
    """

    def __init__(self):
        pass

    @staticmethod
    def new_code(words):
        lang = words[0]
        filename = words[1]
        sub_prompt = " ".join(words[2:])
        prompt = f"Please write a {lang} program to solve the following ask:\n{sub_prompt}\n\n PLEASE DO NOT ADD ANY EXPLANATION AS THIS WILL BE COPIED DIRECTLY TO A FILE."
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        lines = result.split("\n")
        while (lines[0][:3] != "```"):
            lines = lines [1:]
        lines = lines[1:-1]
        LLMManager.MANAGER.adjust_mood(len(lines))
        code = "\n".join(lines)
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(inout_path + "/" + filename, 'w') as file:
                file.write(f"{code}\n")
        except Exception as e:
            return (f"Error: {e}")

        return "File written successfully"

    @staticmethod
    def debug_code(words):
        lang = words[0]
        filename = words[1]
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(f"{inout_path}/{filename}", "r") as f:
                data = f.read()
        except Exception as e:
            return f"ERROR: {e}"

        sub_prompt = " ".join(words[2:])
        prompt = f"Please debug the following program in {lang}.  {sub_prompt}\n\n{data} \n\n PLEASE DO NOT ADD ANY EXPLANATION AS THIS WILL BE COPIED DIRECTLY TO A FILE."
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        lines = result.split("\n")
        lines = lines[1:-1]
        LLMManager.MANAGER.adjust_mood(-1)
        code = "\n".join(lines)
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(inout_path + "/" + filename, 'w') as file:
                file.write(f"{code}\n")
        except Exception as e:
            return (f"Error: {e}")
        return "File written successfully"

    @staticmethod
    def refactor_code(words):
        lang = words[0]
        filename = words[1]
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(f"{inout_path}/{filename}", "r") as f:
                data = f.read()
        except Exception as e:
            return f"ERROR: {e}"

        sub_prompt = " ".join(words[2:])
        prompt = f"Please refactor the following program in {lang}.  {sub_prompt}\n\n{data} \n\n PLEASE DO NOT ADD ANY EXPLANATION AS THIS WILL BE COPIED DIRECTLY TO A FILE."
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        lines = result.split("\n")
        LLMManager.MANAGER.adjust_mood(10)
        lines = lines[1:-1]
        code = "\n".join(lines)
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(inout_path + "/" + filename, 'w') as file:
                file.write(f"{code}\n")
        except Exception as e:
            return (f"Error: {e}")
        return "File written successfully"

    @staticmethod
    def action(command):
        words = command.split(" ")[1:]
        sub_command = words[0]
        if sub_command == "new":
            return Code.new_code(words[1:])
        if sub_command == "debug":
            return Code.debug_code(words[1:])
        if sub_command == "refactor":
            return Code.refactor_code(words[1:])
        return f"ERROR: Unknown subcommand {sub_command}"

    @staticmethod
    def get_token():
        return "code"

    @staticmethod
    def context_description():
        return """
        code new|debug|refactor <language> <filename> <prompt>

        The coding command is a versatile way to have the cortex focus on writing software.  There are three different subcommands for code: new, debug,
        and refactor.  These work as you expect and take <language> <filename> <description> as inputs.  Here is an example interaction.

            robot [2025-07-10 22:08:29]> code new python hello_world.py Deliverable: hello_world.py application that writes Hello, World! to the console
            File written successfully.

            robot [2025-07-10 22:08:29]> python_script hello_world.py
            Hello, World!

            robot [2025-07-10 22:08:29]> code refactor python hello_world.py Deliverable: Add some ascii art after the greeting.
            File written successfully.

            robot [2025-07-10 22:08:29]> python_script hello_world.py
            Hello, World!
               _   _          _
              | | | |        | |
              |_| |_| _   _ | | ___
                 | | | | | | || / __|
                 | | | | | | || \__
                 |_| |_| |_| ||___/

        """

