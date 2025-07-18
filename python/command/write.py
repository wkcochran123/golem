from llm import LLMManager
from db import DB
from context import ContextManager

class Write:
    """
    """

    def __init__(self):
        pass

    @staticmethod
    def new_doc(words):
        filename = words[0]
        sub_prompt = " ".join(words[1:])
        prompt = f"Please write a something to the following prompt:\n{sub_prompt}\n\n PLEASE DO NOT ADD ANY EXPLANATION AS THIS WILL BE COPIED DIRECTLY TO A FILE."
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        LLMManager.MANAGER.adjust_mood(100)
        try:
            with open(inout_path + "/" + filename, 'w') as file:
                file.write(f"{result}\n")
        except Exception as e:
            return (f"Error: {e}")

        return "File written successfully"

    @staticmethod
    def edit_doc(words):
        filename = words[0]
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(f"{inout_path}/{filename}", "r") as f:
                data = f.read()
        except Exception as e:
            LLMManager.MANAGER.adjust_mood(-10)
            return f"ERROR: {e}"

        sub_prompt = " ".join(words[1:])
        prompt = f"Please edit the following doc. {sub_prompt}\n\n {data}\n\nPLEASE DO NOT ADD ANY EXPLANATION AS THIS WILL BE COPIED DIRECTLY TO A FILE."
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        try:
            with open(inout_path + "/" + filename, 'w') as file:
                file.write(f"{result}\n")
        except Exception as e:
            LLMManager.MANAGER.adjust_mood(-10)
            return (f"Error: {e}")
        LLMManager.MANAGER.adjust_mood(10)
        return "File written successfully"


    @staticmethod
    def action(command):
        words = command.split(" ")[1:]
        sub_command = words[0]
        if sub_command == "new":
            return Write.new_doc(words[1:])
        if sub_command == "edit":
            return Write.edit_doc(words[1:])
        return f"ERROR: Unknown subcommand {sub_command}"
        pass

    @staticmethod
    def get_token():
        return "write"

    @staticmethod
    def context_description():
        return """
        write ...
        """

