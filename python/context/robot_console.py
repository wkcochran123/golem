import subprocess
from db import DB,Prefs
import os

class RobotConsole:
    """
    """

    @staticmethod
    def generate_context(context_manager):
        answer = ""
        curdir = os.getcwd();
        for row in DB.select("select timestamp,command,result from robot_console"):
            answer = f"{answer}\nrobot [{row[0]}] {curdir}> {row[1]}\n{row[2]}\n"
        answer = f"{answer}\nrobot [{DB.cdt()}]> _\n"
        return answer

    @staticmethod
    def generate_chat():
        return []

    @staticmethod
    def get_token():
        return "robot_console"
    
