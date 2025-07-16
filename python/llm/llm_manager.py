from db import DB,Prefs
from .completions import Completions
from context import ContextManager


class LLMManager:
    """
    """

    STRATEGY = "llm strategy"
    #DEFAULT_MODEL = "gemma-3-4b-it-qat"
    DEFAULT_MODEL = "qwq-32b"
    MANAGER = None

    def __init__ (self):
        self.all_llm_strategies = [
                Completions,
                ]
        strat = DB.PREFS.get(LLMManager.STRATEGY,Completions.get_token())
        for x in self.all_llm_strategies:
            if x.get_token() == strat:
                self.strategy = x

        LLMManager.MANAGER = self

    def send_prompt(self,prompt: str, model: str, context: str) -> str:
        in_cdt = DB.cdt()
        response = self.strategy.send_prompt(prompt, 
                                             model, 
                                             ContextManager.MANAGER.generate_context(context), 
                                             ContextManager.MANAGER.generate_chat(context))
        DB.add_prompt_response(prompt,response,context,in_cdt)
        return response

