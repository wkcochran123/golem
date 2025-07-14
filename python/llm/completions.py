from db import DB

class Completions:

    API_ENDPOINT = "chat/completion endpoint"
	URL = "chat/completion url"
	DEFAULT_MODEL = "chat/completion default model"

    @staticmethod
    def send_prompt(prompt: str, context: str, chat_log: []) -> str:
        if not base_url:
            raise ValueError("LLM base URL must be provided")
            
        endpoint = DB.PREFS.get(Completions.API_ENDPOINT,"v1/chat/completions")
        full_url = DB.PREFS.get(Completions.URL)  # This will stall for input on first run
		model = DB.PREFS.get(Completions.DEFAULT_MODEL)
		context_model = DB.PREFS.get(f"{context} model",model)
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": -1,  # Keep unlimited for direct requests
            "stream": False
        }
        print(f"Making request to: {full_url}")
        return requests.post(full_url, headers=headers, data=json.dumps(payload), timeout=3000)
