from db import DB,Prefs
from .completions import Completions


class LLMManager:
    """
    """

    STRATEGY = "llm strategy"
    DEFAULT_MODEL = "gemma-3-4b-it-qat"

    def __init__ (self):
        self.all_llm_strategies = [
                Completions,
                ]
        strat = DB.PREFS.get(LLMManager.STRATEGY,Completions.get_token())
        for x in self.all_llm_strategies:
            if x.get_token() == strat:
                self.strategy = x

    def send_prompt(self,prompt: str, model: str, context: str, chat_log: []) -> str:
        print(f"{prompt}\n--\n{model}\n--\n{context}--\n{chat_log}")
        return self.strategy.send_prompt(prompt, model, context, chat_log)

