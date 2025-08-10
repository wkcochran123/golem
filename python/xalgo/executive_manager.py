from .random_thoughts import RandomThoughts
from .mark_progress import MarkProgress
from .make_progress import MakeProgress
from .evaluate import Evaluate
from db import DB
from llm import LLMManager

class ExecutiveManager:

    XM_LIST = "executive manager list"
    STATE = "golem state"
    RUNNING = 1
    STOP = 0
    DEFAULT_PROMPT = "MAKE PROGRESS: Look to see if there are any goals mentioned.  If not, emit noop."
    DEFAULT_CONTEXT = "robot"

    def __init__ (self):
        self.all_xrules = [
                Evaluate,
                RandomThoughts,
#                MarkProgress, 
                MakeProgress,
                ]
        db_pref = [x.get_token() for x in self.all_xrules]
        xrules = DB.PREFS.get(ExecutiveManager.XM_LIST," ".join(db_pref)).split(" ")
        self.rules = []
        for rule in xrules:
            for t in self.all_xrules:
                if t.get_token() == rule:
                    self.rules.append(t)

    @staticmethod
    def start():
        DB.PREFS.set(ExecutiveManager.STATE,ExecutiveManager.RUNNING)

    @staticmethod
    def stop():
        DB.PREFS.set(ExecutiveManager.STATE,ExecutiveManager.STOP)

    @staticmethod
    def is_running():
        return int(DB.PREFS.get(ExecutiveManager.STATE)) == ExecutiveManager.RUNNING

    def no_prompt(self):
        return self.prompt_in(ExecutiveManager.DEFAULT_PROMPT,ExecutiveManager.DEFAULT_CONTEXT)

    def prompt_in (self,prompt,context):
        model=None
        for x in self.rules:
            (prompt,model,context) = x.prompt_in(prompt,model,context)
        if (model == None):
            model = LLMManager.DEFAULT_MODEL
        return (prompt,context,model)

    def response_out (self,prompt,response,context):
        for x in self.rules:
            (prompt,response,context) = x.response_out(prompt,response,context)
        return (prompt,response,context)

    def command_out (self,prompt,response,output,context):
        for x in self.rules:
            print (f"Doing this for {x}")
            x.command_out(prompt,response,output,context)
        pass
