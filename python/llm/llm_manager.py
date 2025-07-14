from db import DB,Prefs


class LLMManager:
    """
    """

    STRATEGY = "llm strategy"

    def __init__ (self):
        self.endpoint = DB.PREFS.get(LLMManager.COMPLETION_API_ENDPOINT)
        self.all_llm_strategies = [

                ]
        strat = DB.PREFS.get(LLMManager.STRATEGY)
        for x in self.all_llm_strategies:
            if x.get_token() == strat:
                self.strategy = x
`
    def send_prompt(prompt: str, model: str, context: str, chat_log: []) -> str:
        return self.strategy.send_prompt(prompt, model, context, chat_log)

