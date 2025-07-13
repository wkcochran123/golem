class PythonScript:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command,goal_id):
        pass

    @staticmethod
    def get_token():
        return "python_script"

    @staticmethod
    def context_description():
        return """
        Do nothing. If the assistant has nothing to do, just noop.  The noop command
        is very useful when there are ERRORS, as if you feel like the error is too complex
        or if you feel the error is incorrect, you can just noop the error.  This will
        allow you to figure out how to fix it.  If you think there is no error, noop
        is your best call.
        """

