from db import DB,Prefs

class CompleteChatLog:
    """
    """

    @staticmethod
    def generate_context(context_manager):
        return "The chat log below shows user messages that come from a robot that is working on behalf of a user"

    @staticmethod
    def generate_chat():
        answer = []
        for row in DB.select ("SELECT stimuli.prompt, response.response where stimuli.sid = response.sid order by sid"):
            answer.append(("user",row[0]))
            answer.append(("assistant",row[1]))

        return answer

    @staticmethod
    def get_token():
        return "complete_chat_log"
    
