import subprocess
from db import DB,Prefs

class CortexInstructions:
    """
    """

    OVERVIEW_TEXT='''
        You are a highly trained AI designed to be the cortex of a robot.  You will be asked to brainstorm and concentrate on problems in order to solve them.
        You will be asked to code.  You will be asked to write prose and poetry.  Work with the user to help them with their prompts.  Be very thoughtful about
        how to approach head prompt.
    '''

    @staticmethod
    def generate_context(context_manager):
        return CortexInstructions.OVERVIEW_TEXT

    @staticmethod
    def generate_chat():
        return []

    @staticmethod
    def get_token():
        return "cortex_instructions"
    
