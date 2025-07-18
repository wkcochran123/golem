
class Look:
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
        return "look"

    @staticmethod
    def context_description():
        return """
        look not implemented
        """

