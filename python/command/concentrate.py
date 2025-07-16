from llm import LLMManager
from context import ContextManager
from db import DB

class Concentrate:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        words = " ".join(command.split(" ")[1:])
        prompt = f"Concentrate on figuring out what needs to be done.  The robot is asking for more insight on: {words}"
        result = LLMManager.MANAGER.send_prompt(prompt, LLMManager.DEFAULT_MODEL, ContextManager.THINK_CONTEXT)
        print(result)
        return result

    @staticmethod
    def get_token():
        return "concentrate"

    @staticmethod
    def context_description():
        return """
        concentrate <prompt>

        By concentrating, you can explore a broader set of solutions. This is good to do every once in a while to focus
        thoughts on particularly difficult problems.

        Example:
            
            concentrate Focus on the best way to get started writing a book.
        """

