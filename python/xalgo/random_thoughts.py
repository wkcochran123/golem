from db import DB
import random

class RandomThoughts:

    RANDOM_THOUGHTS_LIKELIHOOD = "random thoughts likelihood"

    RANDOM_THOUGHTS = [
            "Brainstorm about the current goal you are focused on.  Verify that there is not a better alternative approach",
            "Conentrate on how to tackle your current step in your current goal.  Concentrating on the problem organizes your thoughts a bit better, improving your efficacy.",
            "Evaluate your current progress.  Use the evaluate command to see how your are doing. Ensure you listen to the advice.",
            ]

    @staticmethod
    def get_token():
        return "random_thoughts"

    @staticmethod
    def prompt_in (self,prompt,context):
        if random.random() < float(DB.PREFS.get(RandomThoughts.RANDOM_THOUGHTS_LIKELIHOOD,.5)):
            thought_index = random.randint(0,len(RandomThought.RANDOM_THOUGHTS))
            DB.queue_prompt(RandomThought.RANDOM_THOUGHTS[thought_indes])


    @staticmethod
    def response_out(self,prompt,response,context):
        return (prompt,response,context)

    @staticmethod
    def command_out(self,prompt,response,output,context):
        pass
