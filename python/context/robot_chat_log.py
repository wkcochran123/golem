from db import DB,Prefs

class RobotChatLog:
    """
    """

    @staticmethod
    def generate_context(context_manager):
        return "The chat log below shows user messages that come from a robot that is working on behalf of a user"

    @staticmethod
    def generate_chat():
        answer = []
        for row in DB.select ("SELECT stimuli.prompt, response.response from stimuli,response where stimuli.context = 'robot' and stimuli.sid = response.sid order by stimuli.sid"):
            answer.append(("user",row[0]))
            answer.append(("assistant",row[1]))

        return answer

    @staticmethod
    def get_token():
        return "robot_chat_log"
    
