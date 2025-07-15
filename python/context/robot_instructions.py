import subprocess
from db import DB,Prefs

class RobotInstructions:
    """
    """

    @staticmethod
    def generate_context(context_manager):
        return context_manager.command_manager.get_instructions()

    @staticmethod
    def generate_chat():
        return []

    @staticmethod
    def get_token():
        return "robot_instructions"
    
