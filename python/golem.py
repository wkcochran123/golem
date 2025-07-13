from db import Prefs,DB
from command import CommandManager
import argparse
import os
import shutil

def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true', help='Reset the system state to blank')
    parser.add_argument('--root_directory', default=os.getcwd(), help='Path to the root of the install (default: current working directory)')
    parser.add_argument('--test_command', default=None, help="Execute a command for testing purposes")
    parser.add_argument('--enable_command', default=None, help="Add a command to the command manager.")
    parser.add_argument('--disable_command', default=None, help="Remove a command from the command manager.")
    args = parser.parse_args()

    DB.stat_db(args.root_directory)
    prefs = Prefs()
    if args.reset:
        print("Resetting system...")
        DB.reset()
        prefs = Prefs()
        prefs.set("root",args.root_directory)
        inout = input ("Set your inout directory [inout]")
        if inout == "":
            inout == "inout"
        prefs.set("inout_directory",args.root_directory + "/" + inout)
        subprocess.run("rm","-rf",prefs.get("inout_directory"))
        os.makedirs(prefs.get("inout_directory"), exist_ok=True)
        

    cm = CommandManager()
    if args.test_command is not None:
        cm.run_command(args.test_command,0)
        exit(0)

    if args.enable_command is not None:
        cm.enable_command(args.enable_command)
        exit(0)

if __name__ == "__main__":
        main()
