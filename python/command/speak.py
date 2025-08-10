from llm import LLMManager
from db import DB,Prefs

class Speak:
    """
    SPEAK

    This will relay the message through the dialog on the control panel as well as render sound for playing
    over bluetooth.
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        words = command.split(" ")[1:]
        text = ' '.join(words)
        params = {'text': text}
#        speak_url = DB.PREFS.get("speak url")

#        total_url = requests.Request('GET', get_mac_url("speak",8001), params=params).prepare().url
#        response = requests.get(total_url)

#        if response.status_code == 200:
#            with open('/tmp/speech.m4a', 'wb') as f:
#                f.write(response.content)
#            subprocess.run(['ffplay', '-nodisp', '-autoexit', '/tmp/speech.m4a'])
#        else:
#            print(f"Error from TTS service: {response.status_code}")

        return "speak"



    @staticmethod
    def get_token():
        return "speak"

    @staticmethod
    def context_description():
        return ""
      #  return """
      #  speak <text>

      #  This will speak the text aloud.
      #  """

