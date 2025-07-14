import subprocess
from db import DB,Prefs

class RobotInstructions:
    """
    """

    @staticmethod
    def generate(context_manager):
        return context_manager.command_manager.get_instructions()

    @staticmethod
    def get_token():
        return "robot_instructions"
    
