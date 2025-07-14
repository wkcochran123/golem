from .robot_instructions import RobotInstructions
from .robot_console import RobotConsole
from db import DB,Prefs

class ContextManager:
    """
    This class manages the contexts being presented to the LLM.
    """

    def __init__(self,command_manager):
        self.command_manager = command_manager
        self.all_context_generators = [
                RobotInstructions,
                RobotConsole,
                ]

        context_types = DB.PREFS.get("context types")
        self.context_generators = dict()
        for context in context_types.split(","):
            generators_for_context = DB.PREFS.get(f"{context} generators")
            generator_list = []
            for generator in generators_for_context.split(","):
                for t in self.all_context_generators:
                    if t.get_token() == generator:
                        generator_list.append(t)
            self.context_generators[context] = generator_list

    def generate_context(self,context):
        answer = ""
        for x in self.context_generators[context]:
            answer = f"{answer}\n-------{x.get_token()}--------\n{x.generate(self)}"
        return answer
