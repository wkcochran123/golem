from llm import LLMManager
from db import DB


class Noop:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        open_goals = DB.single_value("select count(*) from goals where progress != 1.0")
        if open_goals > 0:
            LLMManager.MANAGER.adjust_mood(-100*open_goals)
            return "ERROR: OPEN GOALS, NOOP IS NOT AN OPTION"
        LLMManager.MANAGER.adjust_mood(-1)  # Boredom
        return "noop"

    @staticmethod
    def get_token():
        return "noop"

    @staticmethod
    def context_description():
        return """
        noop

        Do nothing. If the assistant has nothing to do, just noop.  The noop command
        is very useful when there are ERRORS, as if you feel like the error is too complex
        or if you feel the error is incorrect, you can just noop the error.  This will
        allow you to figure out how to fix it.  If you think there is no error, noop
        is your best call.
        """
