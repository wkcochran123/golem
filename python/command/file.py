from db import DB,Prefs
import os

class File:
    """
    NOOP

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def _get_file_list():
        inout_path = DB.PREFS.get("inout directory")
        return "\n".join([d for d in os.listdir(inout_path)])


    @staticmethod
    def _read_file(fname):
        inout_path = DB.PREFS.get("inout directory")
        fname = f"{inout_path}/{fname}"
        try:
            with open(fname, 'r') as file:
                contents = file.read()
        except Exception as e:
            return (f"Error: {e}")
        return contents


    @staticmethod
    def action(command):
        words = command.split(" ")
        subcommand = words[1]
        if subcommand == "list":
            return File._get_file_list()
        if subcommand == "read":
            return File._read_file(words[2])
        return f"ERROR Unknown file subcommand: {subcommand}"

    @staticmethod
    def get_token():
        return "file"

    @staticmethod
    def context_description():
        return """
        file

        The file command is used to interact with files on disk.

        file list
        List all the files in the robot's storage. 

        file read <filename>
        This will read the file and place the contents in the telemetry.
        """

