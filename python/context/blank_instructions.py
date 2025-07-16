from db import DB,Prefs

class BlankInstructions:
    """
    """
    @staticmethod
    def generate_context(context_manager):
        return "You are an AI designed to respond very literally to the requests sent to you.  This context is very short with very few messages in order to get a fresh opinion rather than one from a much longer context."

    @staticmethod
    def generate_chat():
        return []

    @staticmethod
    def get_token():
        return "blank_instructions"
    
