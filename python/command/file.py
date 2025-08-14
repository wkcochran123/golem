from db import DB,Prefs
import os

class File:
    """
    """

    def __init__(self):
        pass

    @staticmethod
    def _get_file_list():
        return "\n".join([d for d in os.listdir(os.getcwd())])


    @staticmethod
    def _read_file(fname):
        try:
            with open(fname, 'r') as file:
                contents = file.read()
        except Exception as e:
            return (f"Error: {e}")
        return contents


    @staticmethod
    def _chdir(dir):
        os.chdir(dir)

    @staticmethod
    def action(command):
        words = command.split(" ")
        subcommand = words[1]
        if subcommand == "list":
            return File._get_file_list()
        if subcommand == "read":
            return File._read_file(words[2])
        if subcommand == "chdir":
            return File._chdir(words[2])
        return f"ERROR Unknown file subcommand: {subcommand}"

    @staticmethod
    def get_token():
        return "file"

    @staticmethod
    def context_description():
        return """
        The file command is used to interact with files on disk.

        file list
        List all the files in the robot's storage. 

        file read <filename>
        This will read the file and place the contents in the telemetry.

        file chdir <dir>
        Change the current directory to read from.
        """

