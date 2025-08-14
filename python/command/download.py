import os
import subprocess
from db import DB
from llm import LLMManager

class Download:
    """
    download

    Tell the robot to do nothing
    """

    def __init__(self):
        pass

    @staticmethod
    def action(command):
        ai_words = command.split(" ")
        LLMManager.MANAGER.adjust_mood(1) # Just like TikTok
        output_path = f"{DB.big_strip(ai_words[2])}"
        cmd = ['/usr/bin/curl', '-A', 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0', ai_words[1], '-o', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        return result.stdout + result.stderr

    @staticmethod
    def get_token():
        return "download"

    @staticmethod
    def context_description():
        return """
        download <url> <filename>

        This will download a webpage into a file similar to curl.  To use, give the url and the filename to save the website to.

        Example:
            download http://www.wsj.com todays_wsj.html
        """

