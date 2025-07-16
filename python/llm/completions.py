from db import DB
import requests
import json

class Completions:

    API_ENDPOINT = "chat/completion endpoint"
    URL = "chat/completion url"
    DEFAULT_MODEL = "llm default model"
    DEFAULT_SLOW = "qwq-32b"

    @staticmethod
    def get_token() -> str:
        return "completions"

    @staticmethod
    def send_prompt(prompt: str, model: str, context: str, chat_log: []) -> str:
            
        headers = {
            "Content-Type": "application/json"
        }

        endpoint = DB.PREFS.get(Completions.API_ENDPOINT,"v1/chat/completions")
        url = DB.PREFS.get(Completions.URL)  # This will stall for input on first run
        full_url = url.strip("/") + "/" + endpoint
        
        messages = [
            {"role": "system", "content": context},
        ]
        for (role,msg) in chat_log:
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": prompt})

        for message in messages:
            role = message["role"]
            content = message["content"]
            print (f"{role}:\n{content}\n\n")
        if model == None:
            model = DB.PREFS.get(Completions.DEFAULT_MODEL,Completions.DEFAULT_SLOW)
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": -1,  # Keep unlimited for direct requests
            "stream": False
        }
        response = requests.post(full_url, headers=headers, data=json.dumps(payload), timeout=3000)
        return response.json()["choices"][0]["message"]["content"]
