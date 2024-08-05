import logging
import dspy

from .llm import GeneralChatSig
from ...session import Dialogue

class GeneralChatServer:
    def __init__(self, ui):
        self.name = 'Schedule Event'
        self.ui = ui
        self.general_chat = dspy.TypedPredictor(GeneralChatSig)

    
    async def process_dialogue(self, dialogue: Dialogue):
        logging.info(f'Dialogue: {dialogue}')
        reply = self.general_chat(dialogue=dialogue).reply
        self.ui.send_to_user(reply)