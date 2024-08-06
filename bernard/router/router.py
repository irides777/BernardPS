
import logging

import dspy
from ..session import Dialogue
from .llm import IntentRouterSig

class DialogueRouter:
    def __init__(self) -> None:
        self.intent_router = dspy.TypedPredictor(IntentRouterSig)
        self.server = {}
    
    def add_server(self, intent, server):
        self.server[intent] = server

    async def route(self, dialogue: Dialogue):
        intent = self.intent_router(dialogue=dialogue).intent
        logging.info(f'Intent: {intent}')
        await self.server[intent].process_dialogue(dialogue=dialogue)
    
    async def direct_process(self, dialogue: Dialogue, intent: str):
        await self.server[intent].process_dialogue(dialogue=dialogue)