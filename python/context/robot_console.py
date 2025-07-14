import subprocess
from db import DB,Prefs

class RobotConsole:
    """
    """

    @staticmethod
    def generate(context_manager):
        answer = ""
        for row in DB.select("select timestamp,command,result from robot_console"):
            answer = f"{answer}\nrobot [{row[0]}]> {row[1]}\n{row[2]}\n"
        answer = f"{answer}\nrobot [{DB.cdt()}]> _\n"
        return answer


    @staticmethod
    def get_token():
        return "robot_console"
    
