from db import DB
import requests
import json
import time

# import logging
# from db.DBLogger import SQLiteHandler


class Completions:

    API_ENDPOINT = "chat/completion endpoint"
    API_ENDPOINT_DEFAULT = "v1/chat/completions"
    API_ENDPOINT_DESCRIPTION = """
    This is the local endpoint, most likely to be at v1/chat/completions
    """

    URL = "chat/completion url"
    URL_DESCRIPTION = """
    This is the url that expects the v1/chat/completions endpoint to exist. http[s]://<ip address>:<port>
    """
    DEFAULT_MODEL = "llm default model"
    DEFAULT_SLOW = "None"
    MAX_TOKENS = "llm max tokens"

    @staticmethod
    def get_token() -> str:
        return "completions"

    @staticmethod
    def send_prompt(prompt: str, model: str, context: str, chat_log: []) -> str:
        api_key = DB.PREFS.get("api key", "")
        #        logger = logging.getLogger(__name__)
        #        db_handler = SQLiteHandler(DB.DB_PATH)
        # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # db_handler.setFormatter(formatter)
        print("----------------- start send_prompt")
        if api_key == "":
            headers = {"Content-Type": "application/json"}
        else:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

        endpoint = DB.PREFS.get(
            pref=Completions.API_ENDPOINT,
            default=Completions.API_ENDPOINT_DEFAULT,
            description=Completions.API_ENDPOINT_DESCRIPTION,
        )
        url = DB.PREFS.get(Completions.URL)  # This will stall for input on first run
        print (url)

        messages = [
            {"role": "system", "content": context},
        ]
        for role, msg in chat_log:
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": prompt})

        model = DB.PREFS.get(Completions.DEFAULT_MODEL, Completions.DEFAULT_SLOW)
        max_tokens = int(DB.PREFS.get(Completions.MAX_TOKENS, -1))
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,  # Keep unlimited for direct requests
            "stream": False,
        }
        full_url = (
            DB.PREFS.get(Completions.URL) + "/" + DB.PREFS.get(Completions.API_ENDPOINT)
        )
        if DB.PREFS.get("log level", default="WARNING") in ("INFO", "DEBUG"):
            print(f"Asking LLM to think at: {full_url}")
        if DB.PREFS.get("log level", default="WARNING") in ("INFO", "DEBUG"):
            DB.commit(
                "INSERT INTO prompts (level, timestamp, prompt) VALUES (?, ?, ?)",
                (DB.PREFS.get("log level"), DB.cdt(), json.dumps(payload)),
            )
        try:
            response = requests.post(
                full_url, headers=headers, data=json.dumps(payload), timeout=6000
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

        print(full_url)
        print(headers)
        print(f"response: {response}")
        time.sleep(1)
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError):
            return ""
