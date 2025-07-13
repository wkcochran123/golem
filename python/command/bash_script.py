
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
    def action(command,goal_id):
        command_parts = command.split(" ");
        if command_parts[1] == "new":
            return run_new(command_parts[2:])
        if command_parts[1] == "next_step":
            return run_next_step(command_parts[2:])
        if command_parts[1] == "complete":
            return run_complete(command_parts[2:])


    @staticmethod
    def get_token():
        return "bash_script"

    @staticmethod
    def context_description():
        return """
        bash_script 

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

