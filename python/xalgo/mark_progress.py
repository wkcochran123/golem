from db import DB
import random

class MarkProgress:

    MARK_PROGRESS_LIKELIHOOD = "mark progress likelihood"

    @staticmethod
    def get_token():
        return "mark_progress"

    @staticmethod
    def prompt_in (self,prompt,context):
        if random.random() < float(DB.PREFS.get(MarkProgress.MARK_PROGRESS_LIKELIHOOD,.1)):
            DB.queue_prompt("Mark progress on a goal")


    @staticmethod
    def response_out(self,prompt,response,context):
        return (prompt,response,context)

    @staticmethod
    def command_out(self,prompt,response,output,context):
        pass
