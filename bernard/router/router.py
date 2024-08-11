
import logging
import re

import dspy
from ..session import Dialogue, Message, SessionContext
from .llm import IntentRouterSig


class DialogueRouter:
    def __init__(self, channel) -> None:
        self.intent_router = dspy.TypedPredictor(IntentRouterSig)
        self.channel = channel
        self.server = {}
    
    def add_server(self, intent, server):
        self.server[intent] = server
    

    async def route(self):
        session = self.channel.current_session

        if session['intent'] is None:
            # intent = self._hard_code_route(session['dialogue'])
            # if intent is None:
            intent = self.intent_router(dialogue=session['dialogue']).intent
            session['intent'] = intent

        logging.info(f'Intent: {session["intent"]}')
        await self.server[session['intent']].process_dialogue(dialogue=session['dialogue'])
    
    # async def direct_process(self, dialogue: Dialogue, intent: str):
    #     await self.server[intent].process_dialogue(dialogue=dialogue)