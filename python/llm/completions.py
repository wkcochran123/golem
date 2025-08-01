from db import DB
import requests
import json
import time


class Completions:

    API_ENDPOINT = "chat/completion endpoint"
    URL = "chat/completion url"
    DEFAULT_MODEL = "llm default model"
    DEFAULT_SLOW = "None"
    MAX_TOKENS = "llm max tokens"

    @staticmethod
    def get_token() -> str:
        return "completions"

    @staticmethod
    def send_prompt(prompt: str, model: str, context: str, chat_log: []) -> str:
        api_key = DB.PREFS.get("api key", "")
        print("----------------- start send_prompt")
        if api_key == "":
            headers = {"Content-Type": "application/json"}
        else:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

        endpoint = DB.PREFS.get(Completions.API_ENDPOINT, "v1/chat/completions")
        url = DB.PREFS.get(Completions.URL)  # This will stall for input on first run
        full_url = url.strip("/") + "/" + endpoint

        messages = [
            {"role": "system", "content": context},
        ]
        for role, msg in chat_log:
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": prompt})

        #        for message in messages:
        #            role = message["role"]
        #            content = message["content"]
        #            print(f"m: {role}:\n{content}\n\n")
        #        if model == None:
        model = DB.PREFS.get(Completions.DEFAULT_MODEL, Completions.DEFAULT_SLOW)
        max_tokens = int(DB.PREFS.get(Completions.MAX_TOKENS, -1))
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,  # Keep unlimited for direct requests
            "stream": False,
        }
        print(f"full url: {full_url}")
        print(f"headers: {headers}")
        print(f"num messages: {len(payload)}")
        print(f"model: {model}")
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            print(f"{role}:\n{content}\n")

        try:
            response = requests.post(
                full_url, headers=headers, data=json.dumps(payload), timeout=3000
            )
            response.raise_for_status
        except requests.exceptions.Timeout:
            print("Request timed out.")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.ConnectionError:
            print("Connection error occurred.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        print(f"response: {response}")
        time.sleep(1)
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError):
            return ""
