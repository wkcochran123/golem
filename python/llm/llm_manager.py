from db import DB,Prefs


class LLMManager:
    """
    """

    COMPLETION_API_ENDPOINT = "llm endpoint"

    def __init__ (self):
        self.endpoint = DB.PREFS.get(LLMManager.COMPLETION_API_ENDPOINT)
`
