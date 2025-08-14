import subprocess
import os
from db import DB,Prefs
from llm import LLMManager

class PythonScript:
    """
    PythonScript

    Run a python script in the file list
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        words = command.split(" ")
        cmd = ["python"] + words[1:]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=300)
        except Exception as e:
            LLMManager.MANAGER.adjust_mood(-10)
            return f"ERROR: {e}"
        if len(result.stderr) > 0:
            
            LLMManager.MANAGER.adjust_mood(-5)
        else:
            LLMManager.MANAGER.adjust_mood(100)
        return result.stdout + result.stderr


    @staticmethod
    def get_token():
        return "python_script"

    @staticmethod
    def context_description():
        return """
        python_script

        This will execute a simple python script with arguments. This is a very light
        wrapper around the installed python on the robot.

        python_script <script name> <param1> <param2>

        If you need more sophisticated python, create a bash wrapper around the python
        call to encapsulate the environment.
        """

