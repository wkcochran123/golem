from db import Prefs, DB
from command import CommandManager
from context import ContextManager
from xalgo import ExecutiveManager
from llm import LLMManager
import argparse
import os
import shutil
import subprocess
import yaml

import os
import sys


def daemonize(script_path):
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    os.setsid()
    os.umask(0)

    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "w") as devnull:
        os.dup2(devnull.fileno(), 0)
        os.dup2(devnull.fileno(), 1)
        os.dup2(devnull.fileno(), 2)

    os.execvp("python3", ["python3", script_path])


def build_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset", action="store_true", help="Reset the system state to blank"
    )
    parser.add_argument(
        "--root_directory",
        default=os.getcwd(),
        help="Path to the root of the install (default: current working directory)",
    )
    parser.add_argument(
        "--test_command", default=None, help="Execute a command for testing purposes"
    )
    parser.add_argument(
        "--enable_command", default=None, help="Add a command to the command manager."
    )
    parser.add_argument(
        "--disable_command",
        default=None,
        help="Remove a command from the command manager.",
    )
    parser.add_argument(
        "--list_prefs", action="store_true", help="List all known preferences"
    )
    parser.add_argument(
        "--set_pref_key", default=None, help="The key to a preference to set"
    )
    parser.add_argument(
        "--set_pref_val", default=None, help="The value of a preference to set"
    )
    parser.add_argument(
        "--drop_pref_key", default=None, help="The key of some preference to drop"
    )
    parser.add_argument(
        "--start", action="store_true", help="Start the robot prompt pump"
    )
    parser.add_argument(
        "--stop", action="store_true", help="Start the robot prompt pump"
    )
    parser.add_argument("--prompt", default=None, help="Send the golem a prompt")
    parser.add_argument(
        "--export_prefs",
        default=None,
        help="Export the current preferences to file",
    )
    parser.add_argument(
        "--import_prefs",
        default=None,
        help="Import preferences from file",
    )
    parser.add_argument(
        "--log_level",
        default=None,
        choices=["WARNING", "INFO", "DEBUG"],
        help="Set the log level",
    )
    return parser.parse_args()


def run_infinite_loop(llm_manager, executive_manager, context_manager, command_manager):
    os.chdir(DB.PREFS.get("inout directory"))
    ExecutiveManager.start()
    DB.PREFS.reload()  # Hot swapping prefs like a boss
    while ExecutiveManager.is_running():
        (prompt, context) = DB.pop_prompt()
        (prompt, context, model) = executive_manager.prompt_in(prompt, context)
        if prompt == None:
            (prompt, context, model) = executive_manager.no_prompt()
        result = llm_manager.send_prompt(prompt, model, context)
        (prompt, result, context) = executive_manager.response_out(
            prompt, result, context
        )
        output = command_manager.run_command(result)
        llm_manager.flush_mood()
        executive_manager.command_out(prompt, result, output, context)
        DB.PREFS.reload()


def main():
    args = build_argparse()
    DB.stat_db(args.root_directory)
    prefs = Prefs()
    inout_path = prefs.get("inout directory", args.root_directory + "/inout")
    os.makedirs(prefs.get("inout directory"), exist_ok=True)
    if args.reset:
        print("Resetting system")
        DB.reset()
        DB.PREFS.set("root", args.root_directory)
        inout = input("Set your inout directory [inout]").strip()
        if inout.strip() == "":
            inout = "inout"
        DB.PREFS.set("inout directory", DB.PREFS.get("root") + "/" + inout)
        subprocess.run(["rm", "-rf", prefs.get("inout directory")])
        os.makedirs(DB.PREFS.get("inout directory"), exist_ok=True)

    if args.list_prefs:
        for k, v in DB.PREFS._preferences.items():
            print(f"'{k}': '{v}'")
        exit(0)

    if args.set_pref_key:
        if not args.set_pref_val:
            raise TypeError("Missing --set_pref_val")
        DB.PREFS.set(args.set_pref_key, args.set_pref_val)

    if args.drop_pref_key:
        try:
            DB.PREFS.drop(args.drop_pref_key)
        except KeyError:
            print(f"No such preference key: {args.drop_pref_key}")
            exit(0)

    if args.export_prefs:
        with open(args.export_prefs, "w") as f:
            yaml.safe_dump(DB.PREFS._preferences, f)
        exit(0)

    if args.import_prefs:
        try:
            with open(args.import_prefs, "r") as f:
                loaded_prefs = yaml.safe_load(f)
                if loaded_prefs:
                    for k, v in loaded_prefs.items():
                        DB.PREFS.set(k, v)
                    print(f"Successfully imported preferences from {args.import_prefs}")
                else:
                    print(f"File {args.import_prefs} is empty or invalid")
            exit(0)
        except FileNotFoundError:
            print(f"Error: File not found: {args.import_prefs}")
            exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in: {args.import_prefs}")
            exit(1)
        except Exception as e:
            print(f"Error importing {args.import_prefs}:\n {e}")
            exit(1)

    if args.log_level:
        DB.PREFS.set("log level", args.log_level)
        exit(1)

    command_manager = CommandManager()
    if args.enable_command is not None:
        command_manager.enable_command(args.enable_command)
        exit(0)

    if args.disable_command is not None:
        command_manager.disable_command(args.disable_command)
        exit(0)

    context_manager = ContextManager(command_manager)
    executive_manager = ExecutiveManager()
    llm_manager = LLMManager()

    ############## ONCE CODE REACHES HERE, WE ARE READY TO GET SMART!
    if args.test_command is not None:
        print(command_manager.run_command(args.test_command))
        exit(0)

    if args.start:
        #        daemonize(args.root_directory + "/ctrl.py")
        print("Command and control started")
        run_infinite_loop(
            llm_manager, executive_manager, context_manager, command_manager
        )
        exit(0)

    if args.stop:
        ExecutiveManager.stop()
        exit(0)

    if args.prompt is not None:
        DB.queue_prompt(f"{ContextManager.USER_PROMPT_START}{args.prompt}")


if __name__ == "__main__":
    main()
