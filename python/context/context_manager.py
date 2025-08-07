from .robot_instructions import RobotInstructions
from .cortex_instructions import CortexInstructions
from .robot_console import RobotConsole
from .complete_chat_log import CompleteChatLog
from .robot_chat_log import RobotChatLog
from .robot_goals import RobotGoals
from db import DB,Prefs

class ContextManager:
    """
    This class manages the contexts being presented to the LLM.
    """

    ROBOT_CONTEXT = 'robot'
    THINK_CONTEXT = 'think'
    BLANK_CONTEXT = 'blank'
    ROBOT_CONTEXT_GENERATORS = 'robot_instructions,robot_goals,robot_console,robot_chat_log'
    THINK_CONTEXT_GENERATORS = 'cortex_instructions,robot_goals,robot_console,complete_chat_log'
    BLANK_CONTEXT_GENERATORS = 'blank_instructions'
    MANAGER = None

    USER_PROMPT_START = "The USER has provided a prompt.  If prompt is about a new goal, remember to set a goal to accomplish this task:\n"

    def __init__(self,command_manager):
        self.command_manager = command_manager
        self.all_context_generators = [
                CortexInstructions,
                RobotInstructions,
                RobotConsole,
                CompleteChatLog,
                RobotChatLog,
                RobotGoals,
                ]

        context_types = DB.PREFS.get("context types",",".join([ContextManager.ROBOT_CONTEXT,ContextManager.THINK_CONTEXT,ContextManager.BLANK_CONTEXT]))
        DB.PREFS.set(f"{ContextManager.ROBOT_CONTEXT} generators",f"{ContextManager.ROBOT_CONTEXT_GENERATORS}")
        DB.PREFS.set(f"{ContextManager.THINK_CONTEXT} generators",f"{ContextManager.THINK_CONTEXT_GENERATORS}")
        DB.PREFS.set(f"{ContextManager.BLANK_CONTEXT} generators",f"{ContextManager.BLANK_CONTEXT_GENERATORS}")
        self.context_generators = dict()
        for context in context_types.split(","):
            generators_for_context = DB.PREFS.get(f"{context} generators")
            generator_list = []
            for generator in generators_for_context.split(","):
                for t in self.all_context_generators:
                    if t.get_token() == generator:
                        generator_list.append(t)
            self.context_generators[context] = generator_list

        ContextManager.MANAGER = self

    def generate_chat(self,context):
        answer = []
        for x in self.context_generators[context]:
            answer = answer + x.generate_chat()
        return answer


    def generate_context(self,context):
        answer = ""
        for x in self.context_generators[context]:
            answer = f"{answer}\n-------{x.get_token()}--------\n{x.generate_context(self)}"
        return answer
