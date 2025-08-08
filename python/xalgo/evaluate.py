from db import DB
import random

class Evaluate:

    EVALUATE_COMMANDS = "evaluate commands"
    DEFAULT_EVALUATE_COMMANDS = "code write"
    EVALUATE_RATE = "evaluate rate"
    DEFAULT_EVALUATE_RATE = "0.95"

    @staticmethod
    def get_token():
        return "evaluate"

    @staticmethod
    def prompt_in (prompt,model,context):
        return (prompt,model,context)


    @staticmethod
    def response_out(prompt,response,context):
        return (prompt,response,context)

    @staticmethod
    def command_out(prompt,response,output,context):

        cmds = DB.PREFS.get(Evaluate.EVALUATE_COMMANDS,Evaluate.DEFAULT_EVALUATE_COMMANDS).split(" ")
        cmd = response.strip().split(" ")[0]
        print (f"Found {cmd}")
        if cmd in cmds:
            rnd = random.random();
            lvl = float (DB.PREFS.get(Evaluate.EVALUATE_RATE,Evaluate.DEFAULT_EVALUATE_RATE))
            if rnd > lvl:
                return
            if DB.single_value ("select count(*) from stimuli where prompt like ? and sid not in (select sid from response)",("If your last % command succeed",)) < 1:
                evaluate_prompt = f"If your last {cmd} command succeeded, please run an evaluaion on the file to make sure the file is up to part."
                DB.queue_prompt(evaluate_prompt)
