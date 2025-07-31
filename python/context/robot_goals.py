import subprocess
from db import DB,Prefs

class RobotGoals:
    """
    """

    @staticmethod
    def generate_context(context_manager):
        answer = "The following CSV describes the goals of the robot:\ngoal id , progress , test script , start time , description\n"
        for row in DB.select("select gid,progress,timestamp,description from goals where progress < 1.0"):
            answer = f"{answer}{row[0]},{row[1]},{row[2]},{row[3]}\n"
        return answer

    @staticmethod
    def generate_chat():
        return []

    @staticmethod
    def get_token():
        return "robot_goals"
    
