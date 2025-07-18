from db import DB
from llm import LLMManager
from context import ContextManager

class Evaluate:
    """
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        words = command.split(" ")[1:]
        filename = words[0]
        inout_path = DB.PREFS.get(DB.INOUT_DIRECTORY)
        LLMManager.MANAGER.adjust_mood(1)  #Let's make this good
        try:
            with open(f"{inout_path}/{filename}", "r") as f:
                data = f.read()
        except Exception as e:
            return f"ERROR: {e}"

        expertise = " ".join(words[1:])

        prompt = f"Please evaluate the following on its merits. Be very thorough in your analysis and ensure that you can find every nit.  Give a score out of 100 and grade on a D curve.  Really avoid all benefits of doubt.  We require experise in {expertise}.\n{data}\n"
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.BLANK_CONTEXT)
        return result


    @staticmethod
    def get_token():
        return "evaluate"

    @staticmethod
    def context_description():
        return """
        evaluate <filename> <expertise>
        """

