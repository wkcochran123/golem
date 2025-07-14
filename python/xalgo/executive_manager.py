from .random_thoughts import RandomThoughts
from .mark_process import MarkProcess
from .make_process import MakeProcess

class ExecutiveManager:

    XM_LIST = "executive manager list"

    def __init__ (self):
        this.all_xrules = [
                RandomThoughts,
                MarkProgress,
                MakeProgress,
                ]
        def_pref = [x.get_token() for x in this.all_xrules]
        xrules = DB.PREFS.get(XM_LIST,db_pref)
        this.rules = []
        for rule in xrules:
            for t in this.all_xrules:
                if t.get_token() == rule:
                    this.rules.append(t)

    def prompt_in (self,prompt,context):
        for x in this.rules:
            (prompt,context) = x.prompt_in(prompt,context)
        return (prompt,context)

    def response_out (self,prompt,response,context):
        for x in this.rules:
            (prompt,response,context) = x.response_out(prompt,response,context)
        return (prompt,response,context)

    def command_out (self,prompt,response,output,context):
        for x in this.rules:
            x.command_out(prompt,response,output,context)
        pass
