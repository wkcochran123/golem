from db import DB,Prefs
from llm import LLMManager
from context import ContextManager

class BrainStorm:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        words = " ".join(command.split(" ")[1:])
        prompt = f"Brainstorm and focus on the following: {words}"
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        LLMManager.MANAGER.adjust_mood(1)
        return result


    @staticmethod
    def get_token():
        return "brainstorm"


    @staticmethod
    def context_description():
        return """
        brainstorm <prompt>

        The goal of the brainstorm function is to ask the cortex to focus efforts on finding ways to solve problems.  This is a good
        command to run at the very beginning of tasks or every so often to make sure the cortex is pursing the best path forward.

        To use, simply give brainstorm a prompt.  Example:

            brainstorm Think of various ways to approach our current goal of writing a chap application.

        """

