import subprocess
from db import DB,Prefs
from llm import LLMManager

class BashScript:
    """
    BashScript

    Tell the robot to run a bash script from the file list
    """


    def __init__(self):
        pass


    def run_new(command):
        goal = " ".join(command[1:])
        test_script = command[0]
        goal = f"{goal}. But before you get started, Brainstorm about the different ways to achieve the goal, then choose one and concentrate on it."

    @staticmethod
    def action(command):
        words = command.split(" ")
        inout_path = DB.PREFS.get("inout directory")
        words[1] = f"{inout_path}/{words[1]}"
        cmd = ["bash"] + words[1:]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=300)
        except Exception as e:
            LLMManager.MANAGER.adjust_mood(-100)
            return f"ERROR: {e}"
        LLMManager.MANAGER.adjust_mood(10)
        return result.stdout + result.stderr


    @staticmethod
    def get_token():
        return "bash_script"

    @staticmethod
    def context_description():
        return """
        bash_script <script name>

        The bash_script will execute a bash script on the robot for you. In order to
        use bash_script, first code up a script in bash then call this method.

            robot [2025-07-10 22:08:29]> code new bash install.sh Script to install the software. ||| Writing a script to process all install steps.
            File written successfully.
            robot [2025-07-10 22:09:29]> bash_script install.sh || Running script
            Software installed successfully.

        Should the script fail, iterator on the failure to make progress.

            robot [2025-07-10 22:08:29]> code new bash install.sh Script to install the software. ||| Writing a script to process all install steps.
            File written successfully.
            robot [2025-07-10 22:08:50]> bash_script install.sh || Running script
            install.sh: line 3: lss: command not found
            robot [2025-07-10 22:09:29]> code debug bash install.sh Fix error: install.sh: line 3: lss: command not found. ||| Fix the command not found bug
            File written successfully.
            robot [2025-07-10 22:10:29]> bash_script install.sh || Running script
            Software installed successfully.

        Success or error is shown on the command output.
        """

