from db import DB
import random

class MakeProgress:

    @staticmethod
    def get_token():
        return "make_progress"

    @staticmethod
    def prompt_in (self,prompt,model,context):
        open_goal_count = DB.single_value("select count(*) from goals where progress < 1.0")
        if open_goal_count > 0:
            DB.queue_prompt("Choose a goal and make progress on it")
        if open_goal_count > 1:
            if random.random() < 0.1:
                DB.queue_prompt("Choose a different goal to work on for awhile")
        return prompt,model,context


    @staticmethod
    def response_out(self,prompt,response,context):
        return (prompt,response,context)

    @staticmethod
    def command_out(self,prompt,response,output,context):
        pass
